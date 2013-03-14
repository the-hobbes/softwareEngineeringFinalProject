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
		You got your basic get method right here, but with a twist. 
		This method perfoms the intialization of the game state, creating the json objects that represent the game and
		json encoding them. It then renders them on the game template with jinja. 
		'''
		self.render("game.html")
		#do the encoding
		#for the initial, pass in null for the oldstate
		#in the template, var gamestate = new JSONOBJECT({{{the object}}})
		#render(gamestate)

	def post(self):
		'''
		post
		Responds to post requests for the resource.
		'''
		self.write("You posted. Good for you.")