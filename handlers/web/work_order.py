import webapp2
from handlers.web import WebRequestHandler
from auth import provider_login_required, login_required
from model.provider import Provider
from model.work_order import WorkOrder
from model.appliance import Appliance
from util.util import get_work_orders_for_logged_in_user
import json
import logging

class EstimateHandler(WebRequestHandler):
    def get(self):
        path = 'work_order_estimate.html'
        template_values = {'work_order':self['work_order']}
        self.write(self.get_rendered_html(path, template_values), 200)

class CompletedHandler(WebRequestHandler):
    @login_required
    def get(self):
        path = 'work_order_completed.html'
        template_values = {'work_order':self['work_order']}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProviderCheckinHandler(WebRequestHandler):
    @login_required
    def get(self):
        path = 'provider_checkin.html'
        template_values = {'work_order':self['work_order']}
        self.write(self.get_rendered_html(path, template_values), 200)

class ListHandler(WebRequestHandler):
    @login_required
    def get(self):
        path = 'workorders.html'
        wo_id = str(self['work_order']) if self['work_order'] else ''
        new_wo = str(self['new_wo']) if self['new_wo'] else ''
        workorders = get_work_orders_for_logged_in_user(self)
        template_values = {'workorders': [(wo, wo.get_action_url(self.session['role'])) for wo in workorders], 'count': len(workorders)}
        if wo_id:
            template_values['active_wo'] = wo_id
        if new_wo:
            template_values['new_wo'] = new_wo
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/work_order/provide_estimate', EstimateHandler),
        ('/work_order/checkin_provider', ProviderCheckinHandler),
        ('/work_order/completed',CompletedHandler),
        ('/work_order/list',ListHandler)
    ]
)