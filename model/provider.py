from google.appengine.ext import db

class Provider(db.Model):
    name = db.StringProperty(indexed=False)
    location = db.GeoPtProperty(indexed=True)
    owner = db.ReferenceProperty()
    phone_num = db.StringProperty(indexed=True)
    insurance = db.StringProperty(indexed=False)
    certifications = db.StringProperty(indexed=False)
    reputation = db.FloatProperty(indexed=False)

    @property
    def details_url(self):
        return '/provider/details?id='+str(self.key().id())

    @property
    def template_format(self):
        return [('OWNER',self.owner.name),
                ('EMAIL',self.owner.key().name),
                ('PHONE NUMBER',self.phone_num),
                ('INSURANCE', self.insurance),
                ('CERTIFICATIONS', self.certifications),
                ('REPUTATION', self.reputation)]