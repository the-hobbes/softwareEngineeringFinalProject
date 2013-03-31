#!/usr/bin/env python
# Created 3MAR2013 
# Authors:
# 	Ethan
# 
# This handler facilitates choosing the player character. It renders a template that allows the user to choose one of 6 
# characters, and then forwards the user to the next screen with that information. 

from handler import *

class UnitHarness(Handler):
	'''
		UnitHarness
		Inherits from handler. Used to respond to http requests for the /unit url
		Performs basic Unit tests on each python file. Generates statistics and information for each
	'''
	#Array to hold information about tests. Will
	tests=[{"name" :"Unit Test Harness", "passed" : True, "message" : "Test harness has been called correctly"}]

	def get(self):
		'''
			get
			Standard get method. Renders template.
		'''
		self.render("unit.html",tests=self.tests)
	