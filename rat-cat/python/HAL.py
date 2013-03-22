#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Ethan
#
# This file handles the AI logic and database construction
from handler import *

from random import choice
from google.appengine.ext import db


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
	estAIScore = db.IntegerProperty(required=True)
	estOppScore = db.IntegerProperty(required=True)
	#CSV for memory values 
	opCardsMem = db.StringProperty(required=True)
	aiCardsMem = db.StringProperty(required=True)
	#CSV for the actual card values we know
	opCards = db.StringProperty(required=True)
	aiCards = db.StringProperty(required=True)
	discardTopValue = db.IntegerProperty(required=True)
	#Memory decay rate, abs and rounded between 0.01-.99
	decayRate = db.FloatProperty(required=True)
	#decayMemory CSV, represents chance of remembering correctly
	decayMemory = StringProperty(required=True)
	#Statics to log?

	def __init__(self,sessionID="Debug",diff=0,aiCardArray=[]):
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
		'''









