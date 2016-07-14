from slackclient import SlackClient
import os
import time
import re 
import random
from api import OPERATIONS
from response import Response

# Bot ID from environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
AT_BOT_2 = "<@" + BOT_ID + ">:"
FINBOT_ON = True

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))





# COMMANDS = ['tvol', 'dvol', 'PE', 'vol', 'range', 'high', 'low', 'open', 'close', 'name', 'exchange', '-g']
COMMANDS = ['-g', 'tvol', 'rvol']




PATTERNS = {

	'dvol': {
		"type": "REGEX",
		"patterns": [re.compile(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'), 
					re.compile(r'^\d{4}\/(0?[1-9]|1[012])\/(0?[1-9]|[12][0-9]|3[01])$')]
			}, 
	'tvol': {
		"type": "REGEX",
		"patterns": []
	},
	'-g': {
		"type": "FLAG",
		"patterns": ['1d', '5d', '1M', '3M', '6M', 'YTD', '1Y', '2Y', '5Y']
	},

}

ON_MESSAGES = [
"Ready!",
"Finbot is now ON.",
"How can I help?",
]



class Finbot: 

	@staticmethod
	def get_output(rtm_output):
		"""
		Determines whether Finbot needs to process the output.
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
		either because the bot is turned off or because the user was turning the bot on/off.
		"""
		global FINBOT_ON

		if raw_text.lower() == "finbot on": 
			FINBOT_ON = True
			message = random.choice(ON_MESSAGES)
			slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
			return True

		elif FINBOT_ON == False: 
			return True

		elif raw_text.lower() == "finbot off":
			FINBOT_ON = False
			message = "Going to sleep..."
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
			for each in queries: 
				each.strip()
				each.lstrip('$')
		elif raw_text.startswith(AT_BOT) or raw_text.startswith(AT_BOT_2):
			Finbot.bot_info(raw_text.split()[1:], channel)
			return None
		else: 
			return None

		if len(queries) > 5: 
			warning = "Take it easy! I can only handle a few requests at a time."
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
				message = "Use `<operation name> info` to get information about how to format a query."
			else: 
				command = command[0]
				message = Response.info[command]
		else: 
			message = "Use `<operation name> info` to get information about how to format a query."
		return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)


	@staticmethod
	def process_request(query, channel):
		"""
		Each user query is forwarded to the appropriate function based on the command in the query.
		Once the query has been processed, the resulting response is sent as a message to the channel. 
		If no commands are found, the default is to fetch the last price for the ticker.
		"""
		components = query.split(' ')
		if '' in components: 
			components.remove('')
		ticker = components[0]
		if len(components)>1:
			command = list(set(COMMANDS).intersection(components[1:]))
			if not command: 
				message = "I couldn't understand your request for ticker '{}'.".format(ticker)
				return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
			components = components[2:]
			output = OPERATIONS[command[0]](ticker, components)
			message = output["message"]
			attachments = output["attachments"]

			
			return slack_client.api_call("chat.postMessage", channel=channel, text=message, attachments=attachments, as_user=True)
			# return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
		message = OPERATIONS["last_price"](ticker)
		return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)





		"""
		To do 

		built-in documentation: 
		if message starts with @finbot, look for "<command> info" and get the response from Response.info[command] static class variable
		Where to implement? How to avoid entanglement and preserve single responsibility? 

		Move general finbot responses on startup, etc to response.py. Add more random responses. 

		Implement -g function that fetches graph. Flags for durations (1d, 5d, 3M, etc)

		--> finish graphing function - error handling? (get price for ticker first?)
		--> create copy of -g function that uses urlretrieve - save image locally with UUID as name, upload, then delete locally 

		- Historical pricing (yahoo finance API or pandas datareader)
		- open, close, high, low, range over any given period of time, high/low over any given period of time

		- Fundamentals, ratios, etc
		- ETF Holdings







		"""










if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("Ready")
		while True:
			Finbot.get_output(slack_client.rtm_read())
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")






