#!/usr/bin/env python
# Created 5MAR2013 
# Authors:
# 	Ceberio, Bryan
# 
# This handler contains the datastore classes for storing data input.

from handler import *
from google.appengine.ext import db
import logging

#from google.appengine.ext import webapp
from google.appengine.ext.webapp \
	import template

# Database table for Players
class Players(db.Model):
	# playerID = db.IntegerProperty(required=True)
	name = db.StringProperty(required=True)
	scoreTotal = db.FloatProperty()
	age = db.IntegerProperty()
	joinDate = db.DateTimeProperty(auto_now_add=True)
	games = db.FloatProperty()
	gamesWon = db.FloatProperty()
	gamesLost = db.FloatProperty()
	roundsTotal = db.FloatProperty()
	roundsWonTotal = db.FloatProperty()
	roundsLostTotal = db.FloatProperty()
	catCardsTotal = db.IntegerProperty()
	ratCardsTotal = db.IntegerProperty()
	powerCardsTotal = db.IntegerProperty()

# Database table for Games
class Games(db.Model):
    # gameID = db.IntegerProperty(required=True)
    Players_playerID = db.StringProperty()
    gameStart = db.DateTimeProperty(auto_now_add=True)
    win = db.BooleanProperty()
    score = db.FloatProperty()
    rounds = db.FloatProperty()
    roundsWon = db.FloatProperty()
    roundsLost = db.FloatProperty()
    catCards = db.IntegerProperty()
    ratCards = db.IntegerProperty()
    powerCards = db.IntegerProperty()

class MyHandler(Handler):

	def get(self):
		players = db.GqlQuery(
			"SELECT * FROM Players "
			"ORDER BY scoreTotal DESC LIMIT 10"
		)
		games = db.GqlQuery(
			"SELECT * FROM Games"
		)
		values = {'players': players, 'games': games}

		self.response.out.write(
			template.render('scores.html',
				values)
		)

	def post(self):
		player = Players(
			name=self.request.get('name'),
			scoreTotal=float(self.request.get('scoreTotal')
		)
		game = Games(
			Players_playerID = player.key()
		)
		game.score = 20.0
		game.win = True

		if game.win == True: player.gamesWon = 1
		else: player.gamesLost = 1
		'''
		# Datastore query test to see if a player has input a name that already exists in the database
		players = Players.all()
		name = player.name
		players.filter("name = ", name)
		result = players.get()
		if player.name == result:
			self.response.out.write("Sorry, that username has already been taken!")
		else:
		'''
			player.scoreTotal += game.score
			player.put()
		game.put()
		
		self.redirect('/scores')