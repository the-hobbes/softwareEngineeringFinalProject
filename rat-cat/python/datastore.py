#!/usr/bin/env python
# Created 5MAR2013 
# Authors:
# 	Ceberio, Bryan
# 
# This handler contains the datastore classes for storing data input.

import datetime
from handler import *
from google.appengine.ext import db

# Database table for Players
class Players(db.Model):
	playerID = db.IntegerProperty(required=True)
	name = db.StringProperty()
	age = db.IntegerProperty()
	joinDate = db.DateTimeProperty(auto_now_add=True)
	games = db.FloatProperty()
	gamesWon = db.FloatProperty()
	gamesLost = db.FloatProperty()
	roundsTotal = db.FloatProperty()
	roundsWonTotal = db.FloatProperty()
	roundsLostTotal = db.FloatProperty()
	scoreTotal = db.FloatProperty()
	catCardsTotal = db.IntegerProperty()
	ratCardsTotal = db.IntegerProperty()
	powerCardsTotal = db.IntegerProperty()

# Database table for Games
class Games(db.Model):
    gameID = db.IntegerProperty(required=True)
    Players_playerID = db.IntegerProperty()
    gameStart = db.DateTimeProperty(auto_now_add=True)
    win = db.BooleanProperty()
    score = db.FloatProperty()
    rounds = db.FloatProperty()
    roundsWon = db.FloatProperty()
    roundsLost = db.FloatProperty()
    catCards = db.IntegerProperty()
    ratCards = db.IntegerProperty()
    powerCards = db.IntegerProperty()