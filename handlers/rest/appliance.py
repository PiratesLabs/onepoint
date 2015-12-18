import webapp2
import urllib2
import json
import logging
from model.appliance import Appliance
from handlers.web.web_request_handler import WebRequestHandler

class ApplianceDetailsHandler(WebRequestHandler):
    def post(self):
        id = self['id']
        appliance = Appliance.get_by_id(long(id))
        logging.info(appliance.name)
        self.write(json.dumps({'appliance':{'serial':appliance.serial_num,'manufacturer':appliance.manufacturer}}),
                   content_type = 'application/json')

app = webapp2.WSGIApplication([
    ('/rest/appliance/get', ApplianceDetailsHandler)
])