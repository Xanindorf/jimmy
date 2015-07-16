import requests
import json
import wikipedia
import pickle
from time import sleep
from wikipedia import DisambiguationError
from wikipedia import PageError

class JimmyBot:
	def __init__(self, token):
		print("Starting...")
		self.token = token
		self.message_offset = 0
		self.url = 'https://api.telegram.org/bot%s/' % token

	def message_for_bot(self, message):
		message = message.lower()
		print("Is this a message for the bot?: " + message)
		if message.startswith('wiki') or message.startswith('/wiki'):
			print("Yes")
			return True
		print("No")
		return False
		
	def handle_message(self, id, message):
		print("Handle message: " + message)
		query = message.partition(' ')[2] 	# Get the stuff after the space
		
		try:
			wiki_response = wikipedia.summary(query, sentences = 3)
		except PageError:
			wiki_response = "Sorry! Couldn't find any page matching \"" + query + "\" - please try another search term."
		except DisambiguationError as e:
			wiki_response = self.handle_disambiguation(e)
		
		self.send_message(id, wiki_response, self.url)
		
	def handle_disambiguation(self, e):
		suggestions = e.options[0:3]
		response = "Sorry! This search term leads me to a disambiguation page - please try a more precise search term.\nExamples:\n"
		for suggestion in suggestions:
			response += '- ' + suggestion + '\n'
		
		return response
	
	def send_message(self, id, message, endpoint_url):
		requests.get(endpoint_url + 'sendMessage', params=dict(chat_id=id, text=message))
	
	def run(self):
		print("Started.")
		while True:
			response = requests.get(self.url + 'getUpdates', params=dict(offset=self.message_offset))
			result = json.loads(response.text)
			for update in result['result']:
				self.message_offset = update['update_id'] + 1
				print(update)
				if 'message' in update:
					message = update['message']
					if 'title' in message['chat']:
						continue
					if 'text' in message:
						message_text = message['text']
						chat_id = update['message']['chat']['id']
						if self.message_for_bot(message_text):
							self.handle_message(chat_id, message_text)
						else:
							print("(This is not for WikiBot...)")
			sleep(2)