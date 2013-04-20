#!/usr/bin/env python
# Created 7APR2013 
# Authors:
# 	Phelan
# This handler is responsible for interacting with the datastore and returning manipulated data (model in MVC framework).

from handler import *
import logging
from python.datastore import *
from python.HAL import *
from google.appengine.api.datastore import Key

class DatastoreInteraction():
	'''
		Class DatastoreInteraction
		Instances of this class are created to handle interaction with the datastore. The various methods of this model perform
		the tasks required by the game controller. 
	'''
	# class variable session ID 
	sessionId = ""

	def __init__(self, sessionIDIn):
		'''
			Default Constructor
		'''
		logging.info("Made an instance of the DatastoreInteraction")
		self.sessionId = sessionIDIn

	def setSessionId(self, newSessionId):
		'''
			setSessionId
			Setter for sessionID
			Parameters:
				newSessionId, the sessionID to update to.
		'''
		self.sessionId = newSessionId

	def getSessionId(self):
		'''
			getSessionId
			Getter for session ID.
			Returns:
				sessionId, the unique session ID
		'''
		return self.sessionId

	def getAvatar(self):
		'''
			getAvatar
			Used to retrieve the avatar from the database, by sessionID.
			Parameters:
				sessionID, the unique id identifying the session.
			Return:
				avatar, a string representign the avatar pulled from the datastore
		'''

		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			avatar = result.avatar
		logging.info(avatar)

		return avatar

	def updateRoundsWonTotal(self):
		'''
			updateRoundsWonTotal
			Used to increment the datastore field roundsWonTotal by 1. Called when a player wins a round. This will also update
			the fact that a player has played another round (in addition to winning it)
		'''
		logging.info("got to update rounds won!")

		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.roundsWonTotal += 1
			result.roundsTotal += 1
			result.put()

	def updateRoundsLostTotal(self):
		'''
			updateRoundsLostTotal
			Used to increment the datastore field roundsLostTotal by 1. Called when a player wins a round. This will also update
			the fact that a player has played another round (in addition to losing it)
		'''
		logging.info("got to update rounds lost!")

		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.roundsLostTotal += 1
			result.roundsTotal += 1
			result.put()

	def updateRoundsPlayedTotal(self):
		'''
			updateRoundsPlayedTotal
			Used to increment the datastore field roundsTotal by 1. Called when a game results in a tie, or the rounds need to
			be incremented for some reason.
		'''
		logging.info("got to rounds played total")
		
		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.roundsTotal += 1
			logging.info(result.roundsTotal)
			result.put()

	def updatePlayerScore(self, pScore):
		'''
			updatePlayerScore
			Adds the player's score for the round to the running total in the datastore.
			Parameters:
				pScore, the player's score for the round
		'''
		logging.info("got to update player score!")
		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.scoreTotal = result.scoreTotal + pScore
			result.put()

	def updateComputerScore(self, cScore):
		'''
			updateComputerScore
			Adds the computer's score for the round to the running total in the datastore.
			Parameters:
				cScore, the computer's score for the round
		'''
		logging.info("got to update computer score!")
		results = db.GqlQuery("SELECT * FROM Games WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.halScore = result.halScore + cScore
			result.put()

	def getTotalGameScore(self):
		'''
			getTotalGameScore
			Used to retrieve the total score for the game so far. This method must query the game database to retrieve the 
			score for the current game.
			Returns:
				totalGameScore, the total score for the game so far. 
		'''
		logging.info("got to get total game score!")
		results = db.GqlQuery("SELECT * FROM Games WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			playerScore = result.score
			computerScore = result.halScore

		return playerScore, computerScore

	def updateGameScore(self, pScore):
		'''
			updateGameScore
			Used to update the game table with the current score of the game. 
			Parameters:
				pScore, the score to be added to the total.
		'''
		results = db.GqlQuery("SELECT * FROM Games WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.score = result.score + pScore
			result.put()

	def updateGameWin(self):
		'''
			updateGameWin
			Used to update the game table with the boolean value of win. 
		'''
		results = db.GqlQuery("SELECT * FROM Games WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.win = True
			result.put()

		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.games += 1
			result.gamesWon += 1
			result.put()

	def updateGameLose(self):
		'''
			updateGameWin
			Used to update the game table with the boolean value of lose. 
		'''
		results = db.GqlQuery("SELECT * FROM Games WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.win = False
			result.put()

		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.games += 1
			result.gamesLost += 1
			result.put()
		
	def updateGameRounds(self):
		'''
			updateGameRounds
			Used to keep track of the number of rounds in a game.
		'''
		results =  db.GqlQuery("SELECT * FROM Games WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.rounds += 1
			result.put()

	def getDifficulty(self):
		'''
			getDifficulty
			Retrieve the difficulty from the datastore
		'''
		results =  db.GqlQuery("SELECT * FROM Games WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			difficulty = result.difficulty

		return difficulty

	def getHAL(self):
		'''
			getHAL
			Used to keep retrieve all of the information about hal from the datastore.
			Returns:
				halDict, a dictionary containing k/v pairs of all in information in the datastore relevent to HAL.
		'''
		logging.info("Made it to get HAL")
		# retrieve HAL object from datastore
		# logging.info(self.sessionId)
		
		query = db.GqlQuery("SELECT * FROM HAL WHERE pkSessionID = :sess", sess=self.sessionId)
		lists = query.fetch(10) 
		key = lists[0].key()
		logging.info("this is the key:")
		logging.info(key)

		# SELECT * FROM YourModel WHERE __key__ = KEY('YourModel',1)
		results = db.GqlQuery("SELECT * FROM HAL WHERE __key__ = :sess", sess=key)
		# logging.info(self.sessionId)
		# logging.info(results[0].pkSessionID)
		for result in results:
			pkSessionID = result.pkSessionID
			opCardsMem = result.opCardsMem
			opCards = result.opCards
			estOppScore = result.estOppScore
			estAIScore = result.estAIScore
			discardTopValue = result.discardTopValue
			decayRate = result.decayRate
			# decayMemory = result.decayMemory
			aiCardsMem = result.aiCardsMem
			aiCards = result.aiCards

		# retrieve difficulty from datastore 
		difficulty = self.getDifficulty()
		# logging.info(difficulty)
		halDict = {'pkSessionID':pkSessionID, 'opCardsMem':opCardsMem, 'opCards':opCards, 'estOppScore':estOppScore, 'estAIScore':estAIScore, 'discardTopValue':discardTopValue, 'decayRate':decayRate, 'aiCardsMem':aiCardsMem, 'aiCards':aiCards, 'difficulty':difficulty}

		return halDict

	def updateAiCards(self, opCards, aiCards):
		'''
			updateAiCards
			Used to update the HAL datastore entity with the current card set of the player and computer.
			Parameters:
				opcards, the cards the player has (opcards because the player is the opponent of HAL) 
				aiCards, the cards of the AI itself
		'''
		logging.info("Made it to updateAiCards")
		
		query = db.GqlQuery("SELECT * FROM HAL WHERE pkSessionID = :sess", sess=self.sessionId)
		lists = query.fetch(10) 
		key = lists[0].key()
		logging.info("this is the key:")
		logging.info(key)

		results = db.GqlQuery("SELECT * FROM HAL WHERE __key__ = :sess", sess=key)
		for result in results:
			logging.info(result.opCards)
			result.opCards = opCards
			logging.info(result.aiCards)
			result.aiCards = aiCards
			result.put()
	
	def testMe(self):
		logging.info("Test Satisfactory")


