#!/usr/bin/env python
# Created 5MAR2013 
# Authors:
# 	Phelan
# 
# This handler displays the top ten scores, and performs all of the associated database calls to do so.

from handler import *
from datastore import *
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
		players = db.GqlQuery(
			"SELECT * FROM Players "
			"ORDER BY scoreTotal ASC LIMIT 10"
		)
		self.render("scores.html", players = players)