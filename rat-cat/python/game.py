#!/usr/bin/env python

import webapp2

class GameHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello game!')

