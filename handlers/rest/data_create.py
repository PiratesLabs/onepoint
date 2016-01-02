import webapp2
import urllib2
import urllib
import json
import logging
import airtable_config as airtable
from model.member import Member
from model.work_order import WorkOrder, WorkOrderHistory
from model.store import Store
from model.appliance import Appliance
from model.provider import Provider
from handlers.web.web_request_handler import WebRequestHandler
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import urlfetch

def clear_datastore():
    models = [Member, Store, Appliance, Provider, WorkOrder, WorkOrderHistory]
    for model in models:
        q = model.all(keys_only=True)
        entries = q.fetch(100)
        db.delete(entries)

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
        owner = Member(key_name='owner@americangrid.com', name='Brandon Bell', role='owner', phone='(617)-840-0716')
        manager = Member(key_name='manager@americangrid.com', name='Jose Martinez', role='manager', phone='(617)-840-0716')
        owner.put()
        manager.put()
        return [owner, manager]

    def create_stores(self, manager, owner):
        store = Store(name="Store1", location=db.GeoPt(40.7131116,-74.015359), manager=manager.key().name(), owner=owner.key().name(), address="40 Harrison Street, New York, NY, United States")
        store.put()
        return [store]

    def create_provider(self, email, name, phone):
        provider = Member(key_name = email, name = name, role = 'provider', phone = phone)
        provider.put()
        return provider

def map_address(address):
    if address == '9107 Mendenhall Court, Columbia, MD 21045':
        return db.GeoPt(39.186183, -76.826163)
    elif address == '12011 Guilford Road # 101, Annapolis Junction, MD 20701':
        return db.GeoPt(39.124529, -76.785755)
    elif address == '1595 Cabin Branch Drive, Landover, MD 20785':
        return db.GeoPt(38.913211, -76.905566)
    elif address == '9100 Yellow Brick Road, Suite H, Baltimore, MD 21237':
        return db.GeoPt(39.345803, -76.472525)

def pull_airtable_data():
    tdc = TestDataCreationHandler()
    [owner, manager] = tdc.create_users()
    [store] = tdc.create_stores(manager, owner)

    payload = {'view': airtable.config['view']}
    encoded_payload = urllib.urlencode(payload)
    headers = {'Authorization': 'Bearer '+airtable.config['api_key'], 'Content-Type': 'application/x-www-form-urlencoded'}

    url = 'https://api.airtable.com/v0/'+airtable.config['app_id']+'/Appliances'
    response = urlfetch.fetch(url=url,payload=encoded_payload,method=urlfetch.GET,headers=headers)
    if response.content and 'records' in response.content:
        r = json.loads(response.content)
        appliances = r['records']
        for appliance in appliances:
            appliance_obj = Appliance()
            fields = appliance['fields']
            if len(fields) <= 0:
                continue
            appliance_obj.name = fields['Appliance Name'][0]
            appliance_obj.serial_num = fields['Serial #']
            appliance_obj.model = fields['Model #']
            appliance_obj.manufacturer = fields['Manufacturer'][0]
            appliance_obj.store = store
            appliance_obj.put()
    
    url = 'https://api.airtable.com/v0/'+airtable.config['app_id']+'/Vendors'
    response = urlfetch.fetch(url=url,payload=encoded_payload,method=urlfetch.GET,headers=headers)
    if response.content and 'records' in response.content:
        r = json.loads(response.content)
        providers = r['records']
        provider_user = tdc.create_provider('provider@americangrid.com', 'C.P', '(617)-840-0716')
        for provider in providers:
            provider_obj = Provider()
            fields = provider['fields']
            if len(fields) <= 0:
                continue
            provider_obj.name = fields['Vendor Name']
            provider_obj.phone_num = fields['Phone - Business Hours']
            dispatch_email = fields['Dispatch Email'] if 'Dispatch Email' in fields else 'rajiv@beagleslabs.com'
            #provider_user = tdc.create_provider(dispatch_email, fields['Primary Contact Name'], fields['Phone - Business Hours'])
            provider_obj.owner = provider_user
            provider_obj.location = map_address(fields['Address'])
            provider_obj.address = fields['Address']
            provider_obj.insurance = 'Hartford insurance'
            provider_obj.certifications = 'Class B Electrician license'
            provider_obj.reputation = 4.0
            provider_obj.put()

class AirtableDataPullHandler(webapp2.RequestHandler):
    def get(self):
        clear_datastore()
        deferred.defer(pull_airtable_data)

app = webapp2.WSGIApplication([
    ('/rest/create/store', StoreCreationHandler),
    ('/rest/create/appliance', ApplianceCreationHandler),
    ('/rest/create/airtable_data', AirtableDataPullHandler)
])