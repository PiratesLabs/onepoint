import webapp2
import urllib2
import json
from model.work_order import WorkOrder
from handlers.web.web_request_handler import WebRequestHandler

class CreateWorkOrderHandler(WebRequestHandler):
    @login_required
    def get(self):
        
        wo = WorkOrder()
        wo.update_state({'appliance':self['appliance'], 'provider':self['provider']})

app = webapp2.WSGIApplication([
    ('/rest/work_order/create', CreateWorkOrderHandler)
])