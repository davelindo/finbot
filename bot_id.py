# Retrieve Bot ID from token

import os
from slackclient import SlackClient

BOT_NAME = 'finbot'
slack_client = SlackClient('YOUR_TOKEN_HERE')

if __name__ == "__main__":
	api_call = slack_client.api_call("users.list")
	if api_call.get('ok'):
		# retrieve all users
		users = api_call.get('members')
		for user in users:
			if 'name' in user and user.get('name') == BOT_NAME:
				print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
	else:
		print("could not find bot user with the name " + BOT_NAME)
