#!/usr/bin/env python
# Created 5MAR2013 
# Authors:
# 	Phelan
# 
# This handler displays the top ten scores, and performs all of the associated database calls to do so.

from handler import *
from google.appengine.ext import db
from datastore import Players
import logging

class ScoresHandler(Handler):
	'''
		ScoresHandler
		Inherits from Handler. Used to respond to requests to the /scores resource.
	'''
	def get(self):
		'''
			get
			Default get method. Called when a user lands on /scores. Used to get the top 10 scores from the database,
			then render the template with those top scores.
		'''
		# topTen, sortedKeys = self.getTopScores()
		# self.renderScores(topTen, sortedKeys)
		players = db.GqlQuery(
			"SELECT * FROM Players "
			"ORDER BY scoreTotal DESC LIMIT 10"
		)
		self.render("scores.html", players = players)

	def getTopScores(self):
		# getTopScores
		# Used to retrieve the top 10 scores from the database. Note that the top 10 will be the top 10 LOWEST scores.

		#note: i am just manufacturing a fake top 10 for testing purposes. Here is where the database call would be made in production
		topTen = {}
		topTen['joe'] = '0'
		topTen['bob'] = '1'
		topTen['pete'] = '2'
		topTen['dan'] = '3'
		topTen['kyle'] = '4'
		topTen['kenny'] = '5'
		topTen['stan'] = '6'
		topTen['cartman'] = '7'
		topTen['bart'] = '8'
		topTen['lisa'] = '9'

		#sort the dictionary by the score
		sortedKeys = topTen.keys()
		sortedKeys.sort(lambda x,y: cmp(topTen[x], topTen[y]))
		
		# for key in sortedKeys:
		# 	self.write(topTen[key])

		return topTen, sortedKeys

	def renderScores(self, topTen, sortedKeys):
		# renderScores
		# Render the scores template with the appropriate list of players as arguments.
		# parameters:
		# topTen, list of the names and scores of the top 10 players, as provided for by the database

		self.render("scores.html", topTen = topTen, sortedKeys = sortedKeys)

	def post(self):
		pass