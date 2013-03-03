#!/usr/bin/env python
# Created 3MAR2013 
# Authors:
# 	Phelan
# 
# This handler facilitates choosing the player character. It renders a template that allows the user to choose one of 6 
# characters, and then forwards the user to the next screen with that information. 

from handler import *

class CharacterHandler(Handler):
	def get(self):
		'''
			get
			Standard get method. Renders template.
		'''
		self.render("choosePlayer.html")
	
	def post(self):
		'''
			post
			Standard post method. Collects posted form information.
		'''
		radioAnswer = self.request.get("characterGroup")
		self.write(radioAnswer)