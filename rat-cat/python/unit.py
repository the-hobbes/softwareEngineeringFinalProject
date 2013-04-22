#!/usr/bin/env python
# Created 3MAR2013 
# Authors:
# 	Ethan
# 
# This is the UnitHarness handler, it handles validating and testing functions
# that we create and want to report on. It also reports interesting statistics 
# and such.

from handler import *
from time import time
import python.scores as ps
import python.playerinfo as pi
import python.HAL as ai
import python.game as gh
import logging
import json
from google.appengine.ext.db import stats

global_stat = stats.GlobalStat.all().get()


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
		self.testPlayerInfo()
		self.testHAL()
		self.testGame()
		totalBytes = 'Total bytes stored: %d' % global_stat.bytes
		totalEntities ='Total entities stored: %d' % global_stat.count
		self.render("unit.html",tests=self.tests,totalBytes=totalBytes,totalEntities=totalEntities)
		

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

	def testPlayerInfo(self):
		'''
			testPlayerInfo
			Tests the playerinfo.py file's validation function
		'''

		test = pi.PlayerInfoHandler()

		passed = True
		message = ""

		name=""
		age=""

		vPass,e = test.validateInput(name,age)
		if(vPass):
			message = message + "Failed to return invalid to empty arguments\n"
			passed = False
		else:
			pass

		name="Fuck"
		age=""

		vPass,e = test.validateInput(name,age)
		if(vPass):
			message = message + "Failed to return invalid to bad age argument\n"
			passed = False
		else:
			pass

		age="0"

		vPass,e = test.validateInput(name,age)
		if(vPass):
			message = message + "Failed to return invalid on profanity check\n"
			passed = False
		else:
			pass

		name="Test"
		
		vPass,e = test.validateInput(name,age)
		if(vPass):
			passed = passed and True
		else:
			message = message + "Failed to return valid on valid input arguments"

		if passed:
			message = "Validation Function working correctly"
		self.addTest("Player Info Validation",passed,message)


	def testHAL(self):
		'''
			testHAL
			Tests the time it takes to place a HAL object into the database
		'''
		sTime = time()
		
		#Calls put inside it's constructor
		test = ai.HAL()

		eTime = time()
		passed = True

		if eTime - sTime > 1:
			passed = False
		self.addTest("HAL Test",passed,"HAL object placed into datastore in %2.5f seconds" % (eTime - sTime))

	def testGame(self):
		'''
			testGame
			Monolithic test function to test game play
		'''
		#Need to figure out a way to test game.py correctly
		#this may mean rigging the deck and stuff and testing
		#each power card and sending it fake user actions and such
		#definitely need to work on this part with phelan somewhere

		test = gh.GameHandler()
		state = False
		
		passed=True
		message=""
		#Initalization Test
		try:
			state = json.loads(test.initEncode())
		except Exception, e:
			message = "Failed to initilize game state JSON " 
			passed = False
		else:
			message = ""
		
		self.addTest("Game Initialize Test",passed,message)
		passed=True
		#div to card translation test
		try:
			cardIndex,cardArray,cardChoice = test.translateDivToCard("playCard1",state)
		except Exception, e:
			message = "Failed to translateDivToCard "
			passed = False
			if not state:
				message = message + " due to unintialized state "
		else:
			if cardIndex != 0:
				passed = False
				message = " cardIndex incorrect <br/>"
			if cardArray != 'playCard':
				passed = False
				message = message + " cardArray return value incorrect <br />"
			if cardChoice['image'] != state['playCard'][0]['image']:
				passed = False
				self.write(cardChoice['image'])
				message = message + " cardChoice incorect <br />"
		
		self.addTest("Translate Div -> Card Test",passed,message)
		passed=True
		#Test on actives
		try:
			state = test.resetActiveFlags(state)
		except Exception, e:
			passed = False
			message = " Failed to reset active flags "
		else:
			for r in state['playCard']:
				if(r['active']==1):
					passed = False
			if not passed:
				message = " Failed to reset active flags "
		
		self.addTest("Reset active Flags Test",passed,message)
		passed=True
		#Testing swap cards
		try:
			card1 = state['playCard'][0]['image']
			card2 = state['compCard'][1]['image']
			state['playerClicks'].append("playerCard1")
			state['playerClicks'].append("compCard2")
			state = test.swapCards("p1","c2",state)
		except Exception, e:
			passed = False
			message =  " recieved error while attempting to execute function error:" + str(e)
		else:
			message =""
			if card1 != state['compCard'][1]['image']:
				passed = False
				message = message + " failed to swap player card 1 with computer card 2 <br />"
			if card2 != state['playCard'][0]['image']:
				passed = False
				message = message + " failed to swap computer card 2 and player card 1 <br />"
		
		self.addTest("Swap Cards Test",passed,message)
		passed=True

		#Waiting for PCard test
		try:
			state['playerClicks'][0] = 'playerCard1'
			oldCard = state['playCard'][0]['image']
			#This unit test will fail if the old card and the discard card is the same
			newCard = state['displayCard']['image']
			state = test.waitingForPCard(state)
		except Exception, e:
			passed = False
			message =  " Error while attempting to use waitingForPCard" + str(e)
		else:
			if state['playCard'][0]['image'] != newCard:
				passed = False
				message = "Failed to swap display and selected card "
		
		self.addTest("waitingForPCard Test",passed,message)
		self.addTest("Game Test",passed,message)
