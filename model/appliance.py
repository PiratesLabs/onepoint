from google.appengine.ext import db

class Appliance(db.Model):
    name = db.StringProperty(indexed=False)
    store = db.ReferenceProperty()
    manufacturer = db.StringProperty(indexed=False)
    model = db.StringProperty(indexed=False)
    serial_num = db.StringProperty(indexed=False)
    last_repair_date = db.StringProperty(indexed=False)
    installed_on = db.StringProperty(indexed=False)
    warranty = db.StringProperty(indexed=False)
    airtable_id = db.StringProperty(indexed=True)

    @property
    def details_url(self):
        return '/appliance/details?id=' + str(self.key().id())

    @property
    def image_name(self):
        return 'appliances/'+self.model+'.png'

    @property
    def select_provider_url(self):
        return '/appliance/select_provider?id='+str(self.key().id())

    @property
    def schedule_repair_url(self):
        return '/appliance/schedule_repair?id='+str(self.key().id())

    @property
    def id(self):
        return self.key().id()

    @property
    def abbr_name(self):
        abbr = (''.join([part[0] for part in self.name.strip().split(' ')])).upper()
        if len(abbr) > 3:
            abbr = abbr[0:3]
        return abbr

    @property
    def template_format(self):
        return [('MANUFACTURER',self.manufacturer),
                ('MODEL',self.model),
                ('SERIAL NUMBER',self.serial_num),
                ('LAST REPAIR DATE', self.last_repair_date),
                ('INSTALLED ON', self.installed_on),
                ('WARRANTY', self.warranty)]

    @classmethod
    def for_id(cls, id):
        return cls.get_by_id(id)
    