from google.appengine.ext import db
from util.mandrill import send_mandrill_email
from model.appliance import Appliance
from model.store import Store
from model.member import Member
from model.provider import Provider

work_order_states = ["CREATED", "ESTIMATED", ["APPROVED", "DISAPPROVED"], "COMPLETED"]

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
        return woh

    def send_wo_created_email(self, wo_id):
        appliance = Appliance.get_by_id(long(self.appliance))
        store = appliance.store
        provider = Provider.get_by_id(long(self.provider))
        template_content = [
            {'name':'store_name','content':store.name},
            {'name':'appliance_type','content':appliance.manufacturer+':'+appliance.model},
            {'name':'provider_name','content':provider.name},
            {'name':'estimate_link','content':'<a href="http://onepointapp.appspot.com/work_order/provide_estimate?work_order='+str(wo_id)+'">here</a>'}
        ]
        provider_user = provider.owner
        owner = Member.get_by_key_name(store.owner)
        manager = Member.get_by_key_name(store.manager)
        to = [{'email':provider_user.key().name(),'name':provider_user.name,'type':'to'},
              {'email':owner.key().name(),'name':owner.name,'type':'cc'},
              {'email':manager.key().name(),'name':provider.name,'type':'cc'}]
        send_mandrill_email('Work order created', template_content, to)

    def send_wo_approval_email(self, estimate, wo_id):
        appliance = Appliance.get_by_id(long(self.appliance))
        store = appliance.store
        provider = Provider.get_by_id(long(self.provider))
        provider_user = provider.owner
        owner = Member.get_by_key_name(store.owner)
        manager = Member.get_by_key_name(store.manager)
        template_content = [
            {'name':'owner_name','content':owner.name},
            {'name':'appliance_type','content':appliance.manufacturer+':'+appliance.model},
            {'name':'estimate','content':estimate},
            {'name':'provider_name','content':provider.name},
            {'name':'approval_link','content':'<a href="http://onepointapp.appspot.com/rest/work_order/update?work_order='+str(wo_id)+'&params=approval:1">here</a>'},
            {'name':'disapproval_link','content':'<a href="http://onepointapp.appspot.com/rest/work_order/update?work_order='+str(wo_id)+'&params=approval:0">here</a>'}
        ]
        to = [{'email':owner.key().name(),'name':owner.name,'type':'to'}]
        send_mandrill_email('approve-work-order', template_content, to)

    def send_wo_disapproved_email(self, wo_id):
        appliance = Appliance.get_by_id(long(self.appliance))
        store = appliance.store
        provider = Provider.get_by_id(long(self.provider))
        provider_user = provider.owner
        template_content = [
            {'name':'appliance_type','content':appliance.manufacturer+':'+appliance.model},
            {'name':'provider_name','content':provider.name},
            {'name':'store_name','content':store.name}
        ]
        to = [{'email':provider_user.key().name(),'name':provider_user.name,'type':'to'}]
        send_mandrill_email('work-order-disapproved', template_content, to)

    def send_wo_approved_email(self, wo_id):
        appliance = Appliance.get_by_id(long(self.appliance))
        store = appliance.store
        provider = Provider.get_by_id(long(self.provider))
        provider_user = provider.owner
        template_content = [
            {'name':'appliance_type','content':appliance.manufacturer+':'+appliance.model},
            {'name':'provider_name','content':provider.name},
            {'name':'store_name','content':store.name}
        ]
        to = [{'email':provider_user.key().name(),'name':provider_user.name,'type':'to'}]
        send_mandrill_email('work-order-approved', template_content, to)

    def update_state(self, params):
    	if not self.curr_state:
            self.curr_state = work_order_states[0]
            self.appliance = params['appliance']
            self.provider = params['provider']
            self.create_wo_history(None)
            self.put()
            self.send_wo_created_email(self.key().id())
        elif self.curr_state == 'CREATED':
            estimate = long(params['estimate'])
            self.create_wo_history(params['estimate'])
            if estimate > 250:
                self.curr_state = work_order_states[work_order_states.index(self.curr_state) + 1]
                self.send_wo_approval_email(params['estimate'], self.key().id())
            else:
                self.curr_state = 'APPROVED'
                self.create_wo_history(None)
                self.send_wo_approved_email(self.key().id())
            self.put()
            return
        elif self.curr_state == 'ESTIMATED':
            if params['approval'] == '1':
                self.curr_state = 'APPROVED'
                self.send_wo_approved_email(self.key().id())
            else:
                self.curr_state = 'DISAPPROVED'
                self.send_wo_disapproved_email(self.key().id())
            self.create_wo_history(None)
            self.put()
        elif self.curr_state == 'APPROVED':
            self.curr_state = work_order_states[work_order_states.index(["APPROVED", "DISAPPROVED"]) + 1]
            self.create_wo_history(params['notes'])
            self.put()
