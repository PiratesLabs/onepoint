from google.appengine.ext import db

class Store(db.Model):
    name = db.StringProperty(indexed=True)
    location = db.GeoPtProperty(indexed=True)
    manager = db.StringProperty(indexed=True)
    owner = db.StringProperty(indexed=True)
    address = db.StringProperty(indexed=False)
    billing_address = db.StringProperty(indexed=False)
