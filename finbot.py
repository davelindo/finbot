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


patterns = {
	'tag' : r'^\$',
	'ticker' : r'^[A-Z]*$'
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


		#Check for $ calls -  find tags
		queries = []
		tags = [string.start() for string in re.finditer('\$', message)]

		if tags: 
			num_queries = len(tags)
			if num_queries > 1: 
				for each in tags[:(num_queries-1)]: 
					idx = tags.index(each)
					queries.append(message[each:tags[(idx+1)]])
					# append last item
				queries.append(message[(tags[num_queries-1]):])
			else: 
				queries.append(message)

		for each in queries: 
			print(each)
		# Test again  -- this part is working and is finding every instance of $----- 

		if len(queries) > 4: 
			warning = "Take it easy! I can only handle a few requests at a time."
			slack_client.api_call("chat.postMessage", channel=channel, text=warning, as_user=True)




		if message.startswith('$') or message.startswith(AT_BOT + " $"):
			# body = message.lstrip('$')
			ticker = message[1:]
			message = Source.last_price(ticker)

		elif message.startswith(AT_BOT):
			message = "You talking to me?"

		slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)


	@staticmethod
	def respond(queries):
		pass

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






