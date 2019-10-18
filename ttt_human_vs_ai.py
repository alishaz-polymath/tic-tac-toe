"""
Human vs AI TicTacToe using QLearning table

The Qlearning agent uses the learnt QTable to play against human player with a GUI made using the 
Pygame library. There are still instances where it is apparent that the AI can improve  since  it 
hasn't faced many situations while learning. At the moment, the agent doesn't learn while playing 
against the Human user, and it is a feature I intend to add further down the line.
"""
import numpy as np
import copy
import math
import random
import operator
import itertools
import time as time
import pickle
import pygame, sys
from pygame.locals import *


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
	def __init__(self, player1, player2, qtable):
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
		self.game_running = True
		self.player1 = player1 																#player1 type(QAgent,Human,etc.)
		self.player2 = player2 																#player2 type(QAgent,Human,etc.)
		self.current_player = player1	
		self.event = None
		self.thinking = False
		self.board = None

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
		ttt = pygame.display.set_mode((300,400))
		pygame.display.set_caption('Tic-Tac-Toe')
		self.board = self.init_board(ttt)


	def play_game(self):
		"""
		This is the game loop
		"""
		pygame.init()
		ttt = pygame.display.set_mode((300,400))
		pygame.display.set_caption('Tic-Tac-Toe')
		self.board = self.init_board(ttt)
		while self.game_running is True:
			self.event = pygame.event.poll()
			if self.event.type == pygame.QUIT:
				self.game_running = False
				pygame.quit()
				sys.exit()	
				break
			self.show_board(ttt)	
			self.play_move()																#play a move using current player
			if self.isWinner is None:
				self.turn = self.switch_player()
				self.current_player = self.player1 if self.turn == 'X' else self.player2
			else:																			#Meaning the game is over
				self.count_winner()
				self.draw_strike()
				self.show_board(ttt)
				time.sleep(3)
				self.reset_game(self.player1, self.player2)
		print('Goodbye!')				
		pygame.quit()
		sys.exit()			


	def show_board(self, ttt):
		"""
		This displays the Board
		"""
		self.draw_status()
		ttt.blit(self.board, (0, 0))
		pygame.display.flip()


	def draw_status(self):
		"""
		This adds status messages to the Board
		"""
		if (self.isWinner is None):
			message = self.turn + "'s turn"
		elif (self.isWinner == 'Draw'):
			message = "Game Drawn"	
		else:
			message = self.isWinner + " won!"
	        
		winsAI = 'AI : ' + str(self.xwin_count)
		winsH = 'Human : ' +  str(self.ywin_count)  
		draw = 'Draw : ' + str(self.draw_count)

		font = pygame.font.Font(None, 24)
		text = font.render(message, 1, (10, 10, 10))
		scoreAI = font.render(winsAI, 1, (10, 10, 10))
		scoreH = font.render(winsH, 1, (10, 10, 10))
		scoreD = font.render(draw, 1, (10, 10, 10))

		self.board.fill ((250, 250, 250), (0, 300, 300, 25))
		self.board.blit(text, (10, 300))
		self.board.blit(scoreAI, (10, 325))
		self.board.blit(scoreH, (10, 350))
		self.board.blit(scoreD, (10, 375))


	def init_board(self, ttt):
		"""
		This initialises the Board
		"""
		background = pygame.Surface (ttt.get_size())
		background = background.convert()
		background.fill ((250, 250, 250))

		pygame.draw.line (background, (0,0,0), (100, 0), (100, 300), 2)
		pygame.draw.line (background, (0,0,0), (200, 0), (200, 300), 2)

		pygame.draw.line (background, (0,0,0), (0, 100), (300, 100), 2)
		pygame.draw.line (background, (0,0,0), (0, 200), (300, 200), 2)

		return background


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
			self.thinking = True	
		if self.current_player == 'QLAgent':
			time.sleep(1)	
			state = self.list_to_string(self.state) 
			action = self.choose_action(state) 
			self.state[int(action)] = self.turn 
			self.valid.remove(action)
			self.isWinner = self.check_winner(self.state)
			row,col = self.get_row_col(action)
			self.draw_move(action,row,col)
			self.thinking = True
		elif self.current_player == 'Human':
			pygame.event.wait()
			while self.thinking is True:
				for event in pygame.event.get():
					if pygame.event.event_name(event.type) == 'Quit':
						self.game_running = False
						self.thinking = False
						pos = self.valid[0]
						break
					elif event.type == pygame.MOUSEBUTTONDOWN:
						loc = event.pos
						pos = self.get_box(loc)
						legal = False if pos is None else True
						self.thinking = False if legal is True else True
			self.state[int(pos)] = self.turn
			self.valid.remove(pos)
			self.isWinner = self.check_winner(self.state)


	def get_row_col(self, pos):
		"""
		Returns the row,col based on 0-8 pos on the Board
		"""
		if pos == '0':
			row=0
			col=0	    
		elif pos == '1':
			row=0
			col=1	    
		elif pos == '2':
			row=0
			col=2	    
		elif pos == '3':
			row=1
			col=0	    
		elif pos == '4':
			row=1
			col=1	    
		elif pos == '5':
			row=1
			col=2	    
		elif pos == '6':
			row=2
			col=0	    
		elif pos == '7':
			row=2
			col=1
		else:
			row=2
			col=2		    
		return row, col
	
	def switch_player(self):
		"""
		Switches the current player control and returns the player's symbol
		"""
		self.current_player = self.player2 if self.current_player == self.player1 else self.player1
		return 'X' if self.turn == 'O' else 'O'


	def get_box(self, loc):
		"""
		Returns the position on the board where the user clicked
		"""
		(mouseX, mouseY) = loc
		pos, row, col = self.board_pos(mouseX, mouseY)
		if (self.state[int(pos)] == "X") or (self.state[int(pos)] == "O"):
			return None
		self.draw_move(pos,row,col)
		return pos


	def draw_move(self, pos, boardRow, boardCol):
		"""
		Places X or O on the board, depending on the turn
		"""
		centerX = ((boardCol) * 100) + 50
		centerY = ((boardRow) * 100) + 50
		if (self.turn == 'O'):
			pygame.draw.circle (self.board, (0,0,0), (centerX, centerY), 44, 2)
		else:
			pygame.draw.line (self.board, (0,0,0), (centerX - 22, centerY - 22), \
	                         (centerX + 22, centerY + 22), 2)
			pygame.draw.line (self.board, (0,0,0), (centerX + 22, centerY - 22), \
	                         (centerX - 22, centerY + 22), 2)
		self.state[int(pos)] = self.turn


	def board_pos(self, mouseX, mouseY):
		"""
		Returns board position, row and column of the clicked location
		"""
		if (mouseY < 100):
			row = 0
		elif (mouseY < 200):
			row = 1
		else:
			row = 2

		if (mouseX < 100):
			col = 0
		elif (mouseX < 200):
			col = 1
		else:
			col = 2

		if (row==0) and (col==0):
			pos = '0'	    
		elif (row==0) and (col==1):
			pos = '1'	    
		elif (row==0) and (col==2):
			pos = '2'	    
		elif (row==1) and (col==0):
			pos = '3'	    
		elif (row==1) and (col==1):
			pos = '4'	    
		elif (row==1) and (col==2):
			pos = '5'	    
		elif (row==2) and (col==0):
			pos = '6'	    
		elif (row==2) and (col==1):
			pos = '7'	    
		else:
			pos = '8'    

		return pos, row, col


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
			print('New State: Choosing action randomly')
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


	def draw_strike(self):
		"""
		Draws the line where the strike is
		"""
		if (self.state[0] == self.state[1] == self.state[2] and \
           	(self.state[0] is not None)):
			pygame.draw.line (self.board, (250,0,0), (0, 50), \
                              (300, 50), 2)
		elif (self.state[3] == self.state[4] == self.state[5] and \
           	(self.state[3] is not None)):
			pygame.draw.line (self.board, (250,0,0), (0, 150), \
                              (300, 150), 2)
		elif (self.state[6] == self.state[7] == self.state[8] and \
           	(self.state[6] is not None)):
			pygame.draw.line (self.board, (250,0,0), (0, 250), \
                              (300, 250), 2)    		
		elif (self.state[0] == self.state[3] == self.state[6] and \
           	(self.state[0] is not None)):
			pygame.draw.line (self.board, (250,0,0), (50, 0), \
                              (50, 300), 2)
		elif (self.state[1] == self.state[4] == self.state[7] and \
           	(self.state[1] is not None)):
			pygame.draw.line (self.board, (250,0,0), (150, 0), \
                              (150, 300), 2)
		elif (self.state[2] == self.state[5] == self.state[8] and \
           	(self.state[2] is not None)):
			pygame.draw.line (self.board, (250,0,0), (250, 0), \
                              (250, 300), 2)
		elif (self.state[0] == self.state[4] == self.state[8] and \
           	(self.state[0] is not None)):
			pygame.draw.line (self.board, (250,0,0), (50, 50), \
                              (250, 250), 2)
		elif (self.state[2] == self.state[4] == self.state[6] and \
           	(self.state[2] is not None)):
			pygame.draw.line (self.board, (250,0,0), (250, 50), \
                              (50, 250), 2)

class Player():
	"""
	Defines the Player Type Class
	"""
	def __init__(self):
		"""
		Constructor for the player type with default as Random
		"""
		self.kind = 'Random' 						#random playing bot

	def agent(self):
		"""
		Updates the calling player object to Logical Agent type
		"""
		self.kind = 'LogicAgent' 					#Pseudo-logial intelligent agent	

	def qlagent(self):
		"""
		Updates the calling player object to QLearning Agent type
		"""
		self.kind = 'QLAgent'						#Qlearning agent

	def human(self):
		"""
		Updates the calling player object to Human Player type
		"""
		self.kind = 'Human'							#human player			




def main():
	"""
	Main Function of the program where we construct objects of tictactoe_game class and player class. We also plot the result in this function.
	"""
	player1 = Player()
	player2 = Player()
	player3 = Player()
	player1.qlagent()
	player2.human()
	player1 = player1.kind
	player2 = player2.kind
	pickle_in = open("Qlearn_new.pickle","rb")
	qtable = pickle.load(pickle_in)


	game = tictactoe_game(player1,player2,qtable)
	game.play_game()

	print (player1 + ' as X wins:' + str(game.xwin_count))
	print (player2 + ' as O wins:' + str(game.ywin_count))
	print ('Draws:' + str(game.draw_count))


if __name__ == "__main__":
	main()

		