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
		self.db_path = open('db.pkl', 'rb')
		self.db = pickle.load(self.db_path)
		self.db_path.close()
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
	
	def update_last_update(self, last_update):
		self.db = {"last_update" : last_update}
		self.db_path = open('db.pkl', 'wb')
		pickle.dump(self.db, self.db_path)
		self.db_path.close()
		
	def send_message(self, id, message, endpoint_url):
		requests.get(endpoint_url + 'sendMessage', params=dict(chat_id=id, text=message))
		
	def get_last_update(self):
		self.db_path = open('db.pkl', 'rb')
		return pickle.load(self.db_path)['last_update']
		self.db_path.close()
		
	def run(self):
		print("Started.")
		while True:
			response = requests.get(self.url + 'getUpdates')
			result = json.loads(response.text)
			for update in result['result']:
				if self.get_last_update() < update['update_id']:
					self.update_last_update(update['update_id'])
					print(update)
					if 'message' in update:
						message_text = update['message']['text']
						chat_id = update['message']['chat']['id']
						print(message_text)
						if self.message_for_bot(message_text):
							self.handle_message(chat_id, message_text)
						else:
							print("(This is not for WikiBot...)")
			sleep(2)