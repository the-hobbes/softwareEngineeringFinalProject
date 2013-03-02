#!/usr/bin/env python

import webapp2

class DifficultyHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello difficulty choice!')