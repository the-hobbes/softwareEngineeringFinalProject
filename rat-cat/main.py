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

import webapp2
from python.game import *
from python.scores import *
from python.playerinfo import *
from python.difficulty import *
from python.characterchoice import *
import os
import jinja2
import re
from google.appengine.ext import db

#set templating directory with jinja. NOTE that jinja escapes html because autoescape = True
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	'''
		Class Handler 
		This class inherits from RequestHandler. It is used to simplify writing and rendering to templates by providing
		simpler methods to use in order to do such operations. 
		For example, in other classes which implement this Handler, rendering data to a template can be accomplished by 
		the following statement:
			self.render(template, keyvalue pairs)
		as opposed to the following: 
			self.write(self.render_str(template, keyvalue pairs))
		params: inherits from RequestHandler
	'''
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		#called by render_front in MainPage class
		self.write(self.render_str(template, **kw))

class MasterControlProgram(Handler):
	'''
		Class MasterControlProgram
		Inherits from the Handler class to facilitate writing to templates. 
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
	('/playerinfo',PlayerInfoHandler),
	('/difficulty',DifficultyHandler),
	('/characterchoice',CharacterHandler)
], debug=True)
