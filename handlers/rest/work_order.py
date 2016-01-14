import webapp2
import urllib2
import json
from model.work_order import WorkOrder
from model.store import Store
from model.appliance import Appliance
from handlers.web.web_request_handler import WebRequestHandler
from auth import login_required

class CreateWorkOrderHandler(WebRequestHandler):
    def does_user_own_appliance(self):
        email = self.session['email']
        role = self.session['role']
        store = Store.all().filter(role + ' =', email).get()
        appliance = Appliance.get_by_id(long(self['appliance']))
        if appliance.store.key().id() == store.key().id():
            return True
        return False

    @login_required
    def get(self):
        ret_val = {}
        if(self.does_user_own_appliance()):
            wo = WorkOrder()
            wo.update_state({'fix_by': self['fix_by'], 'appliance':self['appliance'], 'provider':self['provider'], 'remarks':self['remarks'], 'priority':self['priority']}, self.session['role'])
            ret_val = {'status':'success','work_order_id':wo.key().id()}
        else:
            ret_val = {'status':'error','message':'User does not own the appliance'}
        self.write(json.dumps(ret_val))

class UpdateWorkOrderHandler(WebRequestHandler):
    @login_required
    def post(self):
        wo = WorkOrder.get_by_id(long(self['work_order']))
        ret_val = {}
        params = {}
        if self['params']:
            params_str = self['params']
            entry_strs = params_str.split(';')
            for entry_str in entry_strs:
                entry = entry_str.split(':')
                params[entry[0]] = entry[1]
        ret_val = wo.update_state(params, self.session['role'])
        self.write(json.dumps(ret_val))

class CancelWorkOrderHandler(WebRequestHandler):
    @login_required
    def post(self):
        wo = WorkOrder.get_by_id(long(self['work_order']))
        wo.cancel()
        self.write(json.dumps({'status':'success'}))

class EstimateWorkOrderHandler(WebRequestHandler):
    def post(self):
        wo = WorkOrder.get_by_id(long(self['work_order']))
        print(self['params'])
        ret_val = wo.estimate(self['approval'], self['params'])
        self.write(json.dumps(ret_val))

app = webapp2.WSGIApplication([
    ('/rest/work_order/create', CreateWorkOrderHandler),
    ('/rest/work_order/update', UpdateWorkOrderHandler),
    ('/rest/work_order/cancel', CancelWorkOrderHandler),
    ('/rest/work_order/estimate', EstimateWorkOrderHandler)
])