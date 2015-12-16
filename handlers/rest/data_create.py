import webapp2
import urllib2
import json
from model.member import Member
from model.store import Store
from model.appliance import Appliance
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

class ApplianceCreationHandler(WebRequestHandler):
    def post(self):
        app = Appliance()
        app.name = self['name']
        app.store = self['store']
        app.put()

class TestDataCreationHandler(WebRequestHandler):
    def create_users(self):
        Member(key_name='585110577', name='Niranjan Salimath', email='niranjan.salimath@gmail.com').put()
        Member(key_name=user_deets['id'], name=user_deets['name'], email=user_deets['email']).put()
    def get(self):
        self.create_users()

app = webapp2.WSGIApplication([
    ('/rest/create/store', StoreCreationHandler),
    ('/rest/create/appliance', ApplianceCreationHandler),
    ('/rest/setup_testdata', TestDataCreationHandler)
])