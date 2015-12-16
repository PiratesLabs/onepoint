import webapp2
from handlers.web import WebRequestHandler
from auth import login_required
from model.store import Store
import json
import logging

class AppliancesPage(WebRequestHandler):
    @login_required
    def get(self):
        role = self.session['role']
        fb_id = self.session['fb_id']
        store = Store.all().filter(role + ' =', fb_id).get()
        print(store)
        path = 'appliances.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class ApplianceDetailsPage(WebRequestHandler):
    def get(self):
        path = 'appliance_details.html'
        details = [
            {
                'name':'MANUFACTURER',
                'value':'Frymaster'
            },
            {
                'name':'MODEL',
                'value':'FM102'
            },
            {
                'name':'SERIAL NUMBER',
                'value':'EGY674489GHTY76'
            },
            {
                'name':'LAST REPAIR DATE',
                'value':'7/2/2015'
            },
            {
                'name':'INSTALLED ON',
                'value':'6/1/2010'
            },
            {
                'name':'WARRANTY',
                'value':'Expired 6/1/2013'
            }
        ]
        template_values = {'details':details}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/appliance/list', AppliancesPage)
    ]
)