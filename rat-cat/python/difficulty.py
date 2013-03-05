#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Phelan
# 
# This handler facilitates choosing the difficulty level for the AI. It renders a template that allows the user to choose one 
# of 3 levels (easy, medium, and hard) to be used by the game. This is the last bit of information to be collected from the user 
# before the game begins

from handler import *

class DifficultyHandler(Handler):
	'''
		DifficultyHandler
		Inherits from handler. Used to respond to http requests for the /difficulty url.
	'''
	def get(self):
		'''
			get
			Standard get method. Renders template.
		'''
		self.render("selectDifficulty.html")

	def post(self):
		'''
			post
			Standard post method. Relevent information is pulled from the post request and processed. The user is forwarded to the next stage (the actual game)
			if all is well.
		'''
		difficulty = self.request.get("difficultyGroup")
		if difficulty:
			#add the difficulty to the database
			self.redirect("/game")
		else:
			self.render("selectDifficulty.html")