#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Phelan
# 
# This handler executes the actual game environment. 
from handler import *
from random import shuffle
import json

class GameHandler(Handler):
	'''
		GameHandler
		Main handler for rendering game elements in the templating system. Responds to get and post requests for the game url. Inherits from Hander for easy
		template rendering.
	'''
	def get(self):
		'''
			get
			You got your basic get method right here, but with a twist. 
			This method perfoms the intialization of the game state, creating the json objects that represent the game and
			json encoding them. It then renders them on the game template with jinja. 
		'''
		#perform initial creation and encoding of JSON object
		newState = self.initEncode()
		self.render("game.html", oldState='null', newState=newState)

		# TODO
		# the json object is showing up weirdly because it is being escaped twice (once by json.dumps and once by autoescape =true)
		# got to find a way around that
		# also, need to massage ethan's script so it can deal with the 'visible' property i've added

	def post(self):
		'''
			post
			Responds to post requests for the resource.
			This is essentially the model. Takes in the json object passed by the view, and modifies the data based on the 
			current state. Then sends back the data, formatted as json.
		'''
		self.write("You posted. Good for you.")

	def initEncode(self):
		'''
			initEncode
			Creates the initial JSON key:value pairs and encodes them to be sent to the game template.
			Returns:
				initialState, the initial state of the gameboard
		'''
		# make a list of lists of cards, flatten it, then shuffle it
		listOfLists = [ [0]* 4, [1]*4, [2]*4, [3]*4, [4]*4, [5]*4, [6]*4, [7]*4, [8]*4, [9]*9, [10]*3, [11]*3, [12]*3 ]
		deck = sum(listOfLists, [])
		shuffle(deck)

		newState = {"compCard" : [
						{"image" : str(deck.pop()), 'active' : 0, 'visible' : 0}, 
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0}, 
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0},
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0}],  
					"playCard" : [
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 1}, 
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0}, 
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0},
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 1}], 
					"discard" : [], 
					"deck" : deck,
					"displayCard" : {'image' : "13", 'active' : 0}, 
					"knockState" : 0, 
					"state" : "waitingForDraw" 
				}
		# encode it
		return json.dumps(newState)
