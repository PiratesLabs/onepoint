import webapp2
from handlers.web import WebRequestHandler
from auth import login_required
from model.store import Store
from model.appliance import Appliance
from util.util import convert_to_grid_format
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
        appliances_dict = convert_to_grid_format(appliances, ['starred', 'newest', 'oldest'])
        template_values = {'appliances':appliances_dict}
        self.write(self.get_rendered_html(path, template_values), 200)

class ApplianceDetailsPage(WebRequestHandler):
    def get(self):
        path = 'appliance_details.html'
        appliance = Appliance.get_by_id(long(self['id']))
        template_values = {'details':appliance.template_format,'name':appliance.name}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/appliance/list', AppliancesPage),
        ('/appliance/details', ApplianceDetailsPage)
    ]
)