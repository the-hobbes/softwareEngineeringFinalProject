#!/usr/bin/env python
# Created 5MAR2013 
# Authors:
# 	Ceberio, Bryan
# 
# This handler contains the datastore classes for storing data input.

import datetime
from handler import *
from google.appengine.ext import db

class Players(db.Model):
	'''
		Players
		Datastore entity for Players. Used to record relevent player information. Inherits from db.Model
	'''
	# playerID = db.StringProperty(required=True)

	# player specific information
	name = db.StringProperty(required=True)
	age = db.IntegerProperty()
	joinDate = db.DateTimeProperty(auto_now_add=True)
	sessionId = db.StringProperty()
	avatar = db.StringProperty()

	# statistics gathering information
	games = db.IntegerProperty(default=0)
	gamesWon = db.IntegerProperty(default=0)
	gamesLost = db.IntegerProperty(default=0)
	roundsTotal = db.IntegerProperty(default=0)
	roundsWonTotal = db.IntegerProperty(default=0)
	roundsLostTotal = db.IntegerProperty(default=0)
	scoreTotal = db.IntegerProperty(default=0)

class Games(db.Model):
	'''
		Games
		Datastore entity for Games. Used to record relevent game information. Inherits from db.Model
	'''
	# gameID = db.IntegerProperty(required=True)
	# Players_playerID = db.StringProperty()
	gameStart = db.DateTimeProperty(auto_now_add=True)
	win = db.BooleanProperty()
	score = db.IntegerProperty(default=0)
	rounds = db.IntegerProperty(default=0)

	# foreign key
	sessionId = db.StringProperty()
	difficulty = db.StringProperty()