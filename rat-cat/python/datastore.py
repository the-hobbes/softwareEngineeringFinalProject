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
	# playerID = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	age = db.IntegerProperty()
	joinDate = db.DateTimeProperty(auto_now_add=True)
	games = db.IntegerProperty()
	gamesWon = db.IntegerProperty()
	gamesLost = db.IntegerProperty()
	roundsTotal = db.IntegerProperty()
	roundsWonTotal = db.IntegerProperty()
	roundsLostTotal = db.IntegerProperty()
	scoreTotal = db.IntegerProperty()
	catCardsTotal = db.IntegerProperty()
	ratCardsTotal = db.IntegerProperty()
	powerCardsTotal = db.IntegerProperty()

# Database table for Games
class Games(db.Model):
	# gameID = db.IntegerProperty(required=True)
	Players_playerID = db.StringProperty()
	gameStart = db.DateTimeProperty(auto_now_add=True)
	win = db.BooleanProperty()
	score = db.IntegerProperty()
	rounds = db.IntegerProperty()
	roundsWon = db.IntegerProperty()
	roundsLost = db.IntegerProperty()
	catCards = db.IntegerProperty()
	ratCards = db.IntegerProperty()
	powerCards = db.IntegerProperty()

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
			template.render('scores.html', values)
		)
	# Post method for inputting a player into the datastore
	def post(self):
		p = Players(
			name = self.request.get('name'),
			scoreTotal = int(self.request.get('scoreTotal'))
		)
		'''
		BEGIN Check for same name in datastore
		players = db.GqlQuery("SELECT * FROM Players")
		for player in players:
			if player.name == p.name:
				self.response.write('Sorry, that name has already been taken!')
			else:
				p.put()
				self.redirect('/scores')
		END Check for same name in datastore
		'''
		p.put()
		self.redirect('/scores')