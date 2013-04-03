#!/usr/bin/env python
# Created 3MAR2013 
# Authors:
# 	Phelan
# 
# This handler facilitates choosing the player character. It renders a template that allows the user to choose one of 6 
# characters, and then forwards the user to the next screen with that information. 

from handler import *

class CharacterHandler(Handler):
	'''
		CharacterHandler
		Inherits from handler. Used to respond to http requests for the /characterchoice url.
	'''
	def get(self):
		'''
			get
			Standard get method. Renders template.
		'''
		self.render("choosePlayer.html")
	
	def post(self):
		'''
			post
			Standard post method. Collects posted form information, adds it to the database and redirects the user to
			the difficulty choice page.
		'''
		radioAnswer = self.request.get("characterGroup")
		sessionId = self.request.get("sessionId")
		
		
		if radioAnswer:
			#add the choice of character to the database
			self.redirect("/difficulty" +"?sessionId=" + sessionId)
		else:
			self.render("choosePlayer.html")