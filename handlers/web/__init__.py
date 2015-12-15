import webapp2
from .web_request_handler import WebRequestHandler
from .index import IndexPage, GenerateQRCodePage, QRCodePage, AppliancePage, ScanQRCodePage
from django import template

app = webapp2.WSGIApplication([
    ('/scan_qr_code', ScanQRCodePage),
    ('/generate_qr_code', GenerateQRCodePage),
    ('/qr_code', QRCodePage),
    ('/appliance', AppliancePage),
    ('/', IndexPage)
])