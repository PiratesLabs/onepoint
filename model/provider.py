from google.appengine.ext import db

class Provider(db.Model):
    name = db.StringProperty(indexed=False)
    owner = db.ReferenceProperty()
    phone_num = db.StringProperty(indexed=True)
    insurance = db.StringProperty(indexed=False)
    certifications = db.StringProperty(indexed=False)
    reputation = db.FloatProperty(indexed=False)
