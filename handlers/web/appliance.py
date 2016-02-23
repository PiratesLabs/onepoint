import webapp2
from handlers.web import WebRequestHandler
from auth import login_required
from model.store import Store
from model.appliance import Appliance
from model.provider import Provider
from util.util import convert_to_tabbed_format
import json
import logging

class AppliancesPage(WebRequestHandler):
    @login_required
    def get(self):
        email = self.session['email']
        role = self.session['role']
        stores = Store.all().filter(role + ' =', email).order('name')
        store_appliances = []
        for store in stores:
            appliances = [appliance for appliance in Appliance.all().filter('store =', store).fetch(100)]
            store_appliances.append((store,appliances))
        path = 'appliances.html'
        template_values = {'store_appliances':store_appliances, 'count':len(store_appliances)}
        self.write(self.get_rendered_html(path, template_values), 200)

class ApplianceDetailsPage(WebRequestHandler):
    def get(self):
        path = 'appliance_details.html'
        appliance = Appliance.get_by_id(long(self['id']))
        template_values = {'details':appliance.template_format,'name':appliance.name,'select_provider_url':appliance.select_provider_url,'store_name':appliance.store.name}
        self.write(self.get_rendered_html(path, template_values), 200)

class ApplianceSelectProviderPage(WebRequestHandler):
    def load_manager_view(self, appliance_id):
        providers = [provider for provider in Provider.all().fetch(100)]
        path = 'select_provider.html'
        markers = [[provider.name, provider.location.lat,provider.location.lon] for provider in providers]
        appliance = Appliance.for_id(long(appliance_id))
        store_name = appliance.store.name if appliance else ''
        template_values = {'providers':providers,'count':len(providers),'markers':markers, 'appliance_id':appliance_id, 'store_name':store_name}
        self.write(self.get_rendered_html(path, template_values), 200)

    @login_required
    def get(self):
        role = self.session['role']
        if role == 'owner' or role == 'manager':
            appliance_id = self['id']
            self.load_manager_view(appliance_id)

class ApplianceScheduleRepairPage(WebRequestHandler):
    @login_required
    def get(self):
        path = 'appliance_schedule_repair.html'
        appliance = Appliance.for_id(long(self['id']))
        providers = Provider.all().fetch(100)
        provider_array = [(provider.id, provider.name) for provider in providers]
        details = [
            {
                'name':'appliance',
                'value':appliance.name,
                'id':appliance.id,
                'readonly':'readonly'
            },
            {
                'name':'provider',
                'value':'Choose Provider',
                'providers':provider_array,
                'readonly':''
            },
            {
                'name':'provider_owner',
                'value':'Provider Owner',
                'readonly':'readonly'
            },
            {
                'name':'provider_phone',
                'value':'Provider Phone Number',
                'readonly':'readonly'
            },
            {
                'name':'fix_by',
                'value':'Fix by date',
                'type':'date',
                'readonly':''
            },
            {
                'name':'remarks',
                'value':'Remarks',
                'readonly':''
            }
        ]
        priorities = ['Critical', 'Normal', 'Routine']
        template_values = {'details':details,'name':'New Work Order', 'details_url':appliance.details_url, 'priorities':priorities}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/appliance/list', AppliancesPage),
        ('/appliance/details', ApplianceDetailsPage),
        ('/appliance/select_provider', ApplianceSelectProviderPage),
        ('/appliance/schedule_repair', ApplianceScheduleRepairPage)
    ]
)