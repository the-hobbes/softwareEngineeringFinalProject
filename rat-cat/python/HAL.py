#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Ethan
#
# This file handles the AI logic and database construction
from handler import *

from random import choice
from google.appengine.ext import db
import logging
import json

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

	# def __init__(self,sessionID="Debug",diff=0,aiCardArray=[],opCardArray=[],topValue=9):
	# 	'''
	# 		Constructor
	# 			Creates the HAL instance in the database to keep persistent state. 
	# 		Parameters:
	# 			sessionID, The sessionID to find this instance of computer in the database
	# 			diff, The difficult setting of the AI
	# 				Difficulty of 0 corresponds to random choice
	# 				Difficulty of 1 corresponds to high memory decay rate
	# 				Difficulty of 2 corresponds to low memory decay rate
	# 				Difficulty of 3 corresponds to perfect memory recall (Not selectable by user but for funsies is here)
	# 			aiCardArray, An array of the AI's initial cards
	# 			opCardArray, An array of the opponents initial cards
	# 			topValue, The value of the top card, None if the deck is empty
	# 	'''
	# 	logging.info("Made an instance of HAL")
	# 	self.key_name=sessionID
	# 	self.sessionId=sessionID
	# 	self.estAIScore=36
	# 	self.estOppScore=18
	# 	#HAL does not know the user's cards yet...
	# 	self.opCardsMem=[0.0,0.0,0.0,0.0]
	# 	self.aiCardsMem=[1.0,1.0,1.0,1.0]
	# 	self.opCards=json.dumps(opCardArray)
	# 	self.aiCards=json.dumps(aiCardArray)
	# 	self.discardTopValue=json.dumps(topValue)
	# 	self.decayRate = 0.0 #use some equation of difficult (probs 1/e^diff and some stuff)
	# 	self.decayMemory = [1.0,1.0,1.0,1.0]

	# 	#Store this AI into the database to along with this session
	# 	#https://groups.google.com/forum/?fromgroups=#!topic/google-appengine/iX2fEjv5jsM ... uh
	# 	db.Model.__init__(self,key_name=sessionID,sessionId=sessionID,estAIScore=self.estAIScore,estOppScore=self.estOppScore,opCardsMem=self.opCardsMem,aiCardsMem=self.aiCardsMem,opCards=self.opCards,aiCards=self.aiCards,discardTopValue=self.discardTopValue,decayRate=self.decayRate,decayMemory=self.decayMemory)
	# 	self.put()

	def testMe(self):
		logging.info("Test Satisfactory")




		