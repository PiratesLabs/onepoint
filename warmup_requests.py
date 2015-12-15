import webapp2
from handlers.request_handler import RequestHandler

class WarmupHandler(RequestHandler):
    def get(self):
        pass

app = webapp2.WSGIApplication([('/_ah/warmup', WarmupHandler)])

