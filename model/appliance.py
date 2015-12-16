from google.appengine.ext import db

class Appliance(db.Model):
    name = db.StringProperty(indexed=False)
    store = db.ReferenceProperty(indexed=False)

