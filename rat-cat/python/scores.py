#!/usr/bin/env python
import webapp2

class ScoresHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello scores!')

