#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Phelan
# 	SUUUP
# This handler executes the actual game environment. 
from handler import *
from random import shuffle
from random import choice
import cgi
import logging
import json

ENDGAME_SCORE = 60

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
		# logging.info(self.request.arguments())

		# get the json object passed in by the view (assuming it is called currentState)
		oldState = json.loads(cgi.escape(self.request.body))

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
		# make a list of lists of cards, flatten it, pick out a discard card that isnt a power card, then shuffle the deck
		# also, dang this is ugly.  Seriously ugly.

		numberCards = [ [0]* 4, [1]*4, [2]*4, [3]*4, [4]*4, [5]*4, [6]*4, [7]*4, [8]*4, [9]*9 ]
		powerCards = [ [10]*3, [11]*3, [12]*3 ]
		deck = sum(numberCards, [])
		shuffle(deck)
		subDeck = sum(powerCards, [])
		shuffle(subDeck)
		discardCard = str(deck.pop(choice(deck)))
		for p in subDeck:
			deck.append(p)
		shuffle(deck)

		#intitial JSON array. Note that I've added a playerClicks array to track what the player has selected (eg discard or draw)
		newState = {"compCard" : [
						{"image" : str(deck.pop()), 'active' : 0, 'visible' : 0}, 
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0}, 
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0},
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0}],  
					"playCard" : [
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0}, 
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0}, 
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0},
						{'image' : str(deck.pop()), 'active' : 0, 'visible' : 0}], 
					"discard" : [discardCard],
					"discardActivity" : 1,
					"deck" : deck,
					"deckActivity" : 1,
					"displayCard" : {'image' : "13", 'active' : 0}, 
					"knockState" : 0, 
					"state" : "waitingForDraw",
					"score" : 0,
					"gameOver" :0,
					"playerClicks" : [],
					"draw2Counter" : 0,
					"message": {"visible" : 0, 'text' : "There is no card to be selected here"}
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
			return self.waitingForPCard(oldState)
		elif (statePassedIn == 'HAL'):
			return self.HAL(oldState)
		elif (statePassedIn == 'playerChoice'):
			return self.playerChoice(oldState)
		elif (statePassedIn == 'draw2PlayerChoice'):
			pass
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
			except:
				# no cards left in the deck. The round ends, so we should probably have a round end state? 
				# It would probs need to be something similar to a knock state, which we may have to do as well.
				pass

			# add the card to the display card 
			statePassedIn['displayCard'] =  {'image' : str(drawnCard), 'active' : 0}
			# clear out the current list of the player's clicks, so that the new state has a fresh empty list to build into
			statePassedIn['playerClicks'] = []
			# set the new state of the game to be "playerChoice", as per our documentation
			statePassedIn['state'] = "playerChoice"

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
		statePassedIn['state'] = "HAL" # change this to anything and it works. WHY?

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
		statePassedIn['state'] = "waitingForDraw"
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
					# a draw 2 power card. the deck and discard should glow (use or discard).
					# this is the start of the draw2 sequence. Helpful to start here when trying to visualize the series of events,
					#	and realize that when playerChoice is called, it is processing the results of a player's choice to draw from
					#	the deck.
					
					# draw the top card from the deck, and set it as the display card. put the display card(the draw 2) in the discard pile
					statePassedIn['discard'].append(currentCard)
					drawnCard = statePassedIn['deck'].pop()
					statePassedIn['displayCard']['image'] = drawnCard

					# depending on the card they just drew, we need to glow certain areas. However, we always need to glow the discard pile
					statePassedIn['discardActivity'] = 1

					if(drawnCard <= 9 or drawnCard == 11):
						# if the card is a number card or peek card, then glow the player's 4 cards
						for pCard in statePassedIn['playCard']:
							pCard['active'] = 1

					elif(drawnCard == 12):
						# if the card is a swap card, then glow the player's 4 cards and the opponent's 4 cards
						for pCard in statePassedIn['playCard']:
							pCard['active'] = 1
						for cCard in statePassedIn['compCard']:
							cCard['active'] = 1
					else:
						# if the cards is a draw2 card, then glow the deck again
						statePassedIn['deckActivity'] = 1

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
					card1 = newState['playerClicks'].pop()
					card2 = newState['playerClicks'].pop()
					
					# do the swap
					statePassedIn = self.swapCards(card1, card2, statePassedIn)

					# you've swapped, and now the turn is over
					statePassedIn['state'] = "HAL"

				# put the power card in the discard pile
				statePassedIn['discard'].append(currentCard)
				# reset the displaycard and playclicks 
				statePassedIn['displayCard'] = {'image' : "13", 'active' : 0}
				statePassedIn['playerClicks'] = []
				
		return statePassedIn

	def swapCards(self, card1, card2, statePassedIn):
		'''
			swapCards
			Function used to swap the image values of 2 cards. Used when a Swap power card is activated.
			Parameters:
				card1 and card2, the two cards taken from the playerClicks array, which must be swapped.
				statePassedIn, the current state of the game
		'''
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
		# how many draws does the player has left to them?
		currentCounter = int(statePassedIn['draw2Counter'])

		# what's the card the player has drawn as a result of playing his draw 2 action? 
		currentCard = statePassedIn['displayCard']['image']

		# have they chosen to use or discard it for another draw?
		userChoice = statePassedIn['playerClicks'][0]

		# If the user chose to discard the card they drew in the draw2 sequence, do this:
		if(userChoice == 'discardPile'):
			# take the card the user has decided about and add it to the discard
			statePassedIn['discard'].append(currentCard)
			# reset displayCard
			statePassedIn['displayCard'] = {'image' : "13", 'active' : 0} 
			# clear the player clicks queue
			statePassedIn['playerClicks'] = []
			# decrement the draws the user has left
			currentCounter -= 1
			statePassedIn['draw2Counter'] = currentCounter

			# if there are no more draws left, then pass it over to the AI. Otherwise, they may draw again
			if(currentCounter <= 0):
				statePassedIn['state'] = "HAL"
				statePassedIn['draw2Counter'] = 0
			else:
				statePassedIn['state'] = "draw2PlayerChoice"
				# let the user know they can draw again by glowing the deck
				statePassedIn['deckActivity'] = 1

		# If the user chose to use the card they drew in the draw2 sequence, do this:
		else:
			# send back what the player can do with it, depending on the card. 
			if(int(currentCard) <= 9):
				# This is a regular number card. does the player want to use it, or discard it to draw again? 
				# We must answer these questions for all of the cards drawn this way. This'll be done in draw2playeraction
				
				# set all of the user's cards to glow
				for pCard in statePassedIn['playCard']:
					pCard['active'] = 1
				# the user has used thier card, so turn is over and its HAL time
				statePassedIn['state'] = "HAL"

			elif(int(currentCard) == 10):
				# this is draw2 power card
				pass
			elif(int(currentCard) == 11):
				# this is a peek power card
				pass
			else:
				# this is a swap power card
				pass	

		return statePassedIn
		
	def endGame(self, statePassedIn):
		'''
			endGame
			State handler used to sum of the scores of a round and add them to the total score value in the state JSON.
			Also decides if the game is over or just the round is over.
			Parameters:
				statePassedIn, the (current) state of the game that has been passed in by the client side (view) ajax call.
			Returns:
				newState, the new state of the game as delinated by the statePassedIn and the user's choices.
		'''
		# what is the total score of each player's hand?
		pScore = 0
		cScore = 0
		# set the cards to visible at this time as well
		for pCard in statePassedIn['playCard']:
			pScore += int(pCard['image'])
			pCard['visible'] = 1
		for cCard in statePassedIn['compCard']:
			cScore += int(cCard['image'])
			cCard['visible'] = 1

		# who wins?
		if pScore > cScore:
			# player wins
			pass
		elif pScore < cScore:
			# computer wins
			pass
		else:
			# tie
			pass

		# add each player's scores to the running total of their score for the game so far

		# is the game over? (is either player's total score over or at 60?)
		statePassedIn['state'] = "endGame"
		return statePassedIn

