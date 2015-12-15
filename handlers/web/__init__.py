import webapp2
from .web_request_handler import WebRequestHandler
from .index import IndexPage
from django import template

app = webapp2.WSGIApplication([
    ('/', IndexPage)
])