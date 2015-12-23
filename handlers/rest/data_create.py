import webapp2
import urllib2
import json
from model.member import Member
from model.store import Store
from model.appliance import Appliance
from model.provider import Provider
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
        Member(key_name='niranjan.salimath@gmail.com', name='Niranjan Salimath', role='owner').put()
        Member(key_name='rsalimath@gmail.com', name='Rajiv Salimath', role='manager').put()
        Member(key_name='ranju@b-eagles.com', name='Ranju Salimath', role='provider').put()

    def create_stores(self):
        store = Store(name="Store1", location=db.GeoPt(40.7131116,-74.015359), manager="rsalimath@gmail.com", owner="niranjan.salimath@gmail.com")
        store.put()
        return [store]

    def create_appliances(self, store_ids):
        for store in store_ids:
            Appliance(name="Fryer1", store=store, manufacturer="Frymaster", model="FM102", serial_num="EGY1909334569", last_repair_date="7/2/2015", installed_on="6/1/2010", warranty="Expired 6/1/2013").put()
            Appliance(name="Fryer2", store=store, manufacturer="Frymaster", model="FM102", serial_num="EGY1909334569", last_repair_date="7/2/2015", installed_on="6/1/2010", warranty="Expired 6/1/2013").put()
            Appliance(name="Fryer3", store=store, manufacturer="Frymaster", model="FM102", serial_num="EGY1909334569", last_repair_date="7/2/2015", installed_on="6/1/2010", warranty="Expired 6/1/2013").put()
            Appliance(name="Oven1", store=store, manufacturer="Frymaster", model="FM102", serial_num="EGY1909334569", last_repair_date="7/2/2015", installed_on="6/1/2010", warranty="Expired 6/1/2013").put()
            Appliance(name="Oven2", store=store, manufacturer="Frymaster", model="FM102", serial_num="EGY1909334569", last_repair_date="7/2/2015", installed_on="6/1/2010", warranty="Expired 6/1/2013").put()
            Appliance(name="Oven3", store=store, manufacturer="Frymaster", model="FM102", serial_num="EGY1909334569", last_repair_date="7/2/2015", installed_on="6/1/2010", warranty="Expired 6/1/2013").put()

    def clear_datastore(self):
        models = [Member, Store, Appliance, Provider]
        for model in models:
            q = model.all(keys_only=True)
            entries = q.fetch(100)
            db.delete(entries)

    def create_providers(self):
        Provider(name="Acme Oven Services", location=db.GeoPt(40.719510, -74.008930), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Cool Air Conditioning", location=db.GeoPt(40.720030, -74.007052), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Chesapeake HVAC Services", location=db.GeoPt(40.721266, -74.009627), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="O'Mally Ventilation Repairs", location=db.GeoPt(40.716948, -74.007814), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="A1 Oven Servies", location=db.GeoPt(40.715143, -74.011022), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Clean City Services", location=db.GeoPt(40.719542, -74.005700), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Excel Air Conditioning", location=db.GeoPt(40.717038, -74.008887), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Hardys Appliance Repairs", location=db.GeoPt(40.721193, -74.014434), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Oakgrove Oven Services", location=db.GeoPt(40.724043, -74.009989), owner=Member.get_by_key_name("ranju@b-eagles.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()

    def get(self):
        self.clear_datastore()
        self.create_users()
        store_ids = self.create_stores()
        self.create_appliances(store_ids)
        self.create_providers()

app = webapp2.WSGIApplication([
    ('/rest/create/store', StoreCreationHandler),
    ('/rest/create/appliance', ApplianceCreationHandler),
    ('/rest/create/setup_testdata', TestDataCreationHandler),
])