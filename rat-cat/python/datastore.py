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
	games = db.FloatProperty(default=0.0)
	gamesWon = db.FloatProperty(default=0.0)
	gamesLost = db.FloatProperty(default=0.0)
	roundsTotal = db.FloatProperty(default=0.0)
	roundsWonTotal = db.FloatProperty(default=0.0)
	roundsLostTotal = db.FloatProperty(default=0.0)
	scoreTotal = db.FloatProperty(default=0.0)
	catCardsTotal = db.IntegerProperty(default=0)
	ratCardsTotal = db.IntegerProperty(default=0)
	powerCardsTotal = db.IntegerProperty(default=0)


class Games(db.Model):
	'''
		Games
		Datastore entity for Games. Used to record relevent game information. Inherits from db.Model
	'''
	# gameID = db.IntegerProperty(required=True)
	# Players_playerID = db.StringProperty()
	gameStart = db.DateTimeProperty(auto_now_add=True)
	win = db.BooleanProperty()
	score = db.FloatProperty(default=0.0)
	rounds = db.FloatProperty(default=0.0)
	roundsWon = db.FloatProperty(default=0.0)
	roundsLost = db.FloatProperty(default=0.0)
	catCards = db.IntegerProperty(default=0)
	ratCards = db.IntegerProperty(default=0)
	powerCards = db.IntegerProperty(default=0)

	# foreign key
	sessionId = db.StringProperty()
	difficulty = db.StringProperty()

# New Code
class MyHandler(Handler):

	# Returns top ten players from datastore and renders them to scores HTML page
	def get(self):
		players = db.GqlQuery(
			"SELECT * FROM Players "
			"ORDER BY scoreTotal DESC LIMIT 10"
		)
		values = {'players': players}

		self.response.out.write(
			template.render('scores.html',
				values)
		)
	
	# Retrieves input values for player name and total score
	# Inputs player into datastore
	# Refreshes the scores HTML page

	def post(self):
		player = Players(
			name = self.request.get('name'),
			scoreTotal = float(self.request.get('scoreTotal'))
		)
		player.put()
		self.redirect('/scores')