# Created 3MAR2013 
# Authors:
# 	Phelan
# 
# This base handler provides much of the basic libraries used by the other handlers, as well as a Handler class which 
# facilitates an easier method for rendering content to jinja templates. 
# This is done so you can just import this handler file instead of writing the import, template, and Handler information each
# time

import webapp2
import os
import jinja2
import re
from google.appengine.ext import db

#set templating directory with jinja. NOTE that jinja escapes html because autoescape = True
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = False)

class Handler(webapp2.RequestHandler):
	'''
		Class Handler 
		This class inherits from RequestHandler. It is used to simplify writing and rendering to templates by providing
		simpler methods to use in order to do such operations. 
		For example, in other classes which implement this Handler, rendering data to a template can be accomplished by 
		the following statement:
			self.render(template, keyvalue pairs)
		as opposed to the following: 
			self.write(self.render_str(template, keyvalue pairs))
		params: inherits from RequestHandler
	'''
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def renderStr(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		#called by render_front in MainPage class
		self.write(self.renderStr(template, **kw))