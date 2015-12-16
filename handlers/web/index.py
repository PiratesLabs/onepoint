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

class AppliancesPage(WebRequestHandler):
    def get(self):
        path = 'appliances.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProvidersPage(WebRequestHandler):
    def get(self):
        path = 'providers.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

class ApplianceDetailsPage(WebRequestHandler):
    def get(self):
        path = 'appliance_details.html'
        details = [
            {
                'name':'MANUFACTURER',
                'value':'Frymaster'
            },
            {
                'name':'MODEL',
                'value':'FM102'
            },
            {
                'name':'SERIAL NUMBER',
                'value':'EGY674489GHTY76'
            },
            {
                'name':'LAST REPAIR DATE',
                'value':'7/2/2015'
            },
            {
                'name':'INSTALLED ON',
                'value':'6/1/2010'
            },
            {
                'name':'WARRANTY',
                'value':'Expired 6/1/2013'
            }
        ]
        template_values = {'details':details}
        self.write(self.get_rendered_html(path, template_values), 200)

class ProviderDetailsPage(WebRequestHandler):
    def get(self):
        path = 'provider_details.html'
        details = [
            {
                'name':'OWNER',
                'value':'Mike Mason'
            },
            {
                'name':'EMAIL',
                'value':'mike@acmesvcs.com'
            },
            {
                'name':'PHONE NUMBER',
                'value':'(202) 531-4576'
            },
            {
                'name':'INSURANCE',
                'value':'Hartford Insurance, Expires January 13, 2017'
            },
            {
                'name':'CERTIFICATIONS',
                'value':'Class B Electrician License, Expires October 23, 2018'
            },
            {
                'name':'REPUTATION',
                'value':''
            }
        ]
        template_values = {'details':details}
        self.write(self.get_rendered_html(path, template_values), 200)

class IndexPage(WebRequestHandler):
    def get(self):
        path = 'landing.html'
        template_values = {}
        self.write(self.get_rendered_html(path, template_values), 200)

app = webapp2.WSGIApplication(
    [
        ('/scan_qr_code', ScanQRCodePage),
        ('/generate_qr_code', GenerateQRCodePage),
        ('/qr_code', QRCodePage),
        ('/appliances', AppliancesPage),
        ('/providers', ProvidersPage),
        ('/appliance_details', ApplianceDetailsPage),
        ('/provider_details', ProviderDetailsPage),
        ('/', IndexPage)
    ]
)