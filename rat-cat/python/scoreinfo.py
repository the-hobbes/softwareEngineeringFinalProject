#!/usr/bin/env python
# Created 5MAR2013 
# Authors:
# 	Phelan
# 
# This handler displays the player's game information, and performs all of the associated database calls to do so.

from handler import *
from datastore import Players
import cgi
import logging
import json
import re;
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class ScoreInfoHandler(Handler):
	def post(self):
		'''
			POST method to return a player's score information, one that exists within the database.
		'''
		players = db.GqlQuery("SELECT * FROM Players WHERE name = :name", name=self.request.get("name"))
		thumbnailImage = ""
		name = False
		error = "Invalid username!"
		
		for player in players:
			avatar = player.avatar
			name = True
			if(avatar == "character1"):
				thumbnailImage = "bettyThumb.png"
			elif(avatar == "character2"):
				thumbnailImage = "jasonThumb.png"
			elif(avatar == "character3"):
				thumbnailImage = "batRatThumb.png"
			elif(avatar == "character4"):
				thumbnailImage = "catLadyThumb.png"
			elif(avatar == "character5"):
				thumbnailImage = "lebowsCatThumb.png"
			else:
				thumbnailImage = "tommyCatThumb.png"
		
		if name:
			self.render("scoreInfo.html", players=players, thumbnailImage=thumbnailImage, name=name)
		else:
			self.render("scores.html", error=error)