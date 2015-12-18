import webapp2
import urllib2
import json
import logging
from model.provider import Provider
from model.member import Member
from handlers.web.web_request_handler import WebRequestHandler

class ProviderDetailsHandler(WebRequestHandler):
    def post(self):
        id = self['id']
        provider = Provider.get_by_id(long(id))
        owner = provider.owner.name if provider else ''
        phone = provider.phone_num if provider else ''
        self.write(json.dumps({'provider':{'owner':owner,'phone':phone}}),
                   content_type = 'application/json')

app = webapp2.WSGIApplication([
    ('/rest/provider/get', ProviderDetailsHandler)
])