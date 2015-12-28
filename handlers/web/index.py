import webapp2
from handlers.web import WebRequestHandler
from model.member import Member
import json
import logging

class ScanQRCodePage(WebRequestHandler):
    def get(self):
        path = 'scan_qr_code.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class GenerateQRCodePage(WebRequestHandler):
    def get(self):
        path = 'generate_qr_code.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class QRCodePage(WebRequestHandler):
    def get(self):
        path = 'qr_code.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class IndexPage(WebRequestHandler):
    def fetch_users(self):
        users = Member.all().fetch(100)
        return [u for u in users]

    def get(self):
        session_id = self.session['email'] if 'email' in self.session else None
        if not session_id:
            path = 'landing.html'
            template_values = {'users':self.fetch_users()}
            self.write(self.get_rendered_html(path, template_values), 200)
        else:
            self.redirect('/appliance/list')

app = webapp2.WSGIApplication(
    [
        ('/scan_qr_code', ScanQRCodePage),
        ('/generate_qr_code', GenerateQRCodePage),
        ('/qr_code', QRCodePage),
        ('/', IndexPage)
    ]
)