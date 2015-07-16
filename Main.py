from JimmyBot import *
import sys

def main(argv = None):
	bot_token = read_token('token.txt')
	b = JimmyBot(token = bot_token)
	b.run()
	
def read_token(path):
	file = open(path, 'r')
	token = file.readline()
	file.close()
	
	return token
	
if __name__ == "__main__":
	main(sys.argv)