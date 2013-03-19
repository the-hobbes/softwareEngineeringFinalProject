#!/usr/bin/env python
# Created 5MAR2013 
# Authors:
# 	Ceberio, Bryan
# 
# This handler contains the datastore classes for storing data input.

from handler import *
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp \
	import template

# Database table for Players
class Players(db.Model):
	# playerID = db.IntegerProperty(required=True)
	name = db.StringProperty(required=True)
	age = db.IntegerProperty()
	joinDate = db.DateTimeProperty(auto_now_add=True)
	games = db.FloatProperty()
	gamesWon = db.FloatProperty()
	gamesLost = db.FloatProperty()
	roundsTotal = db.FloatProperty()
	roundsWonTotal = db.FloatProperty()
	roundsLostTotal = db.FloatProperty()
	scoreTotal = db.StringProperty()
	catCardsTotal = db.IntegerProperty()
	ratCardsTotal = db.IntegerProperty()
	powerCardsTotal = db.IntegerProperty()

# Database table for Games
class Games(db.Model):
    # gameID = db.IntegerProperty(required=True)
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

class MyHandler(Handler):

	def get(self):
		players = db.GqlQuery(
			'SELECT * FROM Players'
			'ORDER BY scoreTotal DESC LIMIT 10'
		)
		values = {'players': players}

		self.response.out.write(
			template.render('scores.html',
				values)
		)
	
	def post(self):
		player = Players(
			name=self.request.get('name'),
			scoreTotal=self.request.get('scoreTotal')
		)
		player.put()
		self.write(player.name)
		#self.redirect('/')