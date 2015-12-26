from google.appengine.ext import db

class Member(db.Model):
    name = db.StringProperty(indexed=False)
    role = db.StringProperty(indexed=True)

    @property
    def display_string(self):
        return self.key().name() + " : " + self.role

    @property
    def email(self):
        return self.key().name()