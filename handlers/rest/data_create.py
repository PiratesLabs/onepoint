import webapp2
import urllib2
import json
from model.member import Member
from model.store import Store
from handlers.web.web_request_handler import WebRequestHandler
from google.appengine.ext import db

class StoreCreationHandler(WebRequestHandler):
    def post(self):
        loc = self['location'].split(',')
        store = Store()
        store.name = self['name']
        store.location = db.GeoPt(loc[0], loc[1])
        store.manager = self['manager']
        store.owner = self['owner']
        store.put()

app = webapp2.WSGIApplication([
    ('/rest/create/store', StoreCreationHandler)
])