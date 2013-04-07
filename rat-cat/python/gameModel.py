#!/usr/bin/env python
# Created 7APR2013 
# Authors:
# 	Phelan
# This handler is responsible for interacting with the datastore and returning manipulated data (model in MVC framework).

from handler import *
import logging

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
		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.roundsTotal += 1
			result.put()

	def updatePlayerScore(self, pScore):
		'''
			updatePlayerScore
			Adds the player's score for the round to the running total in the datastore.
			Parameters:
				pScore, the player's score for the round
		'''
		results = db.GqlQuery("SELECT * FROM Players WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			result.scoreTotal = result.scoreTotal + pScore
			result.put()

	def getTotalGameScore(self):
		'''
			getTotalGameScore
			Used to retrieve the total score for the game so far. This method must query the game database to retrieve the 
			score for the current game.
			Returns:
				totalGameScore, the total score for the game so far. 
		'''
		results = db.GqlQuery("SELECT * FROM Games WHERE sessionId = :sess", sess=self.sessionId)
		for result in results:
			totalScore = result.score

		return totalScore

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
