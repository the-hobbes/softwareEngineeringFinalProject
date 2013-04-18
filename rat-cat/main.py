#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created 1MAR2013 
# Authors:
# 	Ethan, Phelan
# 
# This is the main app driver file. Requests will hit here when users first enter the page
from python.handler import *
from python.game import *
from python.scores import *
from python.scoreinfo import *
from python.playerinfo import *
from python.difficulty import *
from python.characterchoice import *
from python.HAL import *
from python.unit import *

class MasterControlProgram(Handler):
	'''
		Class MasterControlProgram
		Inherits from the Handler class (in python directory) to facilitate writing to templates. 
		Used to handle all http requests for the root of the site. 
	'''
	def get(self):
		'''
			Method get
			Used to respond to html get requests. Calls render landing, which performs template rendering for the 
			landing page.
		'''
		self.renderLanding()

	def renderLanding(self):
		'''
			Method renderLanding
			Used to render the landing page template. This is a separate function from Get because we are building in the
			capacity for expansion as the project grows, and it is better to modify a self defined method to handle different behavior
			than the builtin Get method.
		'''
		self.render("landing.html")

app = webapp2.WSGIApplication([
	('/', MasterControlProgram),
	('/game',GameHandler),
	('/scores',ScoresHandler),
	('/scoreinfo',ScoreInfoHandler),
	('/playerinfo',PlayerInfoHandler),
	('/difficulty',DifficultyHandler),
	('/characterchoice',CharacterHandler),
	('/unit',UnitHarness)
], debug=True)