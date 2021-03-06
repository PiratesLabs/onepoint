from google.appengine.ext import db

class Provider(db.Model):
    name = db.StringProperty(indexed=False)
    location = db.GeoPtProperty(indexed=True)
    address = db.StringProperty(indexed=False)
    owner = db.ReferenceProperty()
    phone_num = db.StringProperty(indexed=True)
    insurance = db.StringProperty(indexed=False)
    certifications = db.StringProperty(indexed=False)
    reputation = db.FloatProperty(indexed=False)
    airtable_id = db.StringProperty(indexed=True)

    @property
    def details_url(self):
        return '/provider/details?id='+str(self.key().id())

    @property
    def image_name(self):
        return 'providers/'+self.name+'.png'

    @property
    def schedule_repair_url(self):
        return '/provider/schedule_repair?id='+str(self.key().id())

    @property
    def id(self):
        return self.key().id()

    @property
    def abbr_name(self):
        return (''.join([part[0] for part in self.name.split(' ')])).upper()

    @property
    def template_format(self):
        return [('OWNER',self.owner.name),
                ('EMAIL',self.owner.key().name),
                ('PHONE NUMBER',self.phone_num),
                ('INSURANCE', self.insurance),
                ('CERTIFICATIONS', self.certifications),
                ('REPUTATION', self.reputation)]