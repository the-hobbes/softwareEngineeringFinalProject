#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Phelan
# 
# This handler executes the actual game environment. 
from handler import *
from random import shuffle
from random import choice
import cgi
import logging
import simplejson as json

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

	def post(self):
		'''
			post
			Responds to post requests for the resource.
			Takes in the json object from the view and, according to the state, executes the necessary data changes.
		'''
		# get the json object passed in by the view (assuming it is called currentState)
		oldState = json.loads(cgi.escape(self.request.body))
		# logging.info(oldState['playCard'])

		# send the object to the state parser, and get the new state of the gameboard
		newState = self.parseState(oldState)

		# render the template with the new state
		newState = json.dumps(newState)
		self.write(newState)
		# http://stackoverflow.com/questions/14520782/decoding-json-with-python-using-appengine
		# the problem was that the json on the client side wasnt actually json
		# push = json.dumps(jdata)
		# self.write(push)

	def initEncode(self):
		'''
			initEncode
			Creates the initial JSON key:value pairs and encodes them to be sent to the game template.
			Returns:
				initialState, the initial state of the gameboard
		'''
		# make a list of lists of cards, flatten it, pick out a discard card that isnt a power card, then shuffle the deck
		# also, dang this is ugly. 
		numberCards = [ [0]* 4, [1]*4, [2]*4, [3]*4, [4]*4, [5]*4, [6]*4, [7]*4, [8]*4, [9]*9 ]
		powerCards = [ [10]*3, [11]*3, [12]*3 ]
		deck = sum(numberCards, [])
		shuffle(deck)
		subDeck = sum(powerCards, [])
		shuffle(subDeck)
		discardCard = str(deck.pop(choice(deck)))
		deck.append(subDeck)

		#intitial JSON array. Note that I've added a playerClicks array to track what the player has selected (eg discard or draw)
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
					"discard" : [discardCard], 
					"deck" : deck,
					"displayCard" : {'image' : "13", 'active' : 0}, 
					"knockState" : 0, 
					"state" : "waitingForDraw",
					"playerClicks" : []
				}
		# encode it
		return json.dumps(newState)

	def parseState(self, oldState):
		'''
			parseState
			Determines the state passed in by the view, then executes the appropriate function to handle that state.
			Parameters:
				oldState, the state passed in by the view
			Returns:
				newstate, the modified state
		'''
		statePassedIn = oldState['state']

		if (statePassedIn == 'waitingForDraw'):
			return self.waitingForDraw(oldState)
		elif (statePassedIn == 'waitingForPCard'):
			pass
		elif (statePassedIn == 'HAL'):
			pass
		elif (statePassedIn == 'playerChoice'):
			pass
		elif (statePassedIn == 'draw2PlayerChoice'):
			pass
		else:
			return statePassedIn

	def waitingForDraw(self, statePassedIn):
		'''
			waitingForDraw
			This function updates the state in accordance to the parameters of the Waiting for Draw state and what the 
			player has clicked. It then returns the new state, to be later encoded as JSON.
			Parameters: 
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the user's choices.
		'''
		# the div id of what the player clicked (either deck, or discardPile)
		userChoice = statePassedIn['playerClicks'][0]

		# if the user has chosen a card from the discard pile, the user must decide what card to swap it out for:
		if (userChoice == 'discardPile'):
			# what was the card they picked? 
			selectedCard = statePassedIn['discard'].pop()
			# set that as the displayCard
			statePassedIn['displayCard'] = {'image' : str(selectedCard), 'active' : 0}
			# clear out the current list of the player's clicks, so that the new state has a fresh empty list to build into
			statePassedIn['playerClicks'] = []
			# set the new state of the game to be "waitingForPCard", as per our documentation (this will glow the players' cards, etc)
			statePassedIn['state'] = 'waitingForPCard'

			return statePassedIn

		# if the user has chosen a card from the deck:
		else:
			# what was the card they picked from the deck? Note that we must also handle the case of the deck being empty 
			try:
				drawnCard = statePassedIn['deck'].pop()
			except:
				# no cards left in the deck. The round ends, so we should probably have a round end state? 
				pass

			# add the card to the display card 
			statePassedIn['displayCard'] =  {'image' : str(drawnCard), 'active' : 0}
			# clear out the current list of the player's clicks, so that the new state has a fresh empty list to build into
			statePassedIn['playerClicks'] = []
			# set the new state of the game to be "playerChoice", as per our documentation
			statePassedIn['state'] = 'playerChoice'

			return statePassedIn

	def waitingForPCard(self, statePassedIn):
		'''
			waitingForPCard
			This state handler is used to update the state in accordance with the results of the player's choice (what the
			user clicked on the gameboard). 
			Parameters:
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the user's choices.
		'''
		pass

	def HAL(self, statePassedIn):
		'''
			HAL
			This state handler is used to manage the play of the AI. The level of bad-assery which HAL possesses is determined
			by the user's choice in the difficulty choice menu page, and as such this level must be retrieved from the 
			datastore.
			Parameters:
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the computer's choices.
		'''
		pass

	def playerChoice(self, statePassedIn):
		'''
			playerChoice
			This state means a player has drawn any card from the deck and must choose to either discard or use it. We get the
			player's decision and modify the state appropriately. 
			Parameters:
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the user's choices.
		'''
		pass

	def draw2PlayerChoice(self, statePassedIn):
		'''
			draw2PlayerChoice
			Due to the nature of the draw 2 power card, the user is able to draw multiple cards and process each of those states 
			while in this state.
			Parameters:
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the user's choices.
		'''
		pass
		

		
