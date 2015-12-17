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

    @property
    def details_url(self):
        return '/appliance/details?id=' + str(self.key().id())

    @property
    def template_format(self):
        return [('MANUFACTURER',self.manufacturer),
                ('MODEL',self.model),
                ('SERIAL NUMBER',self.serial_num),
                ('LAST REPAIR DATE', self.last_repair_date),
                ('INSTALLED ON', self.installed_on),
                ('WARRANTY', self.warranty)]
    