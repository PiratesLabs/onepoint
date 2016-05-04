import webapp2
import urllib2
import urllib
import json
import logging
import airtable_config as airtable
import random
from model.member import Member
from model.work_order import WorkOrder, WorkOrderHistory
from model.store import Store
from model.appliance import Appliance
from model.provider import Provider
from handlers.web.web_request_handler import WebRequestHandler
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import urlfetch

obj_map = {}

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
        manager = Member(key_name='manager@americangrid.com', name='Jose Martinez', role='manager', phone='(410)-245-7053')
        manager2 = Member(key_name='cpshankar@me.com', name='CP Shankar', role='manager', phone='(410)-245-7053')
        owner.put()
        manager.put()
        manager2.put()
        return [owner, manager, manager2]

    def create_stores(self, manager2, manager, owner):
        stores = []
        store = Store(name="McDonald's", location=db.GeoPt(40.7131116,-74.015359), manager=manager2.key().name(), owner=owner.key().name(), address="McDonald's, Logn Gate Shopping Center, 4396 Montgomery Rd, Ellicott City, MD 21043", billing_address="Brdancat Enterprises, Inc., 9107 Mendenhall Ct., Unit B, Columbia, MD 21045")
        store.put()
        stores.append(store)
        store = Store(name="Starbucks", location=db.GeoPt(40.7131116,-83.015359), manager=manager.key().name(), owner=owner.key().name(), address="Starbucks, Shrt Gate Shopping Center, 6392 Gregory Rd, Kingston City, NV 52552", billing_address="Fieldcat Enterprises, Inc., 1822 Radcliffe St., Unit B, Durby, DL 62611")
        store.put()
        stores.append(store)
        store = Store(name="Friendly's", location=db.GeoPt(37.7131116,-96.015359), manager=manager.key().name(), owner=owner.key().name(), address="Friendly's, North Wall Shopping Center, 4319 Desmond St, Riverside, CA 92503", billing_address="Redwood Services, Inc., 6777 Brook Av., Lansing, PA 48912")
        store.put()
        stores.append(store)
        store = Store(name="Hardrock Cafe", location=db.GeoPt(41.4291638,-76.215929), manager=manager.key().name(), owner=owner.key().name(), address="Hardrock Cafe, 100 Broadway, New York City, NY 10001", billing_address="Rose Inc., 4193 Manning Dr., Richmond, VA 23420")
        store.put()
        stores.append(store)
        store = Store(name="Tavern", location=db.GeoPt(40.6192436,-77.819237), manager=manager.key().name(), owner=owner.key().name(), address="Tavern, 297 Clark St., Chicago, IL 60604", billing_address="The Billers, 78 University Rd., Syracuse, NY 13205")
        store.put()
        stores.append(store)
        return stores

    def create_member(self, email, name, phone, role_name):
        member = Member.get_or_insert(key_name = email)
        member.name = name
        member.role = role_name
        member.phone = phone
        member.put()
        return member

def map_address(address):
    if address == '9107 Mendenhall Court, Columbia, MD 21045':
        return db.GeoPt(39.186183, -76.826163)
    elif address == '12011 Guilford Road # 101, Annapolis Junction, MD 20701':
        return db.GeoPt(39.124529, -76.785755)
    elif address == '1595 Cabin Branch Drive, Landover, MD 20785':
        return db.GeoPt(38.913211, -76.905566)
    elif address == '9100 Yellow Brick Road, Suite H, Baltimore, MD 21237':
        return db.GeoPt(39.345803, -76.472525)

def owner_manager_fields_mapper(member, role_name):
    fields = member['fields']
    tdc = TestDataCreationHandler()
    email = fields['Email']
    owner_obj = tdc.create_member(email, fields['Name'], fields['Phone'], role_name)
    obj_map[member['id']] = owner_obj
    return owner_obj

def vendor_mapper(member, role_name):
    fields = member['fields']
    tdc = TestDataCreationHandler()
    provider_obj = Provider.all().filter('airtable_id =', fields['Vendor ID']).get()
    if not provider_obj:
        provider_obj = Provider()
    provider_obj.name = fields['Vendor Name']
    provider_obj.phone_num = fields['Phone - Business Hours']
    dispatch_email = fields['Dispatch Email']
    provider_user = tdc.create_member(dispatch_email, fields['Primary Contact Name'], fields['Phone - Business Hours'], role_name)
    provider_obj.owner = provider_user
    provider_obj.location = map_address(fields['Address'])
    provider_obj.address = fields['Address']
    provider_obj.insurance = 'Hartford insurance'
    provider_obj.certifications = 'Class B Electrician license'
    provider_obj.reputation = 4.0
    provider_obj.airtable_id = fields['Vendor ID']
    provider_obj.put()

def store_mapper(member, role_name):
    fields = member['fields']
    store_obj = Store.all().filter('airtable_id =', fields['Store ID']).get()
    if not store_obj:
        store_obj = Store()
    store_obj.name = fields['Store Name']
    store_obj.location = db.GeoPt(fields['Latitude'],fields['Longitude'])
    store_obj.address = fields['Store Address']
    store_obj.billing_address = fields['Billing Address']
    store_obj.owner = obj_map[fields['Store Owner'][0]].key().name()
    store_obj.manager = obj_map[fields['Store Manager'][0]].key().name()
    store_obj.airtable_id = fields['Store ID']
    store_obj.put()
    obj_map[member['id']] = store_obj

def appliance_mapper(member, role_name):
    fields = member['fields']
    appliance_obj = Appliance.all().filter('airtable_id =', fields['Appliance_Id']).get()
    if not appliance_obj:
        appliance_obj = Appliance()
    appliance_obj.name = fields['Appliance Name'][0]
    appliance_obj.serial_num = fields['Serial #']
    appliance_obj.model = fields['Model #']
    appliance_obj.manufacturer = fields['Manufacturer'][0]
    appliance_obj.store = obj_map[fields['Store'][0]]
    appliance_obj.airtable_id = fields['Appliance_Id']
    appliance_obj.put()

def create_db_object(rel_url, role_name, payload, encoded_payload, headers, fields_mapper):
    url = 'https://api.airtable.com/v0/'+airtable.config['app_id']+'/'+rel_url
    response = urlfetch.fetch(url=url,payload=encoded_payload,method=urlfetch.GET,headers=headers)
    if response.content and 'records' in response.content:
        r = json.loads(response.content)
        members = r['records']
        for member in members:
            fields = member['fields']
            if len(fields) <= 0:
                continue
            fields_mapper(member, role_name)
    logging.info('Done ' + role_name)

def pull_airtable_data():
    logging.info('Starting Airtable Pull')

    payload = {'view': airtable.config['view']}
    encoded_payload = urllib.urlencode(payload)
    headers = {'Authorization': 'Bearer '+airtable.config['api_key'], 'Content-Type': 'application/x-www-form-urlencoded'}

    create_db_object('Owners', 'owner', payload, encoded_payload, headers, owner_manager_fields_mapper)
    create_db_object('Managers', 'manager', payload, encoded_payload, headers, owner_manager_fields_mapper)
    create_db_object('Vendors', 'provider', payload, encoded_payload, headers, vendor_mapper)
    create_db_object('Stores', 'stores', payload, encoded_payload, headers, store_mapper)
    create_db_object('Appliances', 'appliances', payload, encoded_payload, headers, appliance_mapper)

class AirtableDataPullHandler(webapp2.RequestHandler):
    def get(self):
        deferred.defer(pull_airtable_data)

class ClearAirtableDataHandler(webapp2.RequestHandler):
    def get(self):
        clear_datastore()

class FormDataReadHandler(WebRequestHandler):
    def get_appliance_form_date(self, date_name, appliance, appliance_index):
        date = appliance[appliance_index.index(date_name)].split(" ")[0]
        if date == "UNKNOWN" or date == "NA":
            date = ""
        return date

    def post(self):
        tdc = TestDataCreationHandler()
        tdc.create_member(self['owner_email'], self['owner_name'], self['owner_phone'], 'owner')
        tdc.create_member(self['manager_email'], self['manager_name'], self['manager_phone'], 'manager')

        store_obj = Store()
        store_obj.name = self['store_name']
        store_obj.owner = self['owner_email']
        store_obj.manager = self['manager_email']
        store_obj.location = db.GeoPt(self['store_lat'],self['store_long'])
        store_obj.address = self['store_address']
        store_obj.billing_address = self['store_billing_address']
        store_obj.put()

        appliances_csv = self['appliances_csv']
        appliances = appliances_csv.splitlines()
        appliance_index = [index.strip("\"") for index in str(appliances[0]).split(',')]
        for appliance in appliances[1:]:
            appliance = [detail.strip("\"") for detail in str(appliance).split(',')]
            appliance_obj = Appliance()
            appliance_obj.name = appliance[appliance_index.index("Name of Appliance")]
            appliance_obj.serial_num = appliance[appliance_index.index("Serial #")]
            appliance_obj.model = appliance[appliance_index.index("Model #")]
            appliance_obj.manufacturer = appliance[appliance_index.index("Manufacturer Name")]
            appliance_obj.last_repair_date = self.get_appliance_form_date("Last Repair Date (if you know it)", appliance, appliance_index)
            appliance_obj.installed_on = self.get_appliance_form_date("Installed on (if known)", appliance, appliance_index)
            appliance_obj.warranty = self.get_appliance_form_date("Is it in warranty (if known)", appliance, appliance_index)
            appliance_obj.store = store_obj
            appliance_obj.put()


app = webapp2.WSGIApplication([
    ('/rest/create/store', StoreCreationHandler),
    ('/rest/create/appliance', ApplianceCreationHandler),
    ('/rest/create/form_data', FormDataReadHandler),
    ('/rest/create/airtable_data', AirtableDataPullHandler),
    ('/rest/create/clear_airtable_data', ClearAirtableDataHandler)
])