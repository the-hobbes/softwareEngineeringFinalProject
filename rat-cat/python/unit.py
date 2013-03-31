#!/usr/bin/env python
# Created 3MAR2013 
# Authors:
# 	Ethan
# 
# This handler facilitates choosing the player character. It renders a template that allows the user to choose one of 6 
# characters, and then forwards the user to the next screen with that information. 

from handler import *
from time import time
import python.scores as ps

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
		self.tests=[{"name" :"Unit Test Harness", "passed" : True, "message" : "Test harness has been called correctly"}]
		self.testScores()
		self.render("unit.html",tests=self.tests)
		

	def addTest(self,name,passed=False,message="No Message Set"):
		self.tests.append({"name" : name, "passed" : passed, "message" : message})

	def testScores(self):
		'''
			testScores
			Tests the scores.py file's Handler's methods
		'''

		test = ps.ScoresHandler()

		#Retrieve the top scores
		#use clock() on windows, time() on nix
		sTime = time()
		eTime = 0.0
		try:
			topTen,sortKey = test.getTopScores()
			eTime = time()
		except Exception, e:
			self.addTest("scores.py", False, "Failed to retrieve top scores")
		else:
			self.addTest("scores.py", True, "Retrieved top scores in %2.5f seconds " % (eTime - sTime))

		#We can't really call render methods because those will cause
		#the gae to die.
		


	