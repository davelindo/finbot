from slackclient import SlackClient
import os
import time
import re 
import random
from api import Source

# Bot ID from environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
AT_BOT_2 = "<@" + BOT_ID + ">:"
FINBOT_ON = True

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


patterns = {
	'ticker' : re.compile(r'^[A-Z]*$')
}

COMMANDS = ['tvol', 'dvol', 'PE', 'vol', 'range', 'high', 'low', 'open', 'close', 'name', 'exchange', '-g']
FLAGS = {
	'dvol': [re.compile(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'), 
			re.compile(r'^\d{4}\/(0?[1-9]|1[012])\/(0?[1-9]|[12][0-9]|3[01])$')], 
	'-g': ['1d', '5d', '1M', '3M', '6M', 'YTD', '1Y', '2Y', '5Y'], 

}

ON_MESSAGES = [
"Ready!",
"Finbot is now ON.",
"How can I help?",
]

# Regex for Tvol: "tvol XXXX" with # of days (>7)



class Finbot: 

	@staticmethod
	def get_output(rtm_output):
		"""
		Determines whether Finbot needs to process the output.
		"""
		if rtm_output and len(rtm_output) > 0:
			for output in rtm_output:
				if output and 'text' in output and 'user_profile' not in output:
					Finbot.handle_output(output)
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
	def handle_output(output):
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
		else: 
			return None

		if len(queries) > 5: 
			warning = "Take it easy! I can only handle a few requests at a time."
			slack_client.api_call("chat.postMessage", channel=channel, text=warning, as_user=True)
			queries = queries[0:5]

		for each in queries: 
			Finbot.respond(each, channel)

	@staticmethod
	def respond(query, channel):
		components = query.split(' ')
		if '' in components: 
			components.remove('')
		print(components)
		ticker = components[0]
		if len(components)>1:
			command = list(set(COMMANDS).intersection(components[1:]))
			if not command: 
				message = "I couldn't understand your request for ticker '{}'.".format(ticker)
				return slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
			command = command[0]

			flag = None
			command_flags = FLAGS.get(command)
			if command_flags: 
				flag = list(set(command_flags).intersection(components[1:]))
			if flag: 
				flag = flag[0]


			print("COMMAND", command)
			print("FLAG", flag)
			# edit "command=" line and add [0] at the end - only take one operation per query
			# for each operation, match the other elements of 'components' to the FLAGS variable to get
			# specifics for the operation to be performed 
			message = Source.last_price(ticker)
			slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)
		else: 
			# ticker = components[0]
			message = Source.last_price(ticker)
			slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

		"""
		Move all responding functionality from handle_output to here. 
		Get_output will decide if activity in the channel needs to be handled by Finbot. If yes, it proceeds to handle_output. 
		Handle_output will sort all the text and send all relevant information to the respond method. 

		This will include an array of queries (things tagged with $). It will also be able to respond in some basic ways if the 
		user @s Finbot without using any tags - providing basic guidance and shooting the shit. 

		the handle_output method will also need to retrieve and pass along any relevant user info - the user's username, real name, ID, 
		etc - for addressing the person with its response as well as being able to tag the user that called the bot. 

		++ Add a set of commands for Bot Settings. These should begin by tagging finbot. 
		@finbot tag on - Default. Finbot will tag the user that called it when it replies. if a user sends this message, 
		Finbot will respond saying "Tagging ON" or "Tagging OFF" if someone enters '@finbot tag off'.



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






