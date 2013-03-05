#!/usr/bin/env python
# Created 4MAR2013 
# Authors:
# 	Phelan
# 
# This handler executes the actual game environment. 
from handler import *

class GameHandler(Handler):
	'''
		GameHandler
		Main handler for rendering game elements in the templating system. Responds to get and post requests for the game url. Inherits from Hander for easy
		template rendering.
	'''
	def get(self):
		'''
		get
		You got your basic get method right here.
		'''
		self.render("game.html")

	def post(self):
		'''
		post
		Responds to post requests for the resource.
		'''
		self.write("You posted. Good for you.")

