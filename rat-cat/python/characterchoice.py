#!/usr/bin/env python

import webapp2

class CharacterHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello character choice!')