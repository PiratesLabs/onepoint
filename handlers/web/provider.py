import webapp2
from handlers.web import WebRequestHandler
from auth import login_required
from model.provider import Provider
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
        template_values = {'details':provider.template_format,'name':provider.name, 'ratings':[x for x in range(1,6)], 'schedule_repair_url':provider.schedule_repair_url}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProviderScheduleRepairPage(WebRequestHandler):
    @login_required
    def get(self):
        path = 'provider_schedule_repair.html'
        provider = Provider.get_by_id(long(self['id']))
        appliances = get_appliances_for_logged_in_user(self)
        appliance_array = [(appliance.id, appliance.name) for appliance in appliances]
        details = [
            {
                'name':'provider',
                'value':provider.name,
                'id':provider.id,
                'readonly':'readonly'
            },
            {
                'name':'appliance',
                'value':'Choose Appliance',
                'appliances':appliance_array,
                'readonly':''
            },
            {
                'name':'appliance_serial',
                'value':'Appliance Serial Number',
                'readonly':'readonly'
            },
            {
                'name':'appliance_manufacturer',
                'value':'Appliance Manufacturer',
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
        priorities = ['High', 'Medium', 'Low']
        template_values = {'details':details,'name':'WORK ORDER #12-345', 'ratings':[x for x in range(1,6)], 'details_url':provider.details_url, 'priorities':priorities}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/provider/list', ProvidersPage),
        ('/provider/details',ProviderDetailsPage),
        ('/provider/schedule_repair', ProviderScheduleRepairPage)
    ]
)