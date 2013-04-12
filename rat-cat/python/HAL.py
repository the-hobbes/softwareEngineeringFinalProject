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
import python.gameModel as gm


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
	estAIScore = db.IntegerProperty()
	estOppScore = db.IntegerProperty()
	#list for memory values 
	opCardsMem = db.ListProperty(float)
	aiCardsMem = db.ListProperty(float)
	#list for the actual card values we know
	opCards = db.StringProperty(str)
	aiCards = db.StringProperty(str)
	discardTopValue = db.StringProperty()
	#Memory decay rate, abs and rounded between 0.01-.99
	decayRate = db.FloatProperty()
	#decayMemory list, represents chance of remembering correctly
	decayMemory = db.ListProperty(float)
	#This will be a string that builds up to tell the view what to do
	actionsToTake = ""
	diff =0

	def __init__(self,sessionID="Debug",diff=0,aiCardArray=[],opCardArray=[],topValue=9):
		'''
			Constructor
				Creates the HAL instance in the database to keep persistent state. 
			Parameters:
				sessionID, The sessionID to find this instance of computer in the database
				diff, The difficult setting of the AI
					Difficulty of 0 corresponds to random choice
					Difficulty of 1 corresponds to high memory decay rate
					Difficulty of 2 corresponds to low memory decay rate
					Difficulty of 3 corresponds to perfect memory recall (Not selectable by user but for funsies is here)
				aiCardArray, An array of the AI's initial cards
				opCardArray, An array of the opponents initial cards
				topValue, The value of the top card, None if the deck is empty
		'''

		self.key_name=sessionID
		self.pkSessionID=sessionID
		self.estAIScore=36
		self.estOppScore=18
		#HAL does not know the user's cards yet...
		self.opCardsMem=[0.0,0.0,0.0,0.0]
		self.aiCardsMem=[1.0,1.0,1.0,1.0]
		self.opCards=json.dumps(opCardArray)
		self.aiCards=json.dumps(aiCardArray)
		self.discardTopValue=json.dumps(topValue)
		self.decayRate = 0.0 #use some equation of difficult (probs 1/e^diff and some stuff)
		self.decayMemory = [1.0,1.0,1.0,1.0]

		#Store this AI into the database to along with this session
		#https://groups.google.com/forum/?fromgroups=#!topic/google-appengine/iX2fEjv5jsM ... uh
		db.Model.__init__(self,key_name=sessionID,pkSessionID=sessionID,estAIScore=self.estAIScore,estOppScore=self.estOppScore,opCardsMem=self.opCardsMem,aiCardsMem=self.aiCardsMem,opCards=self.opCards,aiCards=self.aiCards,discardTopValue=self.discardTopValue,decayRate=self.decayRate,decayMemory=self.decayMemory)
		self.put()

	def rememberTopCard(self,topCard):
		'''
		rememberTopCard
			topCard, The top card of the deck to be remembered
		'''
		self.discardTopValue = topCard

	def doTurn(self,state):
		'''
		Does the HAL's turn, this function is essentially a way for the AI to keep

		'''
		pass

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
		self.aiCardsMem[i] = 1

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
		elif(self.diff == 3):
			#Perfect Recall of all cards that it knows. This is mean
			humanCard  = 0
			humanValue = 15
			i=0
			#Look through the cards we remember and find the lowest value
			for c in self.opCards:
				if( int(c['image']) < humanValue):
					humanCard = i 
					humanValue = int(c['image'])
				i=i+1
			#Find out highest cards
			compCard = 0
			compValue = 0
			i=0
			for c in self.aiCards:
				if(int(c['image']) > compValue ) :
					compCard = i 
					compValue = int(c['image'])
				i=i+1
			#Now that we know, we perform the swap
			tmp = state['playCard'][humanCard]['image']
			state['playCard'][humanCard]['image'] = state['compCard'][compCard]['image']
			state['compCard'][compCard]['image'] = tmp
			#Update our representation of the cards
			tmp = self.opCards[humanCard]
			self.opCards[humanCard] = self.aiCards[compCard]
			self.aiCards[compCard] = tmp
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
				if( int(c['image']) < humanValue):
					humanCard = i 
					humanValue = int(c['image'])
				i=i+1
			#Find out highest cards
			compCard = 0
			compValue = 0
			i=0
			for c in compCards:
				if(int(c['image']) > compValue ) :
					compCard = i 
					compValue = int(c['image'])
				i=i+1
			#Update our representation of it (note this propagates remembering wrong)
			tmp = humanCards[humanCard]
			self.opCards[humanCard] = compCard[compCard]
			self.aiCards[compCard] = tmp
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
		humanRep = [0,0,0,0]
		compRep  = [9,9,9,9]
		for i in range(len(self.opCardsMem)):
			if(self.opCardsMem[i] < randZ()):
				#Remember correctly
				humanRep[i] = self.opCards[i]
			else:
				#Remembered incorrectly
				humanRep[i] = {'image' : str(randint(0,9)), 'active' : 0, 'visible' : 0}
			if(self.aiCardsMem[i] < randz()):
				#Remembered correctly
				compRep[i] = self.aiCards[i]
			else:
				#Remembered incorrectly
				compRep[i] = {'image' : str(randint(0,9)), 'active' : 0, 'visible' : 0}
		#Return two things at once #YOLO
		return humanRep,compRep






















