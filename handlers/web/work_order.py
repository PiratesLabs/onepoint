import webapp2
from handlers.web import WebRequestHandler
from auth import provider_login_required
from model.provider import Provider
import json
import logging

class EstimateHandler(WebRequestHandler):
    @provider_login_required
    def get(self):
        path = 'work_order_estimate.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/work_order/provide_estimate', EstimateHandler)
    ]
)