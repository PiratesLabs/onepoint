import webapp2
from handlers.web import WebRequestHandler
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
    def get(self):
        session_id = self.session['email'] if 'email' in self.session else None
        if not session_id:
            path = 'landing.html'
            template_values = {}
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