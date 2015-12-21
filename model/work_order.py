from google.appengine.ext import db
from util.mandrill import send_mandrill_email
from model.appliance import Appliance
from model.store import Store
from model.member import Member
from model.provider import Provider

work_order_states = ["CREATED", "ESTIMATED", ["APPROVED", "DISAPPROVED"], "PROVIDER_CHECKED_IN", "COMPLETED"]

class WorkOrderHistory(db.Model):
	time = db.DateTimeProperty(auto_now=True)
	details = db.StringProperty(indexed=False)

class WorkOrder(db.Model):
    appliance = db.StringProperty(indexed=True)
    provider = db.StringProperty(indexed=True)
    history = db.ListProperty(long)
    curr_state = db.StringProperty(indexed=True)

    @property
    def id(self):
        return self.key().id()
    @property
    def appliance_obj(self):
        return Appliance.get_by_id(long(self.appliance))
    @property
    def provider_obj(self):
        return Provider.get_by_id(long(self.provider))
    @property
    def store(self):
        return self.appliance_obj.store
    @property
    def provider_user(self):
        return self.provider_obj.owner
    @property
    def owner_user(self):
        return Member.get_by_key_name(self.store.owner)
    @property
    def manager_user(self):
        return Member.get_by_key_name(self.store.manager)
    @property
    def action_url(self):
        if self.curr_state == 'CREATED':
            return ('ESTIMATE','/work_order/provide_estimate?work_order='+str(self.id))
        elif self.curr_state == 'ESTIMATED':
            return ('PLEASE CHECK EMAIL','')
        elif self.curr_state == 'APPROVED':
            return ('CHECK IN PROVIDER','/rest/work_order/update?work_order='+str(self.id))
        elif self.curr_state == 'PROVIDER_CHECKED_IN':
            return ('COMPLETE','/work_order/completed?work_order='+str(self.id))
        return ''

    def create_wo_history(self, details):
        woh = WorkOrderHistory()
        if details:
            woh.details = details
        woh.put()
        self.history.append(woh.key().id())
        return woh

    def send_wo_created_email(self, wo_id):
        template_content = [
            {'name':'store_name','content':self.store.name},
            {'name':'appliance_type','content':self.appliance_obj.manufacturer+':'+self.appliance_obj.model},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'estimate_link','content':'<a href="http://onepointapp.appspot.com/work_order/provide_estimate?work_order='+str(wo_id)+'">here</a>'}
        ]
        to = [{'email':self.provider_user.key().name(),'name':self.provider_user.name,'type':'to'},
              {'email':self.owner_user.key().name(),'name':self.owner_user.name,'type':'cc'},
              {'email':self.manager_user.key().name(),'name':self.provider_user.name,'type':'cc'}]
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

    def store_login(self, role):
        if role == 'manager' or role == 'owner':
            return True
        return False

    def provider_login(self, role):
        if role == 'provider':
            return True
        return False    

    def update_state(self, params, role):
        ret_val = {'status':'success'}
    	if not self.curr_state:
            if not self.store_login(role):
                ret_val = {'status':'error', 'message':'Only a store manager or owner can create a work order'}
                return ret_val
            self.curr_state = work_order_states[0]
            self.appliance = params['appliance']
            self.provider = params['provider']
            self.create_wo_history(None)
            self.put()
            self.send_wo_created_email(self.key().id())
        elif self.curr_state == 'CREATED':
            if not self.provider_login(role):
                ret_val = {'status':'error', 'message':'Only a provider can estimate a work order'}
                return ret_val
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
            return ret_val
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
            self.create_wo_history(None)
            self.put()
        elif self.curr_state == 'PROVIDER_CHECKED_IN':
            self.curr_state = work_order_states[work_order_states.index('PROVIDER_CHECKED_IN') + 1]
            self.create_wo_history(params['notes'])
            self.put()
        return ret_val
