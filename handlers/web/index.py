import webapp2
from handlers.web import WebRequestHandler
import json
import logging

class IndexPage(WebRequestHandler):
    def get(self):
        path = 'landing.html'
        template_values = {}
        self.render_template(template_name=path, template_values=template_values)

app = webapp2.WSGIApplication(
    [
    ]
)