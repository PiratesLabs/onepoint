import webapp2
from handlers.web import WebRequestHandler
from auth import login_required
from model.provider import Provider
from model.appliance import Appliance
from util.util import convert_to_tabbed_format, get_appliances_for_logged_in_user
import json
import logging

class ProvidersPage(WebRequestHandler):
    def load_manager_view(self):
        providers = [provider for provider in Provider.all().fetch(100)]
        path = 'providers.html'
        markers = [[provider.name, provider.location.lat,provider.location.lon] for provider in providers]
        template_values = {'providers':providers,'count':len(providers),'markers':markers}
        self.write(self.get_rendered_html(path, template_values), 200)

    @login_required
    def get(self):
        role = self.session['role']
        if role == 'owner' or role == 'manager':
            self.load_manager_view()

class ProviderDetailsPage(WebRequestHandler):
    @login_required
    def get(self):
        path = 'provider_details.html'
        provider = Provider.get_by_id(long(self['id']))
        appliance_id = self['appliance_id']
        schedule_repair_url = provider.schedule_repair_url
        schedule_repair_url = schedule_repair_url + '&appliance_id='+ appliance_id if appliance_id else schedule_repair_url
        template_values = {'details':provider.template_format,'name':provider.name, 'ratings':[x for x in range(1,6)], 'schedule_repair_url':schedule_repair_url}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProviderScheduleRepairPage(WebRequestHandler):
    @login_required
    def get(self):
        path = 'provider_schedule_repair.html'
        provider = Provider.get_by_id(long(self['id']))
        appliance = Appliance.get_by_id(long(self['appliance_id']))
        details = [
            {
                'name':'provider',
                'title':'Provider',
                'value':provider.name,
                'id':provider.id,
                'readonly':'readonly'
            },
            {
                'name':'appliance',
                'title':'Appliance',
                'value':appliance.name,
                'readonly':'readonly'
            },
            {
                'name':'appliance_serial',
                'title':'Serial Number',
                'value':appliance.serial_num,
                'readonly':'readonly'
            },
            {
                'name':'appliance_manufacturer',
                'title':'Manufacturer',
                'value':appliance.manufacturer,
                'readonly':'readonly'
            },
            {
                'name':'fix_by',
                'value':'Select date',
                'title':'Fix by date',
                'type':'date',
                'readonly':''
            },
            {
                'name':'remarks',
                'value':'',
                'title':'Remarks',
                'readonly':''
            }
        ]
        priorities = ['Critical', 'Normal', 'Routine']
        template_values = {'details':details,'name':'New Work Order', 'ratings':[x for x in range(1,6)], 'priorities':priorities, 'appliance_id':self['appliance_id']}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/provider/list', ProvidersPage),
        ('/provider/details',ProviderDetailsPage),
        ('/provider/schedule_repair', ProviderScheduleRepairPage)
    ]
)