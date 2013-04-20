#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Phelan
# 	Ethan
# This handler executes the actual game environment. The initial gameboard is setup and displayed as a response to an http GET
#	request. The GameHandler class fills the role of a 'Controller' in the MVC paradigm. It manages game logic and responds to
#	POST requests from the View (a collection of Javascript and HTML code). In addition to having a method to handle each state,
#	the GameHander class also possesses several utility functions (including setup, swapping translation, etc...). 

from handler import *
from random import shuffle
from random import choice
from python import HAL
import cgi
import logging
import json
from python.gameModel import DatastoreInteraction
import time

class GameHandler(Handler):
	'''
		GameHandler
		Main handler for rendering game elements in the templating system. Responds to get and post requests for the game url. Inherits from Hander for easy
		template rendering.
	'''
	# class variables 
	sessionId = ""
	ENDGAME_SCORE = 60
	thumbnailImage = ""

	def get(self):
		'''
			get
			You got your basic get method right here, but with a twist. 
			This method perfoms the intialization of the game state, creating the json objects that represent the game and
			json encoding them. It then renders them on the game template with jinja. 
		'''

		# get the player avatar image from the datastore 
		self.sessionId = self.request.get("sessionId")
		# use the gameModel to interact with the datastore
		newModel = DatastoreInteraction(self.sessionId)
		avatar = newModel.getAvatar()

		# set the right picture
		if(avatar == "character1"):
			self.thumbnailImage = "bettyThumb.png"
		elif(avatar == "character2"):
			self.thumbnailImage = "jasonThumb.png"
		elif(avatar == "character3"):
			self.thumbnailImage = "batRatThumb.png"
		elif(avatar == "character4"):
			self.thumbnailImage = "catLadyThumb.png"
		elif(avatar == "character5"):
			self.thumbnailImage = "lebowsCatThumb.png"
		else:
			self.thumbnailImage = "tommyCatThumb.png"

		# perform initial creation and encoding of JSON object
		newState = self.initEncode()

		# update the opcards and aicards in the hal object in the datastore
		halState = json.loads(newState)
		newModel = DatastoreInteraction(self.sessionId)
		logging.info(newModel)
		newModel.updateAiCards(str(halState['playCard']), aiCards=str(halState['compCard']))

		self.render("game.html", oldState='null', newState=newState, thumbnailImage=self.thumbnailImage)

	def post(self):
		'''
			post
			Responds to post requests for the resource.
			Takes in the json object from the view and, according to the state, executes the necessary data changes.
			
			**** TODO: when an oldState comes in we need to check to see if there are cards left in the deck. if there aren't,
			we need to direct program flow to endgame. If there are, then we can proceed as normal, according to the information
			included in the oldState.
		'''
		# logging.info(self.request.arguments())

		# get the json object passed in by the view (assuming it is called currentState)
		oldState = json.loads(cgi.escape(self.request.body))

		# reset all of the active flags in the json (to remove all glowing effects and prepare for new ones)
		oldState = self.resetActiveFlags(oldState)

		# if the deck is empty, its time for the endgame state
		if( len(oldState['deck']) == 0 ):
			logging.info("Deck is empty")
			newState = self.endGame(oldState)
		# otherwise, proceed as normal
		else:
			# send the object to the state parser, and get the new state of the gameboard
			newState = self.parseState(oldState)
		
		#write the new data out as a response for the view to render
		newState = json.dumps(newState)

		self.write(newState)


	def initEncode(self):
		'''
			initEncode
			Creates the initial JSON key:value pairs and encodes them to be sent to the game template.
			Returns:
				initialState, the initial state of the gameboard
		'''
		# logging.info("This is the session id: "  + sessionId)
		# make a list of lists of cards, flatten it, pick out a discard card that isnt a power card, then shuffle the deck
		# numberCards = [ [0]* 4, [1]*4, [2]*4, [3]*4, [4]*4, [5]*4, [6]*4, [7]*4, [8]*4, [9]*9 ]
		# powerCards = [ [10]*3, [11]*3, [12]*3 ]
		# deck = sum(numberCards, [])
		# shuffle(deck)
		# subDeck = sum(powerCards, [])
		# shuffle(subDeck)
		# discardCard = deck.pop(choice(deck))
		# for p in subDeck:
		# 	deck.append(p)
		# shuffle(deck)

		deck = [12,12,12,12,12,12,12,12,12,12,12,12]
		discardCard = 11		

		#intitial JSON array. Note that I've added a playerClicks array to track what the player has selected (eg discard or draw)
		newState = {"compCard" : [
						{"image" : str(deck.pop()), "active" : 0, "visible" : 0}, 
						{"image" : str(deck.pop()), "active" : 0, "visible" : 0}, 
						{"image" : str(deck.pop()), "active" : 0, "visible" : 0},
						{"image" : str(deck.pop()), "active" : 0, "visible" : 0}],  
					"playCard" : [
						{"image" : str(deck.pop()), "active" : 0, "visible" : 0}, 
						{"image" : str(deck.pop()), "active" : 0, "visible" : 0}, 
						{"image" : str(deck.pop()), "active" : 0, "visible" : 0},
						{"image" : str(deck.pop()), "active" : 0, "visible" : 0}], 
					"discard" : [discardCard],
					"discardActivity" : 1,
					"deck" : deck,
					"deckActivity" : 1,
					"displayCard" : {'image' : "13", 'active' : 0}, 
					"knockState" : 0, 
					"state" : "waitingForDraw",
					"score" : 0,
					"gameOver" :0,
					"win": 0,
					"sessionId" : self.sessionId,
					"playerClicks" : [],
					"draw2Counter" : 0,
					"message": {"visible" : 0, "text" : "There is no card to be selected here"}
				}

		# encode it
		# logging.info(newState)
		#TODO
		#
		# WE NEED TO CREATE THE AI OBJECT HERE. DO THIS TOMORROW WITH PHELAN
		#
		disc = newState['discard'][0]
		ai = HAL.HAL(pkSessionID=self.sessionId, estAIScore=36,estOppScore=0,opCardsMem=[0.0,0.0,0.0,0.0],aiCardsMem=[1.0,0.0,0.0,1.0],opCards=json.dumps(newState['playCard']),aiCards=json.dumps(newState['compCard']),discardTopValue=int(disc) ,decayRate=0.01)

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
			return self.waitingForPCard(oldState)
		elif (statePassedIn == 'HAL'):
			return self.HAL(oldState)
		elif (statePassedIn == 'playerChoice'):
			return self.playerChoice(oldState)
		elif (statePassedIn == 'draw2PlayerChoice'):
			return self.draw2PlayerChoice(oldState)
		return oldState

	def waitingForDraw(self, statePassedIn):
		'''
			waitingForDraw
			Result of waiting for the user to draw from the discard or draw pile.
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
			try:
				selectedCard = statePassedIn['discard'].pop()

			except:
				# This could happen if the opponent takes the discard pile and then the user tries to. Added field to json array
				# 	to compensate for this. Set the message visible, then simply pass back the state. 
				statePassedIn['displayCard'] = {'image' : str(selectedCard), 'active' : 0}
				statePassedIn['playerClicks'] = []
				statePassedIn['message']['visible'] = 1
				
				return statePassedIn

			# set all of the user's cards to active, so they are glown. Also remove visibility from them.
			for pCard in statePassedIn['playCard']:
				pCard['active'] = 1
				pCard['visible'] = 0
			# set that as the displayCard
			statePassedIn['displayCard'] = {'image' : str(selectedCard), 'active' : 0}
			# clear out the current list of the player's clicks, so that the new state has a fresh empty list to build into
			statePassedIn['playerClicks'] = []
			# set the new state of the game to be "waitingForPCard", as per our documentation (this will glow the players' cards, etc)
			statePassedIn['state'] = "waitingForPCard"

		# if the user has chosen a card from the deck:
		else:
			# what was the card they picked from the deck? Note that we must also handle the case of the deck being empty 
			try:
				drawnCard = statePassedIn['deck'].pop()

				# here, we'll need to know if it is a kind of power card and indicate that to the view.
				# 	the power cards we really care about, because they make glows appear differently on the gameboard, are the
				#	draw2 and the swap cards. 
				if(drawnCard == 10):
					# draw 2. Glow the deck and discard
					statePassedIn['deckActivity'] = 1
					statePassedIn['discardActivity'] = 1
				elif(drawnCard == 12):
					# swap. glow the discard, opponents cards, and the player's cards.
					statePassedIn['discardActivity'] = 1
					for pCard in statePassedIn['playCard']:
						pCard['active'] = 1
					for cCard in statePassedIn['compCard']:
						cCard['active'] = 1
				elif(drawnCard == 11):
					#peek card, player can view their cards or the deck, or discard it
					statePassedIn['deckActivity'] = 1
					statePassedIn['discardActivity'] = 1
					for cCard in statePassedIn['playCard']:
						cCard['active'] = 1
				else:
					# a number card or peek card was draw. glow deck and player's cards
					statePassedIn['discardActivity'] = 1
					for pCard in statePassedIn['playCard']:
						pCard['active'] = 1
			except:
				# no cards left in the deck. The round ends
				return self.endGame(statePassedIn)

			# add the card to the display card 
			statePassedIn['displayCard'] =  {'image' : str(drawnCard), 'active' : 0}
			# clear out the current list of the player's clicks, so that the new state has a fresh empty list to build into
			statePassedIn['playerClicks'] = []
			# set the new state of the game to be "playerChoice", as per our documentation
			statePassedIn['state'] = "playerChoice"

			# check for knock state
			statePassedIn = self.checkKnock(statePassedIn)

		return statePassedIn

	def waitingForPCard(self, statePassedIn):
		'''
			waitingForPCard
			The user has clicked on the discard pile and must now swap out a card. 
			This state handler is used to update the state in accordance with the results of the player's choice (what the
			user clicked on the gameboard). 
			Note that this automatically handles the case of a power card drawn from the discard pile, as there simply is no
			logic built into this function to handle them. 
			Parameters:
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the user's choices.
		'''
		# what is the card they want to swap with? well i dunno?!!
		swapCard = statePassedIn['playerClicks'][0]

		# get the active card 
		activeCard = statePassedIn['displayCard']

		# put the active card into the hand at the position the swapCard was at, and discard the other
		if(swapCard == 'playerCard1'):
			statePassedIn['discard'].append(statePassedIn['playCard'][0]['image'])
			statePassedIn['playCard'][0]['image'] = activeCard['image']

		elif(swapCard == 'playerCard2'):
			statePassedIn['discard'].append(statePassedIn['playCard'][1]['image'])
			statePassedIn['playCard'][1]['image'] = activeCard['image']

		elif(swapCard == 'playerCard3'):
			statePassedIn['discard'].append(statePassedIn['playCard'][2]['image'])
			statePassedIn['playCard'][2]['image'] = activeCard['image']

		else:
			statePassedIn['discard'].append(statePassedIn['playCard'][3]['image'])
			statePassedIn['playCard'][3]['image'] = activeCard['image']

		# reset the activecard, reset the clicks list, set the new state
		statePassedIn['displayCard'] = {'image' : "13", 'active' : 0}
		statePassedIn['playerClicks'] = []
		statePassedIn['state'] = "HAL" 

		# check for knock state
		statePassedIn = self.checkKnock(statePassedIn)

		return statePassedIn

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

		# what is the difficulty level?
		# HAL remembers things better according to the difficulty level chosen. We must keep track of everything he has seen. 
		#	The chance of remembering what he has seen is related to the difficulty level he has been set to. This can be done
		#	in the database, or perhaps just in a variable here, or even in the json. 
		
		logging.info("Made it to the HAL State")
		# self.ai.testMe()
		# newModel = DatastoreInteraction(statePassedIn['sessionId'])
		# parameterDict = newModel.getHAL()
		# logging.info(parameterDict)

		#Did the player knock and the counter is down?? 
		#THIS CODE TO BE MODIFIED ONCE THE CLASS VARIABLE TO MAINTAIN KNOCKING FROM THE AI'S SIDE IS UP
		ai = HAL.HAL()
		ai.setupAIObject(statePassedIn['sessionId'])
		newState = ai.doTurn(statePassedIn)		

		#HAL needs to set the activity of the cards for the player to use on their turn before it ends it's
		statePassedIn['deckActivity'] = 1
		statePassedIn['discardActivity'] = 1
		statePassedIn['state'] = "waitingForDraw"
		logging.info(statePassedIn)

		# need to check the deck to see if the deck is empty
		# if the deck is empty, its time for the endgame state
		if( len(newState['deck']) == 0 ):
			logging.info("Deck is empty")
			freshState = self.endGame(newState)
		# otherwise, proceed as normal.

		return statePassedIn

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

		# has the player chosen to use or discard? (If they have chosen to use, this will also tell you what they have clicked)
		userChoice = statePassedIn['playerClicks'][0]
		# and what is the card they have made this decision about?
		currentCard = statePassedIn['displayCard']['image']

		# if choice is discard, add the card the discard pile, and remove it from the displayCard. clear the playerclicks as well
		if(userChoice == 'discardPile'):
			# logging.info('Choice was to discard it')
			# take the card the user has decided about and add it to the discard
			statePassedIn['discard'].append(currentCard)
			# reset displayCard
			statePassedIn['displayCard'] = {'image' : "13", 'active' : 0} 
			# clear the player clicks queue
			statePassedIn['playerClicks'] = []
			# the user's turn is now over, so it is up to HAL to take over as the new state
			statePassedIn['state'] = "HAL"

		# otherwise, the choice is use. Determine if it is a number card or a power card first
		else:
			# logging.info('Choice was to use it')
			if(int(currentCard) <= 9):
				# this is a number card. Update the value of the card in thier hand they clicked on with this new value, 
				# 	as well as updating the discard pile with the card they swapped out for.

				# NOTE: This seems like a clunky way to do this. A better option would be to add a k/v pair to each playcard
				#	slot of the div id, allowing us to simply do this=> statePassedIn['playCard'][userChoice] = whatever?
				if(userChoice == 'playerCard1'):
					# first, discard the card they have chosen to replace
					statePassedIn['discard'].append(statePassedIn['playCard'][0]['image'])
					# next, update thier hand with the card they have decided upon
					statePassedIn['playCard'][0]['image'] = currentCard

				elif(userChoice == 'playerCard2'):
					statePassedIn['discard'].append(statePassedIn['playCard'][1]['image'])
					statePassedIn['playCard'][1]['image'] = currentCard

				elif(userChoice == 'playerCard3'):
					statePassedIn['discard'].append(statePassedIn['playCard'][2]['image'])
					statePassedIn['playCard'][2]['image'] = currentCard 

				else:
					statePassedIn['discard'].append(statePassedIn['playCard'][3]['image'])
					statePassedIn['playCard'][3]['image'] = currentCard 

				# housekeeping
				statePassedIn['displayCard'] = {'image' : "13", 'active' : 0} 
				statePassedIn['playerClicks'] = []
				statePassedIn['state'] = "HAL"

			else:
				# this is a power card. What kind of power card are we talking about?
				if(int(currentCard) == 10):
					# a draw 2 power card. the deck and discard should glow ('use' or 'discard').
					# this is the start of the draw2 sequence. Helpful to start here when trying to visualize the series of events,
					#	and realize that when playerChoice is called, it is processing the results of a player's choice to draw from
					#	the deck.

					# make the player's cards non-clickable (non-active)
					for pCard in statePassedIn['playCard']:
						pCard['active'] = 0
					
					# draw the top card from the deck, and set it as the display card. put the display card(the draw 2) in the discard pile
					statePassedIn['discard'].append(currentCard)
					try:
						# draw a card for the player
						drawnCard = statePassedIn['deck'].pop()
					except:
						# no cards left in the deck. The round ends, so we should probably have a round end state? 
						# It would probs need to be something similar to a knock state, which we may have to do as well.
						return self.endGame(statePassedIn)

					# set the display card to the newly drawn card
					statePassedIn['displayCard']['image'] = drawnCard

					# depending on the card they just drew, we need to glow certain areas. However, we always need to glow the discard pile
					statePassedIn['discardActivity'] = 1

					# depending on what that newly drawn card is, set the right things glowing 
					statePassedIn = self.glowCards(drawnCard, statePassedIn)

					# set the draw2 counter to 2, the initial value for a draw2 series
					statePassedIn['draw2Counter'] = 2

					statePassedIn['state'] = 'draw2PlayerChoice'

				elif(int(currentCard) == 11):
					# this is a peek power card. Set the card they wanted to peek at to be visible. 
					if(userChoice == 'playerCard1'):
						statePassedIn['playCard'][0]['visible'] = 1
					elif(userChoice == 'playerCard2'):
						statePassedIn['playCard'][1]['visible'] = 1
					elif(userChoice == 'playerCard3'):
						statePassedIn['playCard'][2]['visible'] = 1
					else:
						statePassedIn['playCard'][3]['visible'] = 1
					# their turn is over, so send in the AI state
					statePassedIn['state'] = "HAL"

				else:
					# coming here means the user's card is a 12, or swap power card.
					# We have to swap the cards the player clicked on, so that means there are two items in the clicks array
					# 	get the items out of the array, find out what they are, and swap their positions.

					# get the items out of the player clicks array
					card1 = statePassedIn['playerClicks'].pop()
					card2 = statePassedIn['playerClicks'].pop()
					
					# do the swap
					statePassedIn = self.swapCards(card1, card2, statePassedIn)

					# you've swapped, and now the turn is over
					statePassedIn['state'] = "HAL"
				if(statePassedIn['state']=="HAL"):
					#Set the active cards that will be glown on the players next turn 
					statePassedIn['discardActivity'] = 1
					statePassedIn['deckActivity'] = 1
				# put the power card in the discard pile
				statePassedIn['discard'].append(currentCard)
				# reset the displaycard and playclicks 
				statePassedIn['displayCard'] = {'image' : "13", 'active' : 0}
				statePassedIn['playerClicks'] = []
				
		# check for knock state
		statePassedIn = self.checkKnock(statePassedIn)

		return statePassedIn

	def draw2PlayerChoice(self, statePassedIn):
		'''
			draw2PlayerChoice
			Due to the nature of the draw 2 power card, the user is able to draw multiple cards and process each of those states 
			while in this state.
			Parameters:
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the user's choices.

			THIS is what gets passed back after a player has made his draw2 decision on the game board (has drawn something).
			now we need to know what that card is, and what the player wants to do with it.

			this state will increment or decrement (draw2Counter) max 2.
			this will either pass back draw2PlayerChoice or HAL, depending on what the player has drawn and decided to do.
			(Very similar to playerchoice, but has a counter that is incremented and decremented)
		'''
		# pull out the user's choice of what to do from playerclicks
		userChoice = statePassedIn['playerClicks'][0]

		# pull out currently displayed card
		currentCard = statePassedIn['displayCard']['image']

		# if the user's choice was to discard:
		if(userChoice == 'discardPile'):

			# what's the counter looking like? If it is 0, then the user has used up all of their discards and their turn is over.
			if(statePassedIn['draw2Counter'] <= 0):
				# put current display card into discard pile and reset it
				statePassedIn['discard'].append(currentCard)
				statePassedIn['displayCard'] = {'image' : "13", 'active' : 0} 
				# clear the player clicks queue
				statePassedIn['playerClicks'] = []
				# the user's turn is now over, so it is up to HAL to take over as the new state
				statePassedIn['state'] = "HAL"

				# check for knock state
				statePassedIn = self.checkKnock(statePassedIn)

				return statePassedIn

			# otherwise, the user still has some draw2 power left.
			else:
				# decrement the counter by 1
				statePassedIn['draw2Counter'] -= 1
				# put current display card into discard pile
				statePassedIn['discard'].append(currentCard)
				# pop out a new card for the user from the deck
				try:
					drawnCard = statePassedIn['deck'].pop()
				except:
					# no cards left in the deck. The round ends
					return self.endGame(statePassedIn)

				# set the display card to what we've just drawn
				statePassedIn['displayCard']['image'] = drawnCard 
				# reset playerclicks
				statePassedIn['playerClicks'] = []

				# depending on what that newly drawn card is, set the right things glowing 
				statePassedIn = self.glowCards(drawnCard, statePassedIn)

				# leave state at draw2PlayerChoice, and return it to the view so the player can decide what to do with their
				#	newly drawn card.
				
				# check for knock state
				statePassedIn = self.checkKnock(statePassedIn)

				return statePassedIn

		# otherwise, the user's choice must've been to use the card that was drawn
		else:
			# we can learn about what the user clicked (how they decided to use the card) from the currently displayed card...
			
			# if the card has a value of from 1 to 9, it is a regular number card. Therefore, they chose to swap it out with
			#	another card in their spread. 
			if(currentCard <= 9):
				# add the current card to discard
				statePassedIn['discard'].append(currentCard)

				# what was the card that the user clicked (translated from the value in the playerclicks array), and what was its
				#	index position?
				idx, cardArray, cardClicked = self.translateDivToCard(userChoice, statePassedIn)

				# put the (up until now) currently displayed card into what the player clicked
				statePassedIn[cardArray][idx]['image'] = currentCard

				# reset the playerclicks array and the display card.
				statePassedIn['playerClicks'] = []
				statePassedIn['displayCard'] = {'image' : "13", 'active' : 0}

				# return, with the state being set to HAL
				statePassedIn['state'] = 'HAL'

				# check for knock state
				statePassedIn = self.checkKnock(statePassedIn)

				return statePassedIn

			# if the card is a 10, then it is a draw 2 card. This also means they've clicked the deck.
			elif(currentCard == 10):
				# pop a new card from the deck
				try:
					drawnCard = statePassedIn['deck'].pop()
				except:
					# no cards left in the deck. The round ends
					return self.endGame(statePassedIn)

				# clear the clicks array
				statePassedIn['playerClicks'] = []

				# proceed as per the draw2 in playerChoice...
				# set the display card to the newly drawn card
				statePassedIn['displayCard']['image'] = drawnCard

				# depending on the card they just drew, we need to glow certain areas. However, we always need to glow the discard pile
				statePassedIn['discardActivity'] = 1

				# depending on what that newly drawn card is, set the right things glowing 
				statePassedIn = self.glowCards(drawnCard, statePassedIn)

				# set the draw2 counter to 2, the initial value for a draw2 series (since we are beginning again)
				statePassedIn['draw2Counter'] = 2
				statePassedIn['state'] = 'draw2PlayerChoice'

				# check for knock state
				statePassedIn = self.checkKnock(statePassedIn)

				return statePassedIn

			# if the card is an 11, then it is a peek card
			elif(currentCard == 11):
				# this mean's they've chosen a card of theirs to look at. get that card from player clicks
				idx, cardArray, cardClicked = self.translateDivToCard(userChoice, statePassedIn)
				# set its visibility to 1
				statePassedIn[cardArray][idx]["visible"] = 1
				# put the active display card into the discard pile and reset that display card
				statePassedIn['discard'].append(currentCard)
				statePassedIn['displayCard'] = {'image' : "13", 'active' : 0}
				# clear the clicks array
				statePassedIn['playerClicks'] = []
				# return, with the state being set to HAL
				statePassedIn['state'] = "HAL"
				
				# check for knock state
				statePassedIn = self.checkKnock(statePassedIn)

				return statePassedIn
				
			# then the card is a 12, which means it is a swap card.
			else:
				# This means they've chosen two cards, one of theirs and one of their opponents. Get those two cards and 
				#	perform the swap as in playerChoice. 
				# get the items out of the player clicks array
				card1 = statePassedIn['playerClicks'].pop()
				card2 = statePassedIn['playerClicks'].pop()
				# do the swap
				statePassedIn = self.swapCards(card1, card2, statePassedIn)
				# clear the clicks array
				statePassedIn['playerClicks'] = []
				# return, with the state being set to HAL.
				statePassedIn['state'] = "HAL"

				# check for knock state
				statePassedIn = self.checkKnock(statePassedIn)

				return statePassedIn
		
	def endGame(self, statePassedIn):
		'''
			endGame
			State handler used to sum of the scores of a round and add them to the total score value in the state JSON.
			Also decides if the game is over or just the round is over.
			Note about the sleep timers: Google, get your shit together and serialize your datastore. This is just ridiculous.
			Parameters:
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the user's choices.
		'''
		logging.info("Made it to the endgame state")

		# set the state to endgame so the view knows what to do
		statePassedIn['state'] = "endGame"

		# make a new object to interact with the datastore
		newModel = DatastoreInteraction(statePassedIn['sessionId'])
		# update the number of rounds played in the game
		newModel.updateGameRounds()

		# what is the total score of each player's hand?
		pScore = 0
		cScore = 0

		# check to see if the deck has enough cards in it to accomodate swapping all potential power cards
		# also, remove all power cards, so they cannot be distributed again
		numberCards = [ [0]* 4, [1]*4, [2]*4, [3]*4, [4]*4, [5]*4, [6]*4, [7]*4, [8]*4, [9]*9 ]
		cardReplace = sum(numberCards, [])
		shuffle(cardReplace)
		
		# set the cards to visible, get the score, and swap out any power cards
		for pCard in statePassedIn['playCard']:
			cardVal = int(pCard['image'])
			# if the card is a power card, replace it
			if(cardVal >= 10):
				pCard['image'] = cardReplace.pop()
			# add to running total and set visible
			pScore += cardVal
			pCard['visible'] = 1

		for cCard in statePassedIn['compCard']:
			cardVal = int(cCard['image'])
			# if the card is a power card, replace it
			if(cardVal >= 10):
				cCard['image'] = cardReplace.pop()
			cScore += cardVal
			cCard['visible'] = 1

		logging.info("This is the player score")
		logging.info(pScore)
		logging.info("This is the computer score")
		logging.info(cScore)

		# who wins the round?
		if (pScore < cScore):
			# player wins
			logging.info("player wins")
			statePassedIn["win"] = 1
			# update the fact that the player won a round, and played a round
			newModel.updateRoundsWonTotal()
			time.sleep(1)

		elif (pScore > cScore):
			# computer wins
			logging.info("computer wins")
			newModel.updateRoundsLostTotal()
			time.sleep(1)

		else:
			# tie
			logging.info("tie!!")
			statePassedIn["win"] = 2
			newModel.updateRoundsPlayedTotal()
			time.sleep(1)

		# use sleep to prevent the datastore from overwriting itself
		time.sleep(1)

		# add the player score to the running total of their score for all games so far in the database
		newModel.updatePlayerScore(pScore)
		time.sleep(1)
		# add the computer score to the running total for HAL
		newModel.updateComputerScore(cScore)
		time.sleep(1)
		# add the players score to the running total for the current game 
		newModel.updateGameScore(pScore)
		time.sleep(1)
		# what is the player and computer's total score now for this specific game?
		playerTotalScore, computerTotalScore = newModel.getTotalGameScore()
		time.sleep(1)

		# is the game over? If yes...
		if(playerTotalScore >= self.ENDGAME_SCORE or computerTotalScore >= self.ENDGAME_SCORE):
			logging.info("Game is now over")

			# update the json to reflect that the game is now over
			statePassedIn['gameOver'] = 1

			# is the player's score, retrieved from the database, greater than the computer's score? Who won?
			if (playerTotalScore > computerTotalScore):
				# player loses
				logging.info("Player Loses")
				gameText = "You Lose,"
				newModel.updateGameLose()
			elif(computerTotalScore > playerTotalScore):
				# player wins
				logging.info("Player Wins")
				gameText = "You Win,"
				statePassedIn["win"] = 1
				newModel.updateGameWin()
			else:
				# a tie
				logging.info("A tie has occurred")
				gameText = "It was a tie,"
				statePassedIn["win"] = 2
				newModel.updateGameLose()

			time.sleep(1)

			statePassedIn['message']['text'] = "Game Over. " + gameText + str(playerTotalScore) + " to " + str(computerTotalScore) + ". Would you like to start a new game?"

			return statePassedIn

		# if the game is not over, only the rounds is. Therefore, we begin a new round
		else:
			time.sleep(1)

			logging.info("Starting a new round")
			statePassedIn['message']['text'] = "The round is over! Your score for the round was: " + str(pScore) + ". The computer's score was: " + str(cScore) + ". Would you like to continue playing?"

			return statePassedIn
		

	'''
		The following are utility methods, employed by the state handlers to perform various standard tasks. They are separated
		from the handlers themselves for the sake of modularity and readability. 
	'''

	def swapCards(self, card1, card2, statePassedIn):
		'''
			swapCards
			Function used to swap the image values of 2 cards. Used when a Swap power card is activated.
			Parameters:
				card1 and card2, the two cards taken from the playerClicks array, which must be swapped.
				statePassedIn, the current state of the game
			Returns:
				statePassedIn, the gamestate modified by the swap
		'''
		# modify the message property of the json to explain to the player what to do.
		statePassedIn['message']['visible'] = 1
		statePassedIn['message']['text'] = "Choose one of your cards and one of your opponent's cards to swap."

		# is card1 player or opponent? Note the format of these clicks, which are div names, for example: playerCard4 or opCard2
		# (you can tell whats what by the first letter of the div name passed into the playerclicks array, either p or o)
		if (card1[0] == 'p'):
			# a player card that must be swapped out with an opponent's card
			# get the index of this card (you can tell this by subtracting 1 from the last character of the div name passed in)
			playerIndex = int(str(card1[-1])) - 1
			# get the index of the other card, which must be the opponent's card
			oppIndex = int(str(card2[-1])) - 1
			# swap the image values of these two cards in the dictionaries, using a temp variable
			tmpPlayerImage = statePassedIn['playCard'][playerIndex]['image']
			statePassedIn['playCard'][playerIndex]['image'] = statePassedIn['compCard'][oppIndex]['image']
			statePassedIn['compCard'][oppIndex]['image'] = tmpPlayerImage
		else:
			# a computer card that must be swapped out with a player's card. just do the reverse (change card numbers, ie card2 becomes card1)
			playerIndex = int(str(card2[-1])) - 1
			oppIndex = int(str(card1[-1])) - 1
			tmpPlayerImage = statePassedIn['playCard'][playerIndex]['image']
			statePassedIn['playCard'][playerIndex]['image'] = statePassedIn['compCard'][oppIndex]['image']
			statePassedIn['compCard'][oppIndex]['image'] = tmpPlayerImage

		return statePassedIn

	def glowCards(self, drawnCard, statePassedIn):
		'''
			glowCards
			This function is used to set a flag (active, in the JSON) in elements of the gameboard to indicate to
			the view that they should glow. This glow is a signal to the player of what options they have available
			to them. 
			Parameters:
				drawnCard, the card they player has just drawn from the deck, which dictates what should glowCards
			Returns:
				statePassedIn, the modified JSON of the gamestate with the active flag set in the appropriate areas
		'''
		if(drawnCard == 10):
			# draw 2. Glow the deck and discard
			statePassedIn['deckActivity'] = 1
		elif(drawnCard == 12):
			# swap. glow the discard, opponents cards, and the player's cards.
			statePassedIn['discardActivity'] = 1
			for pCard in statePassedIn['playCard']:
				pCard['active'] = 1
			for cCard in statePassedIn['compCard']:
				cCard['active'] = 1
		else:
			# a number card or peek card was draw. glow deck and player's cards
			statePassedIn['deckActivity'] = 1
			for cCard in statePassedIn['compCard']:
				cCard['active'] = 1

		return statePassedIn

	def resetActiveFlags(self, statePassedIn):
		'''
			resetActiveFlags
			This function sets all of the active flags in the JSON array to 0, effectively removing the glow from each element
			and preparing the state to receive new glow elements. 

			It also resets the visibility of cards, making them non-visible

			Parameters:
				statePassedIn, the state passed in by the view.
			Return:
				statePassedIn, the state with all of the active flags set to 0

		'''
		# reset computer and user card active and visible flags
		for pCard in statePassedIn['playCard']:
			pCard['active'] = 0
			pCard['visible'] = 0
		for cCard in statePassedIn['compCard']:
			cCard['active'] = 0
			cCard['visible'] = 0

		# reset deck and discard flags
		statePassedIn['discardActivity'] = 0
		statePassedIn['deckActivity'] = 0

		# reset displayCard flag
		statePassedIn['displayCard']['active'] = 0

		# reset the message visibilty and it's text 
		statePassedIn['message'] = {"visible" : 0, "text" : "There is no card to be selected here"}

		return statePassedIn

	def translateDivToCard(self, divToTranslate, statePassedIn):
		'''
			translateDivToInt
			Function used to take a click the user made and determine what card it represents. 
			Parameters:
				divToTranslate, the name of the div that the user clicked. This is taken from the playerClicks array.
				statePassedIn, the current state of the game.
			Return:
				cardIndex, the position in the card array the card occupies.
				cardArray, the type (player of computer) of array the card belongs to.
				cardChoice, the card object that the divToTranslate represented.
		'''
		# What is the position of the card in whatever card array it is found. The position is from 0 to 3.
		cardIndex = int(str(divToTranslate[-1])) - 1
		cardArray = ""

		# determine if the card was a user or computer card
		if (divToTranslate[0] == 'p'):
			# this is a playerCard. 
			logging.info(statePassedIn)

			cardChoice = statePassedIn['playCard'][cardIndex]
			cardArray = 'playCard'

		elif(divToTranslate[0] == 'o'):
			# this is a computer card.
			cardChoice = statePassedIn['compCard'][cardIndex]
			cardArray = 'compCard'
		else:
			# something went wrong
			logging.info("something went wrong")

		return cardIndex, cardArray, cardChoice

	def checkKnock(self, statePassedIn):
		'''
			checkKnock
			Used to determine the knock status of any state passed in by the view. 
			If the knock status is 0, then no knocking has occurred and play proceeds as normal.
			If the knock status is 2, then the player has just clicked knock, and the opponent has one more round to play. 
			If the knock status is 1, then the player has already clicked knock and the state we are working with is the 
			result of the opponent's turn. This means the next state must be endGame.
		'''
		knockStatus = statePassedIn['knockState']

		if(knockStatus == 2):
			statePassedIn['knockState'] = 1

		elif(knockStatus == 1):
			statePassedIn['knockState'] = 0
			statePassedIn['state'] = endGame

		else:
			pass

		return statePassedIn
