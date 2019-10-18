"""
QL Agent vs other agents Performance in TicTacToe

The Qlearning agent uses the learnt QTable to play against other agents, from random to Logical .
We notice that the QL Agent performs exceptionally against the Logical agent because it learnt by
playing against the Logical Agent. However, the Logical agent outperforms the QL Agent against  a
random agent.
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
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Syed Ali Shahbaz"
__email__ = "contact@alishaz.com"
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
		self.episodes = 0
		print('The Games Begin')
		self.state = ['0','1','2','3','4','5','6','7','8'] 									#initialize current state as empty board
		self.valid = ['0','1','2','3','4','5','6','7','8']									#initialize valid moves as empty slots in the current state
		self.isWinner = None 																	#initialize winner as none
		self.turn = 'X' 																	#initialize the current symbol as X
		self.xwin_count = 0		
		self.ywin_count = 0		
		self.draw_count = 0
		self.player1 = player1 																#player1 type(QAgent,Human,etc.)
		self.player2 = player2 																#player2 type(QAgent,Human,etc.)
		self.current_player = player1	
		self.episodes = episodes																#A list of cumulative reward for plotting
		self.iter = 0
		

	def reset_game(self, player1, player2):
		"""
		Reset the board to initialization game state 
		"""
		self.state = ['0','1','2','3','4','5','6','7','8'] 									#Reset current state as empty board
		self.valid = ['0','1','2','3','4','5','6','7','8']									#Reset valid moves as empty slots in the current state
		self.isWinner = None 																	#Reset winner as none
		self.turn = 'X' 
		self.prevMove = None
		self.prevState = None
		self.player1 = player1
		self.player2 = player2	
		self.current_player = player1
		

	def play_game(self):
		"""
		This is the game loop
		"""
		while self.iter < self.episodes:
			self.play_move()																#play a move using current player
			if self.isWinner is None:
				self.turn = self.switch_player()
				self.current_player = self.player1 if self.turn == 'X' else self.player2
			else:																			#Meaning the game is over
				self.count_winner()
				self.reset_game(self.player1, self.player2)
				self.iter +=1	


	def play_move(self):
		"""
		This function decides the mechanics and logic behind every move based on the Agent/Player type
		"""
		if self.current_player == 'LogicAgent':
			if len(self.valid)>1:
				strike, pos = self.check_strike() 
				if strike is True:
					self.state[int(pos)] = self.turn 
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
			state = self.list_to_string(self.state) 				
		elif self.current_player == 'QLAgent':
			state = self.list_to_string(self.state) 
			action = self.choose_action(state) 
			self.state[int(action)] = self.turn 
			self.valid.remove(action)
			self.isWinner = self.check_winner(self.state)
		elif self.current_player == 'Human':
			pos = input("Enter the position where you want to place " + self.turn) 
			print('You selected : ' + pos)
			self.state[int(pos)] = self.turn
			self.valid.remove(pos)
			self.isWinner = self.check_winner(self.state)
		elif self.current_player == 'Random':
			pos = random.choice(self.valid)
			self.state[int(pos)] = self.turn
			self.valid.remove(pos)			
			state = self.list_to_string(self.state)
			self.isWinner = self.check_winner(self.state)	

	
	def switch_player(self):
		"""
		Switches the current player control and returns the player's symbol
		"""
		self.current_player = self.player2 if self.current_player == self.player1 else self.player1
		return 'X' if self.turn == 'O' else 'O'


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


	def choose_action(self, state):
		"""
		Policy for choosing an action
		"""
		player = self.turn
		listOfQValues = []
		if state in self.qtable.keys():
			for pos, val in self.qtable[state].items():
				if str(pos) in self.valid:
					listOfQValues.append( tuple((pos, val)) ) 
			action = max(listOfQValues,key=operator.itemgetter(1))[0]
		else:
			action = random.choice(self.valid)	
		return str(action) if str(action) in self.valid else random.choice(self.valid)
		

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
		self.kind = 'Random' #random playing bot

	def agent(self):
		"""
		Updates the calling player object to Logical Agent type
		"""
		self.kind = 'LogicAgent' #somewhat intelligent playing agent			

	def qlagent(self):
		"""
		Updates the calling player object to QLearning Agent type
		"""
		self.kind = 'QLAgent'	#Qlearning playing agent			

	def human(self):
		"""
		Updates the calling player object to Human Player type
		"""
		self.kind = 'Human'	#human player			


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
	episodes = 100000

	pickle_in = open("Qlearn_new.pickle","rb")
	qtable = pickle.load(pickle_in)

	game = tictactoe_game(player1,player2,episodes,qtable)
	game.play_game()

	print (player1 + ' as X wins:' + str(game.xwin_count))
	print (player2 + ' as O wins:' + str(game.ywin_count))
	print ('Draws:' + str(game.draw_count))

	fig = plt.figure()
	x = [player1, 'DRAW', player2, 'Total Games']
	a = game.xwin_count
	b = game.draw_count
	c = game.ywin_count
	d = a+b+c
	ax1 = fig.add_subplot(1, 1, 1)

	ax1.clear()
	bar1 = ax1.bar(x, [a, b, c, d])
	bar1[0].set_color('r')
	bar1[1].set_color('b')
	bar1[2].set_color('g')
	ax1.set_ylim((0, d + 100))
	plt.draw()
	plt.show()


if __name__ == "__main__":
    main()

		