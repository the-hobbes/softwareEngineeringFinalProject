#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Ethan
#
# This file handles the AI logic and database construction
from handler import *

from random import choice
from random import randint
from random import random as randZ
from google.appengine.ext import db
import logging
import json
import time
from python.gameModel import DatastoreInteraction

class HAL(db.Model):
	'''
		HAL 
		This class uses it's current memory of what each of the cards are 
		and bases it's decisions on that. It continually tries to make the
		most appropriate decisions based on it's difficulty level.

		Difficulty of 0 means completely random choices with no intelligence
		Difficulty of 1 means the decay rate of the memory is fairly high
		Difficulty of 2 means slow rate of moderate
		Difficulty of 3 means no recay rate and perfect recall. Good luck.
	'''
	#Estimates used in decision calculations
	pkSessionID = db.StringProperty()
	estAIScore = db.IntegerProperty(default=0)
	estOppScore = db.IntegerProperty(default=0)
	#list for memory values 
	opCardsMem = db.ListProperty(float)
	aiCardsMem = db.ListProperty(float)
	#list for the actual card values we know
	opCards = db.StringProperty(str)
	aiCards = db.StringProperty(str)
	discardTopValue = db.IntegerProperty(default=0)
	#Memory decay rate, abs and rounded between 0.01-.99
	decayRate = db.FloatProperty(default=0.0)
	#This will be a string that builds up to tell the view what to do
	actionsToTake = ""
	diff =0
	realOpCards = []
	realAiCards = []

	def testMe(self):
		logging.info("Test Satisfactory")

	def rememberTopCard(self,topCard):
		'''
		rememberTopCard
			topCard, The top card of the deck to be remembered
		'''
		self.discardTopValue = topCard

	def setupAIObject(self, sessionId):
		'''
			setupAIObject
			This is used to retrieve all of the information from the datstore about the AI object and set the class variables
			equal to the values of the entitites retrieved in this way. This should be called whenever a new instance of 
			HAL is created. 
			Parameters:
				sessionId, the sessionId which identifies the HAL entity we are working with. 
		'''
		newModel = DatastoreInteraction(sessionId)
		valueDict = newModel.getHAL()

		self.pkSessionID = valueDict['pkSessionID']
		self.estAIScore = valueDict['estAIScore']
		self.estOppScore = valueDict['estOppScore']
		self.opCardsMem = valueDict['opCardsMem']
		self.aiCardsMem = valueDict['aiCardsMem']
		tmpOP = valueDict['opCards'].encode('utf-8').replace("u","")
		tmpAI = valueDict['aiCards'].encode('utf-8').replace("u","")
		#Welcome to hack central. where python has type issues!
		self.realOpCards = eval(str(tmpOP))
		self.realAiCards = eval(str(tmpAI))
		self.opCards = tmpOP
		self.aiCards = tmpAI
		self.discardTopValue = valueDict['discardTopValue']
		self.decayRate = valueDict['decayRate']

	def doTurn(self,state):
		'''
		Does the HAL's turn, this function is essentially a way for the AI to keep

		'''
		logging.info("made it to Hal's DO TURN!")
		#clear old actions
		self.actionsToTake = ""
		#Decide whether or not to draw from the discard pile or the deck
		#If the card on the discard pile is lower than the largest number we think we have
		#take it, else draw from the deck
		discardPile = state['discard'][-1]
		maxVal = 0
		i,j=0,0
		human,aiCards = self.getMemory()
		logging.info("in do turn...")
		for c in aiCards:
			if(maxVal < c):
				i=j
				maxVal = c
			j=j+1
		#Now we know what the maxVal is
		card = 0
		if(maxVal > discardPile):
			#Pull from the discard pile
			card = state['discard'].pop()
			self.actionsToTake = self.actionsToTake + " HAL pulling from Discard"
		else:
			#Pull from the deck
			card = -1
			try:
				card = state['deck'].pop()
			except Exception, e:
				#well fuck. no more cards?!
				state['state'] = 'endgame'
				return state
			else:
				pass
			
			self.actionsToTake = self.actionsToTake + " HAL pulling from Deck"
		#We now have a card, is it a regular card or a power card?
		self.actionsToTake = self.actionsToTake + " HAL pulled a " + str(card)
		if(card < 10):
			#Regular Card
			#Choose whichever card is highest in our hand, if card is lower then take it
			#else discard
			indexOfHighest,highVal = self.findHighestInHand()
			if(card < highVal):
				#Yes we do!
				#give us the card and we remember it well becuase we just got it	
				state['discard'].append(self.realAiCards[indexOfHighest]['image'])
				self.realAiCards[indexOfHighest] = {'image' : card, 'active' : 0, 'visible' : 0}
				self.aiCards = json.dumps(self.realAiCards)
				self.aiCardsMem[indexOfHighest] = 1.0
				self.actionsToTake = self.actionsToTake + " HAL kept the card!"
			else:
				#NO!
				self.actionsToTake = self.actionsToTake + " HAL discarded the card."
				state['discard'].append(card)
		else:
			#Power Card. Really wish we had  a switch... (python)
			if(card==10):
				self.actionsToTake = self.actionsToTake + " HAL has a draw two card. "
				logging.info("ACTIONS")
				logging.info(self.actionsToTake)
				return self.drawTwo(state)
			elif(card==11):
				self.actionsToTake = self.actionsToTake + " HAL is peeking at his cards."
				logging.info("ACTIONS")
				logging.info(self.actionsToTake)
				return self.peek(state)
			elif(card==12):
				self.actionsToTake = self.actionsToTake + " HAL is going into a swap state"
				logging.info("ACTIONS")
				logging.info(self.actionsToTake)
				return self.swap(state)
			else:
				#Back of a card, aka we drew from an empty deck maybe?
				#need to add in error checking
				state['discard'].append(card)
		
		#Should we knock??
		#We should knock if we think our cards are higher than the players by some threshold
		state = self.shouldKnock(state)

		state['compCard'] = json.loads(self.aiCards)

		logging.info("ACTIONS")
		logging.info(self.actionsToTake)

		#Slowly forget what our cards are\
		self.alzheimer()

		time.sleep(2)
		return state



	def drawTwo(self,state):
		'''
			drawTwo:
				The AI decides what to do with a draw two card
			Parameters:
				state, the state of the game

		'''
		#The AI draws a card and decides if it will keep it, 
		#To decide if it keeps it or not really depends on the value of the card
		#if the value of the card is greater than any it thinks it has in it's hand it will
		#keep it. If it finds a power card it will use it 

		#We draw our first card (from the deck because by the logic in do turn we already disregarded the discard)
		try:
			card = state['deck'].pop()
		except Exception, e:
			#well crap. We're out of cards
			#we disregarded the discard already so we'll just knock and be done with it.
			state['knockState'] = True;
			return state
		else:
			#We have a card!
			#Is it any good?
			if(card < 10):
				#It's a number! 
				#Do we want it?
				indexOfHighest,highVal = self.findHighestInHand()
				if(card < highVal):
					#Yes we do!
					#give us the card and we remember it well becuase we just got it
					state['discard'].append(self.realAiCards[indexOfHighest]['image'])
					self.realAiCards[indexOfHighest] = {'image' : highVal, 'active' : 0, 'visible' : 0}
					self.aiCards = json.dumps(self.realAiCards)
					self.aiCardsMem[indexOfHighest] = 1.0
				else:
					#Meh we could do without it
					state['discard'].append(card)
					#Lets draw a new card (yo dawg I heard you like try catches...)
					try:
						card = state['deck'].pop()
					except Exception, e:
						#well how damn there wasn't anything left to grab!
						state['knockState'] = True
						return state
					else:
						#well goody gumdrops lets get going!
						if(card < 10):
							#well doesnt this seem awfully familiar...
							indexOfHighest,highVal = self.findHighestInHand()
							if(card < highVal):
								#We want it!
								state['discard'].append(self.aiCards['image'])
								self.realAiCards[indexOfHighest] = {'image' : highVal, 'active' : 0, 'visible' : 0}
								self.aiCards = json.dumps(self.realAiCards)
								self.aiCardsMem[indexOfHighest] = 1.0
							else:
								#We dont want it!
								state['discard'].append(card)

						else:
							#It's a power card! Let's use it!
							if(card==10):
								return self.drawTwo(state)
							elif(card==11):
								return self.peek(state)
							elif(card==12):
								return self.swap(state)
							else:
								#back of a card or something strange? 
								#push whatever it was onto the discard pile
								state['discard'].append(card)
								pass			


			else:
				#It's a power card! Let's use it!
				if(card==10):
					return self.drawTwo(state)
				elif(card==11):
					return self.peek(state)
				elif(card==12):
					return self.swap(state)
				else:
					#back of a card or something strange? 
					#push whatever it was onto the discard pile
					state['discard'].append(card)
					pass



		return state

	def peek(self,state):
		'''
			peek:
				The AI chooses its least remembered card and refreshes it's memory of it
			Parameters:
				state, the state of the game

		'''
		#What's the least remembered card of ours?
		i=0
		val=99
		for j in range(len(self.aiCardsMem)):
			if(self.aiCardsMem[j] < val):
				val = self.aiCardsMem[j]
				i = j
		#reset the memory (this is effectively the same as us looking at it)
		self.aiCardsMem[i] = 1.0
		self.actionsToTake = self.actionsToTake + " HAL remembers his " + i + "th card!"

		return state

	def swap(self,state):
		'''
			Swap
				This function simply switches two cards from the player and computers hands
			Parameters:
				state, The state of the game
		'''
		if(self.diff == 0):
			#Choose a random card of the humans and ours and switch em
			humanCard = randint(0,3)
			compCard = randint(0,3)
			tmp = state['playCard'][humanCard]['image']
			state['playCard'][humanCard]['image'] = state['compCard'][compCard]['image']
			state['compCard'][compCard]['image'] = tmp
			#done
		else:
			#We have a difficuly of 1 or 2, which means basic memory decay and swappage
			#Here is our fuzzy memory scheme:
			#The AI has some probability of having NO clue what it's and the users
			#cards are. 
			#So lets get the cards we think we have
			humanCards,compCards = self.getMemory()
			humanCard  = 0
			humanValue = 15
			i=0
			#Look through the cards we remember and find the lowest value
			for c in humanCards:
				if( c < humanValue):
					humanCard = i 
					humanValue = c
				i=i+1
			#Find out highest cards
			compCard = 0
			compValue = 0
			i=0
			for c in compCards:
				if(c > compValue ) :
					compCard = i 
					compValue = c
				i=i+1
			#Update our representation of it (note this propagates remembering wrong)
			tmp = humanCards[humanCard]

			self.realOpCards[humanCard] = compCard[compCard]
			self.opCards = json.dumps(self.realOpCards)
			self.realAiCards[compCard] = tmp
			self.aiCards = json.dumps(self.realAiCards)
			#Now perform the real swap
			tmp = state['playCard'][humanCard]['image']
			state['playCard'][humanCard]['image'] = state['compCard'][compCard]['image']
			state['compCard'][compCard]['image'] = tmp
			#update the memory 
			self.opCardsMem[humanCard],self.aiCardsMem[compCard] = self.aiCardsMem[compCard],self.opCardsMem[humanCard]

		return state

	def alzheimer(self):
		'''
			alzheimer:
				This makes HAL forget his cards as if he had alzheimers 
				(Decrement each remembrance array by the decary rate multiplied by difficulty)
		'''
		#Decrement how much we remember
		for i in range(len(self.opCardsMem)):
			self.opCardsMem[i] = self.opCardsMem[i] - self.diff*self.decayRate
			self.aiCardsMem[i] = self.aiCardsMem[i] - self.diff*self.decayRate
			if(self.opCardsMem[i] < 0):
				self.opCardsMem[i] = 0
			if(self.aiCardsMem[i] < 0):
				self.aiCardsMem[i] = 0

	def getMemory(self):
		'''
			getMemory
				This function uses the probability of rememberance of the AI
				to determine the representations
		'''
		logging.info("made it to HAL's get Memory!!")
		humanRep = [0,0,0,0]
		compRep  = [9,9,9,9]

		aiCards = self.realAiCards
		humanCards = self.realOpCards
		for i in range(len(self.opCardsMem)):
			if(self.opCardsMem[i] < randZ()):
				#Remember correctly
				humanRep[i] = humanCards[i]
			else:
				#Remembered incorrectly
				humanRep[i] = {'image' : str(randint(0,9)), 'active' : 0, 'visible' : 0}
			if(self.aiCardsMem[i] < randZ()):
				#Remembered correctly
				compRep[i] = aiCards[i]
			else:
				#Remembered incorrectly
				compRep[i] = {'image' : str(randint(0,9)), 'active' : 0, 'visible' : 0}
		#Return two things at once #YOLO
		return humanRep,compRep

	def findHighestInHand(self):
		'''
			findHighestInHand
				Finds the highest card in the hand and returns it's index and value
		'''
		#The running max val
		maxVal = 0
		i,j=0,0
		human,aiCards = self.getMemory()
		for c in aiCards:
			if(maxVal < c):
				i=j
				maxVal = c
			j=j+1

		return i,maxVal

	def shouldKnock(self, state):
		'''
			shouldKnock
				Returns true or false if we should try to end the game or not
		'''
		#Get what we remember
		humanCards,aiCards = self.getMemory()
		#Add up the values
		#LAWL human value is nothing! so true!
		humanValue = 0
		compValue = 0
		for c in humanCards:
			humanValue = humanValue + int(c['image'])
		for c in aiCards:
			compValue = compValue + int(c['image'])
		#Now here comes some math
		#Quite frankly, if we just do a comparison that's silly. We'll end the game if the ai
		#by chance believes itself to be in the right when it's really just remembering poorly
		#while this isn't a terrible thing, we still have a pretty good chance that the AI will
		#try to end the game really early (I don't feel like calculating the probabilty, but we 
		# could if we got bored and wanted it on the presentation)
		#The higher the difficulty the more we want to weight it in the AI's favor.
		#So lets do some ratio work shall we?
		if(humanValue/compValue < 1):
			#compValue is larger than the human value but to what degree?
			#If they are close we will be closer to 1, the more towards zero the more confident 
			#the computer is
			if(humanValue/compValue < .75):
				#pretty unsure, what difficult are we on?
				if(self.diff > 1):
					#we're on hard... which means we've got alright memory
					#flip a coin.
					if(  randZ() > humanValue/compValue):
						#Let's knock!
						state['knockState'] = True
				else:
					#We're not on hard, let's do it with some very small probability
					if(randZ() < .15):
						state['knockState'] = True
			elif(humanValue/compValue < .4)	:
				#pretty confident
				if(self.diff > 0):
					#if we're not on easy we'll flip a coid
					if( randZ() > humanValue/compValue):
						#60% chance of knocking
						state['knockState'] = True
			else:
				#we're above 75 we aint knocking.
				pass
		else:
			#The human's cards are more than ours, so we wont knock
			pass
		return state
