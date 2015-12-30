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
        store = Store.all().filter(role + ' =', email).get()
        appliances = [appliance for appliance in Appliance.all().filter('store =', store).fetch(100)]
        path = 'appliances.html'
        template_values = {'appliances':appliances, 'count':len(appliances)}
        self.write(self.get_rendered_html(path, template_values), 200)

class ApplianceDetailsPage(WebRequestHandler):
    def get(self):
        path = 'appliance_details.html'
        appliance = Appliance.get_by_id(long(self['id']))
        template_values = {'details':appliance.template_format,'name':appliance.name,'schedule_repair_url':appliance.schedule_repair_url}
        self.write(self.get_rendered_html(path, template_values), 200)

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
        template_values = {'details':details,'name':'WORK ORDER #12-345', 'details_url':appliance.details_url, 'priorities':priorities}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/appliance/list', AppliancesPage),
        ('/appliance/details', ApplianceDetailsPage),
        ('/appliance/schedule_repair', ApplianceScheduleRepairPage)
    ]
)