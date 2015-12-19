from google.appengine.ext import db
from util.mandrill import send_mandrill_email
from model.appliance import Appliance
from model.store import Store
from model.member import Member
from model.provider import Provider

work_order_states = ["CREATED", "ESTIMATED", ["APPROVED", "DISAPPROVED"], "PROVIDER_CHECKED_IN", "PROVIDER_CHECKED_OUT", "COMPLETED"]

class WorkOrderHistory(db.Model):
	time = db.DateTimeProperty(auto_now=True)
	details = db.StringProperty(indexed=False)

class WorkOrder(db.Model):
    appliance = db.StringProperty(indexed=True)
    provider = db.StringProperty(indexed=True)
    history = db.ListProperty(long)
    curr_state = db.StringProperty(indexed=True)

    def create_wo_history(self, details):
        woh = WorkOrderHistory()
        if details:
            woh.details = details
        woh.put()
        self.history.append(woh.key().id())

    def send_wo_created_email(self):
        appliance = Appliance.get_by_id(long(self.appliance))
        store = appliance.store
        provider = Provider.get_by_id(long(self.provider))
        template_content = [
            {'name':'store_name','content':store.name},
            {'name':'appliance_type','content':appliance.manufacturer+':'+appliance.model},
        ]
        provider_user = provider.owner
        owner = Member.get_by_key_name(store.owner)
        manager = Member.get_by_key_name(store.manager)
        to = [{'email':provider_user.key().name(),'name':provider_user.name,'type':'to'},
              {'email':owner.key().name(),'name':owner.name,'type':'cc'},
              {'email':manager.key().name(),'name':provider.name,'type':'cc'}]
        send_mandrill_email('Work order created', template_content, to)

    def update_state(self, params):
    	if not self.curr_state:
            self.curr_state = work_order_states[0]
            self.appliance = params['appliance']
            self.provider = params['provider']
            self.create_wo_history(None)
            self.send_wo_created_email()
        elif self.curr_state == 'CREATED':
            self.curr_state = work_order_states[work_order_states.index(self.curr_state) + 1]
            self.create_wo_history(params['estimate'])
        elif self.curr_state == 'ESTIMATED':
            if params['approval'] == '1':
                self.curr_state = 'APPROVED'
            else:
                self.curr_state = 'DISAPPROVED'
            self.create_wo_history(None)
        elif self.curr_state == 'APPROVED' or self.curr_state == 'DISAPPROVED':
            self.curr_state = work_order_states[work_order_states.index(["APPROVED", "DISAPPROVED"]) + 1]
            self.create_wo_history(None)
        elif self.curr_state == 'PROVIDER_CHECKED_IN':
            self.curr_state = work_order_states[work_order_states.index('PROVIDER_CHECKED_IN') + 1]
            self.create_wo_history(None)
        elif self.curr_state == 'PROVIDER_CHECKED_OUT':
            self.curr_state = work_order_states[work_order_states.index('PROVIDER_CHECKED_OUT') + 1]
            self.create_wo_history(params['notes'])
    	self.put()
