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


class Games(db.Model):
	'''
		Games
		Datastore entity for Games. Used to record relevent game information. Inherits from db.Model
	'''
	# gameID = db.IntegerProperty(required=True)
	# Players_playerID = db.StringProperty()
	gameStart = db.DateTimeProperty(auto_now_add=True)
	win = db.BooleanProperty()
	score = db.FloatProperty()
	rounds = db.FloatProperty()
	roundsWon = db.FloatProperty()
	roundsLost = db.FloatProperty()
	catCards = db.IntegerProperty()
	ratCards = db.IntegerProperty()
	powerCards = db.IntegerProperty()

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