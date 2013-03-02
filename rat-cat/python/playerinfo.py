#!/usr/bin/env python

import webapp2

class PlayerInfoHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello player info!')