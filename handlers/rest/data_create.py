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
        Member(key_name='niranjan.salimath@gmail.com', name='Niranjan Salimath', role='manager').put()
        Member(key_name='aiyappa@b-eagles.com', name='Aiyappa', role='owner').put()

    def create_stores(self):
        store = Store(name="Store1", location=db.GeoPt(40.7131116,-74.015359), manager="niranjan.salimath@gmail.com", owner="aiyappa@b-eagles.com")
        store.put()
        return [store]

    def create_appliances(self, store_ids):
        for store in store_ids:
            Appliance(name="Fryer1", store=store).put()
            Appliance(name="Fryer2", store=store).put()
            Appliance(name="Fryer3", store=store).put()
            Appliance(name="Oven1", store=store).put()
            Appliance(name="Oven2", store=store).put()
            Appliance(name="Oven3", store=store).put()

    def get(self):
        self.create_users()
        store_ids = self.create_stores()
        self.create_appliances(store_ids)

app = webapp2.WSGIApplication([
    ('/rest/create/store', StoreCreationHandler),
    ('/rest/create/appliance', ApplianceCreationHandler),
    ('/rest/create/setup_testdata', TestDataCreationHandler),
])