import os
import time
import re 
from slackclient import SlackClient
from api import Source

# Bot ID from environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


MESSAGE_PATTERNS = {
	'alpha' : r'^[a-z A-Z]*$'
}



class Finbot: 

	@staticmethod
	def get_output(rtm_output):
		if rtm_output and len(rtm_output) > 0:
			for output in rtm_output:
				# if output and 'text' in output and AT_BOT in output['text']:
				if output and 'text' in output and 'user_profile' not in output:
					# print(output)
					# return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
					# return output['text'], output['channel']
					Finbot.handle_output(output)
		return None

	@staticmethod
	def handle_output(output):
		message, channel = output['text'], output['channel']
		if message.startswith('$'):
			ticker = message[1:]
			message = Source.last_price(ticker)

		response = "I can't respond to that right now but I will have more functionality later."
		slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)









if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
	if slack_client.rtm_connect():
		print("Ready")
		while True:
			Finbot.get_output(slack_client.rtm_read())
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")






