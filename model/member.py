from google.appengine.ext import db

class Member(db.Model):
    name = db.StringProperty(indexed=False)
    email = db.StringProperty(indexed=True)
    role = db.StringProperty(indexed=True)