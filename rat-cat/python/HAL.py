#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Ethan
#
# This file handles the AI logic and database construction
from handler import *

from random import choice
from google.appengine.ext import db

ENDGAME_SCORE = 60

class HAL(db.Model):
	#Estimates used in decision calculations
	estAIScore = db.IntegerProperty(required=True)
	estOppScore = db.IntegerProperty(required=True)
	#CSV for memory values 
	opCardsMem = db.StringProperty(required=True)
	aiCardsMem = db.StringProperty(required=True)
	#CSV for the actual card values we know
	aiCards = db.StringProperty(required=True)
	discardTopValue = db.IntegerProperty(required=True)
	#difficulty level 0-3 (3 being perfect recall)
	difficulty = db.IntegerProperty(required=True)
	#Memory decay


