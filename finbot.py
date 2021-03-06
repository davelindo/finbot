from slackclient import SlackClient
import os
import time
import re 
import random
from api import OPERATIONS
from response import Response

# Bot ID from environment variable
BOT_ID = "finbot"

# constants
AT_BOT = "<@" + BOT_ID + ">"
AT_BOT_2 = "<@" + BOT_ID + ">:"
FINBOT_ON = True

# instantiate Slack client
slack_client = SlackClient('YOUR_TOKEN_HERE')

COMMANDS = ['hist', '?', 'actions', '-g', 'tvol', 'rvol', 'PE', 'rate', 'fred']


# Add ETF Holdings

class Finbot: 

	@staticmethod
	def get_output(rtm_output):
		"""
		Determines whether Finbot needs to handle the output.
		"""
		if rtm_output and len(rtm_output) > 0:
			for output in rtm_output:
				if output and 'text' in output and 'user_profile' not in output:
					Finbot.filter_output(output)
		return None

	@staticmethod
	def bot_status(raw_text, channel): 
		"""
		Returns True when Bot shouldn't perform any further handling of the output, 
		either because the bot is turned off or because the output was the user turning the bot on/off.
		"""
		global FINBOT_ON

		if raw_text.lower() == "finbot on": 
			FINBOT_ON = True
			message = random.choice(Response.ON_MESSAGES)
			slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
			return True

		elif FINBOT_ON == False: 
			return True

		elif raw_text.lower() == "finbot off":
			FINBOT_ON = False
			message = random.choice(Response.OFF_MESSAGES)
			slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
			return True
		else: 
			return False


	@staticmethod
	def filter_output(output):
		"""
		Parses a user message for processable queries (up to 5 per message). 
		Finbot uses the '$' sign to tag symbols for processing. 
		"""
		raw_text, channel = output['text'], output['channel']
		if Finbot.bot_status(raw_text, channel): 
			return None

		queries = []
		if raw_text.startswith('$'):
			queries = raw_text.split('$')
			queries.remove('')
			if not queries[0].split(' ')[0].isalpha():
				return None
			for each in queries:
				each.strip()
				each.lstrip('$')
		elif raw_text.startswith(AT_BOT) or raw_text.startswith(AT_BOT_2):
			Finbot.bot_info(raw_text.split()[1:], channel)
			return None
		elif '$' in raw_text:
			queries = re.findall(r"\$(\w+)", raw_text)
		else: 
			return None
		if len(queries) > 5: 
			warning = random.choice(Response.TOO_MANY_REQUESTS)
			slack_client.api_call("chat.postMessage", channel=channel, text=warning, as_user=True)
			queries = queries[0:5]

		for each in queries: 
			Finbot.process_request(each, channel)


	@staticmethod
	def bot_info(query, channel):
		"""
		Sends a message with information about how to use a command if the user tags the bot.
		"""
		message = ''
		if 'info' in query: 
			command = list(set(COMMANDS).intersection(query))
			if not command: 
				message = Response.BOT_INFO
			else: 
				command = command[0]
				message = Response.info[command]
		else: 
			message = Response.BOT_INFO
		return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)


	@staticmethod
	def process_request(query, channel):
		"""
		Each user query is forwarded to the appropriate function based on the command in the query.
		Once the query has been processed, the resulting response is sent as a message to the channel. 
		If no commands are found, the default is to fetch the last price for the ticker.
		"""
		# components - each query split into a list of words and symbols
		components = query.split(' ')
		if '' in components: 
			components.remove('')
		ticker = components[0]
		if len(components)>1:
			command = list(set(COMMANDS).intersection(components[1:]))
			if not command: 
				message = Response.unknown_command(ticker)
				return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
			components = components[2:]
			output = OPERATIONS[command[0]](ticker, components)
			message = output["message"]
			if output.get("attachments"):
				attachments = output['attachments']
				return slack_client.api_call("chat.postMessage", channel=channel, text=message, attachments=attachments, as_user=True)
			return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
		message = OPERATIONS["last_price"](ticker)
		return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)



if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("Ready")
		while True:
			Finbot.get_output(slack_client.rtm_read())
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")






