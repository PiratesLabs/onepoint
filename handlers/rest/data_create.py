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
        Member(key_name='niranjan.salimath@gmail.com', name='Niranjan Salimath', role='manager').put()
        Member(key_name='aiyappa@b-eagles.com', name='Aiyappa', role='owner').put()
        Member(key_name='ashray.test1@gmail.com', name='Ashray Velapanur', role='provider').put()

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

    def clear_datastore(self):
        models = [Member, Store, Appliance, Provider]
        for model in models:
            q = model.all(keys_only=True)
            entries = q.fetch(100)
            db.delete(entries)

    def create_providers(self):
        Provider(name="Acme Oven Services", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Cool Air Conditioning", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Chesapeake HVAC Services", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="O'Mally Ventilation Repairs", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="A1 Oven Servies", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Clean City Services", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Excel Air Conditioning", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Hardys Appliance Repairs", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()
        Provider(name="Oakgrove Oven Services", owner=Member.get_by_key_name("ashray.test1@gmail.com"), phone_num="617-840-0716", insurance="Hartford insurance", certifications="Class B Electrician license", reputation=4.0).put()

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