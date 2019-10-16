"""
Plays TicTacToe against a pseudo logical(simpleton) AI and prepares a Q-Table for future reference 

The Qlearning agent play a number of episodes of the famous boardgame- Tic Tac Toe against a psuedo 
logical AI and learn from experience to play and eventually beat  the  pseudo  logical  AI. In this 
program, we simply train the agent by playing it against the pseudo logical AI for a  given  number 
of episodes. We store it using the pickle library and we  can  also load  an  existing  Q-table  to 
update it further.

Note that the human player playing logic is not yet defined in the program, and I hope to update it
at a later stage such that we can then make the agent learn by playing against  a human  player  as 
well.
"""
import numpy as np
import copy
import math
import random
import operator
import itertools
import time as time
from matplotlib import pyplot as plt
import pickle


__author__ = "Syed Ali Shahbaz"
__copyright__ = "Copyright 2019, TicTacToe with AI"
__credits__ = ["Abhijit Nair"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Syed Ali Shahbaz"
__email__ = "alishahbaz7@gmail.com"
__status__ = "Production"


class tictactoe_game():
	"""
	Defines the TicTacToe Game sequence class
	"""
	def __init__(self, player1, player2, episodes, qtable):
		"""
		Constructor for tic-tac-toe game initialization
		"""
		self.learning = True
		self.qtable = qtable	
		self.exploration = 0.2
		self.episodes = 0
		print('The Learning Begins')
		self.state = ['0','1','2','3','4','5','6','7','8'] 									#initialize current state as empty board
		self.valid = ['0','1','2','3','4','5','6','7','8']									#initialize valid moves as empty slots in the current state
		self.isWinner = None 																#initialize winner as none
		self.turn = 'X' 																	#initialize the current symbol as X
		self.xwin_count = 0		
		self.ywin_count = 0		
		self.draw_count = 0
		self.prevMove = None 																#Remember previous move for learning
		self.prevState = None 																#Remember previous State for learning
		self.player1 = player1 																#player1 type(QAgent,Human,etc.)
		self.player2 = player2 																#player2 type(QAgent,Human,etc.)
		self.current_player = player1														#the current player type
		self.rewardSum = 0																	#total reward sum over the current episode
		self.rewardCnt = 0																	#total reward adding to existing rewards in previous episodes
		self.cumureward = []																#A list of cumulative reward for plotting
		self.episodes = episodes															
		self.iter = 0
		self.cumuWins = []																	#A list of cumulative wins for plotting


	def reset_game(self, player1, player2):
		"""
		Reset the board to initialization game state 
		"""
		self.state = ['0','1','2','3','4','5','6','7','8'] 									#Reset current state as empty board
		self.valid = ['0','1','2','3','4','5','6','7','8']									#Reset valid moves as empty slots in the current state
		self.isWinner = None 																#Reset winner as none
		self.turn = 'X' 																	#Reset the current symbol as X
		self.prevMove = None
		self.prevState = None
		self.player1 = player1
		self.player2 = player2	
		self.current_player = player1
		self.rewardCnt += self.rewardSum													#update total reward count
		self.cumureward.append(self.rewardCnt)												#Update cumureward list
		self.rewardSum = 0																	#Reset reward Sum for new episode


	def play_game(self):
		"""
		This is the game loop for every single episode
		"""
		while self.iter < self.episodes:
			#self.draw_board()																#Uncomment this line if you wish to visualize the text-based play on the console
			self.play_move()																#play a move using current player
			if self.isWinner is None:
				reward = self.get_reward()													#get reward for self.prevState and self.prevMove
				self.update_qtable(reward)													#update qtable for self.prevState and prev reward
				self.rewardSum += reward	
				self.turn = self.switch_player()
				self.current_player = self.player1 if self.turn == 'X' else self.player2
			else:																			#Meaning the game is over
				reward = self.get_reward()													#get reward for self.prevState and self.prevMove
				self.update_qtable(reward)													#update qtable for self.prevState and prev reward
				self.rewardSum += reward													
				self.count_winner()
				self.cumuWins.append(self.xwin_count)
				self.reset_game(self.player1, self.player2)
				self.iter +=1	


	def play_move(self):
		"""
		This function decides the mechanics and logic behind every move based on the Agent/Player type
		"""
		if self.current_player == 'LogicAgent':
			if len(self.valid)>1:
				strike, pos = self.check_strike() 											#if there is a strike, and what position on board to place the symbol
				if strike is True:
					self.state[int(pos)] = self.turn 										#using board position as index, since board position is same as item value in our case
					self.valid.remove(pos)
					self.isWinner = self.check_winner(self.state)
				else:	
					pos = random.choice(self.valid)
					self.state[int(pos)] = self.turn
					self.valid.remove(pos)										
			elif len(self.valid) == 1:
				pos = self.valid[0]
				self.state[int(pos)] = self.turn
				self.valid.remove(pos)
				self.isWinner = self.check_winner(self.state)
			state = self.list_to_string(self.state)											#convert list to string for qtable dictionary manipulation
			if state not in self.qtable.keys():
				self.add_key(state) 															#add the current state as a string in the qtable as new key					
		elif self.current_player == 'QLAgent':
			state = self.list_to_string(self.state) 											#convert list to string for qtable dictionary manipulation
			if state not in self.qtable.keys():
				self.add_key(state) 															#add the current state as a string in the qtable as new key
			action = self.choose_action(state) 												#choose an action based on the specific policy design
			self.prevMove = int(action)
			self.prevState = self.state[:]
			self.state[int(action)] = self.turn 											#place the symbol on current action position
			self.valid.remove(action)
			nextState = self.list_to_string(self.state)
			if nextState not in self.qtable.keys():
				self.add_key(nextState)
			self.isWinner = self.check_winner(self.state)	
		elif self.current_player == 'Random':
			pos = random.choice(self.valid)
			self.state[int(pos)] = self.turn
			self.valid.remove(pos)			
			state = self.list_to_string(self.state)
			if state not in self.qtable.keys():
				self.add_key(state) 															#add the current state as a string in the qtable as new key
			self.isWinner = self.check_winner(self.state)

	
	def switch_player(self):
		"""
		Switches the current player control and returns the player's symbol
		"""
		self.current_player = self.player2 if self.current_player == self.player1 else self.player1
		return 'X' if self.turn == 'O' else 'O'


	def get_reward(self):
		"""
		Returns reward based on the policy
		"""
		if self.isWinner == 'X':
			return 1
		elif self.isWinner == 'O':
			return -1
		else:
			return 0


	def list_to_string(self, list):
		"""
		Returns string converted from the provided list
		"""
		str = "" 
		for x in list: 
			str += x
		return str


	def check_strike(self):
		"""
		Returns the next state's possibility of game winning move for either players along with the position
		"""
		gameState = self.state[:]
		for pos in self.valid:
			gameState[int(pos)] = self.turn
			if self.check_winner(gameState) == self.turn:
				return True, pos
			gameState = self.state[:]	
			opponent = 'O' if self.turn == 'X' else 'X'		
			gameState[int(pos)] = opponent
			if self.check_winner(gameState) == opponent:
				return True, pos		
			gameState = self.state[:]		
		return False, '0'	


	def check_winner(self, state):
		"""
		Returns the result of the game or None, if there's free space on the board to play and neither of the players won
		"""
		state = self.list_to_string(state)
		winner = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
		for line in winner:
			strike = state[line[0]] + state[line[1]] + state[line[2]]
			if strike == 'XXX':
				return 'X'
			elif strike == 'OOO':
				return 'O'	
			elif len(self.valid)<1:
				return 'Draw'
		return None		


	def add_key(self, state):
		"""
		Adds the key to the qtable
		"""
		self.qtable.update({state:{0:0.0, 1:0.0, 2:0.0, 3:0.0, 4:0.0, 5:0.0, 6:0.0, 7:0.0, 8:0.0}})


	def choose_action(self, state):
		"""
		Policy for choosing an action
		"""
		player = self.turn
		if self.iter == 100000:
			self.exploration = 1.01
		num = random.uniform(0,1)
		if num < self.exploration:
			listOfQValues = []
			for pos, val in self.qtable[state].items():
				if str(pos) in self.valid:
					listOfQValues.append( tuple((pos, val)) ) 
			action = max(listOfQValues,key=operator.itemgetter(1))[0]
			return str(action) if str(action) in self.valid else random.choice(self.valid)
		else:
			action = random.choice(self.valid)
			return action	


	def update_qtable(self,reward):
		"""
		Qtable update policy
		"""
		discount = 0.01	
		learningRate = 0.5 
		state = self.list_to_string(self.state)
		prevState = self.list_to_string(self.prevState)

		if self.isWinner is not None:
			expected = reward	
		else:
			expected = reward + (discount * max(self.qtable[state].items(), key=operator.itemgetter(1))[0])
		try:	
			change = learningRate * (expected - self.qtable[prevState][self.prevMove])
		except:
			print('error in : ' + prevState)	
			print('action : ' + str(self.prevMove))
			print('Turn : ' + self.turn)	
			print(self.qtable)
		self.qtable[prevState][self.prevMove] += change	


	def count_winner(self):
		"""
		Updates the win/draw count
		"""
		if self.isWinner == 'X':
			self.xwin_count+=1
		elif self.isWinner == 'O':
			self.ywin_count+=1
		else:
			self.draw_count+=1	


	def draw_board(self):
		"""
		Provides a text-based visualization of the game
		"""
		print(self.current_player + '\'s turn playing : ' + self.turn )
		time.sleep(2)
		state = self.list_to_string(self.state)
		print('_______')
		print('|'+state[0]+'|'+state[1]+'|'+state[2]+'|')
		print('|'+state[3]+'|'+state[4]+'|'+state[5]+'|')
		print('|'+state[6]+'|'+state[7]+'|'+state[8]+'|')
		print('_______')
		nextKey = self.state		


class Player():
	"""
	Defines the Player Type Class
	"""
	def __init__(self):
		"""
		Constructor for the player type with default as Random
		"""
		self.kind = 'Random' 														#random playing bot

	def agent(self):
		"""
		Updates the calling player object to Logical Agent type
		"""
		self.kind = 'LogicAgent' 													#Pseudo-logial intelligent agent			

	def qlagent(self):
		"""
		Updates the calling player object to QLearning Agent type
		"""
		self.kind = 'QLAgent'														#Qlearning agent			

	def human(self):
		"""
		Updates the calling player object to Human Player type
		"""
		self.kind = 'human'															#human player			


def main():
	"""
	Main Function of the program where we construct objects of tictactoe_game class and player class. We also plot the result in this function.
	"""
	player1 = Player()
	player2 = Player()
	player1.qlagent()
	player2.agent()
	player1 = player1.kind
	player2 = player2.kind
	episodes = 200000
	qtable = {'012345678': {0:0.0, 1:0.0, 2:0.0, 3:0.0, 4:0.0, 5:0.0, 6:0.0, 7:0.0, 8:0.0}}
	#########################################################################################################
	####NOTE : if you want to update an existing qtable, please uncomment the following two lines of code:###
	####pickle_in = open("Qlearn_new.pickle","rb")###########################################################
	####qtable = pickle.load(pickle_in)######################################################################
	#########################################################################################################
	game = tictactoe_game(player1,player2,episodes,qtable)
	game.play_game()
	print (player1 + ' as X wins:' + str(game.xwin_count))
	print (player2 + ' as O wins:' + str(game.ywin_count))
	print ('Draws:' + str(game.draw_count))
	print ('Qtable entries : ' + str( len(game.qtable) ) )
	x=range(0,200000)
	plt.plot(x, game.cumuWins)
	plt.xlabel('Episodes')
	plt.ylabel('Number of Wins')		
	plt.show()

	pickle_out = open("Qlearn_new.pickle","wb")
	pickle.dump(game.qtable, pickle_out)
	pickle_out.close


def print_qtable(qtable, indent=0):
	"""
	Print Qtable with state(Key) and values. Useful in debugging.
	"""
	for key, value in qtable.items():
		print(key)
		print(value)

if __name__ == "__main__":
	main()

		