from google.appengine.ext import db
from util.mandrill import send_mandrill_email
from model.appliance import Appliance
from model.store import Store
from model.member import Member
from model.provider import Provider
from datetime import datetime
import pytz
from pytz import timezone

work_order_states = ["CREATED", ["ESTIMATED", "REJECTED"], ["APPROVED", "DISAPPROVED"], "PROVIDER_CHECKED_IN", "COMPLETED", "CANCELLED"]
work_order_display_names = {
        "CREATED":"CREATED", 
        "ESTIMATED":"PENDING", 
        "REJECTED":"REJECTED", 
        "APPROVED":"SCHEDULED", 
        "DISAPPROVED":"DISAPPROVED", 
        "PROVIDER_CHECKED_IN":"PROVIDER_CHECKED_IN", 
        "COMPLETED":"COMPLETED",
        "CANCELLED":"CANCELLED"
}
work_order_state_index = {
        "CREATED":0, 
        "ESTIMATED":1, 
        "REJECTED":1, 
        "APPROVED":2, 
        "DISAPPROVED":2, 
        "PROVIDER_CHECKED_IN":3, 
        "COMPLETED":4,
        "CANCELLED":-1
}
separator = '~~##'

def get_display_id(long_id):
    str_id = str(long_id)
    retVal = []
    for (idx, char) in enumerate(str_id):
        if idx > 0 and idx % 4 == 0:
            retVal.append("-")
        retVal.append(char)
    return "".join(retVal)

class WorkOrderHistory(db.Model):
	time = db.DateTimeProperty(auto_now=True)
	details = db.StringProperty(indexed=False)

class WorkOrder(db.Model):
    appliance = db.StringProperty(indexed=True)
    provider = db.StringProperty(indexed=True)
    history = db.ListProperty(long)
    curr_state = db.StringProperty(indexed=True)
    fix_by = db.DateTimeProperty(indexed=False)
    problem_description = db.StringProperty(indexed=False)
    priority = db.StringProperty()

    @property
    def id(self):
        return self.key().id()

    @property
    def display_id(self):
        return get_display_id(self.key().id())

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
    def fix_by_date(self):
        details = WorkOrderHistory.get_by_id(self.history[work_order_states.index('CREATED')]).details.split(separator)
        return details[2] if len(details) > 2 else ''
    @property
    def curr_state_display_name(self):
        return self.get_state_display_name()
    @property
    def curr_state_timestamp(self):
        return self.get_work_order_history().time.replace(tzinfo=timezone('UTC')).astimezone(timezone('US/Eastern'))
    @property
    def curr_state_notes(self):
        return self.get_work_order_history().details

    def get_state_display_name(self, state=None):
        state = self.curr_state if not state else state
        return work_order_display_names[state]

    def get_work_order_history(self, state=None):
        state = self.curr_state if not state else state
        index = work_order_state_index[state]
        if index == -1:
            return WorkOrderHistory.get_by_id(self.history[len(self.history)-1])
        else:
            return WorkOrderHistory.get_by_id(self.history[index])
    
    def time_to_service(self, end_woh):
        time_to_service = ''
        if self.curr_state == 'COMPLETED':
            start = WorkOrderHistory.get_by_id(self.history[(len(self.history) - 2)]).time
            end = end_woh.time
            time_delta = end - start
            s = time_delta.seconds
            hours, remainder = divmod(s, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_to_service = '%s hours %s minutes' % (hours, minutes)
        return time_to_service

    @property
    def action_url(self):
        if self.curr_state == 'CREATED':
            return [('ESTIMATE','')]
        elif self.curr_state == 'ESTIMATED':
            return [('APPROVE','approval:1'), ('DISAPPROVE','approval:0')]
        elif self.curr_state == 'APPROVED':
            return [('CHECK IN PROVIDER','')]
        elif self.curr_state == 'PROVIDER_CHECKED_IN':
            return [('COMPLETE','')]
        return None

    def create_wo_history(self, details):
        woh = WorkOrderHistory()
        if details:
            woh.details = details
        woh.put()
        self.history.append(woh.key().id())
        return woh

    def send_wo_created_email(self, wo_id, fix_by):
        estimation_link = "http://onepointstaging.appspot.com/work_order/provide_estimate?work_order="+str(wo_id)
        template_content = [
            {'name':'work_order_id','content':self.display_id},
            {'name':'store_name','content':self.appliance_obj.store.name},
            {'name':'provider_address','content':self.provider_obj.address},
            {'name':'store_address','content':self.store.address},
            {'name':'store_name','content':self.store.name},
            {'name':'store_manager_name','content':self.manager_user.name},
            {'name':'store_manager_phone','content':self.manager_user.phone},
            {'name':'store_billing_address','content':self.store.billing_address},
            {'name':'appliance_name','content':self.appliance_obj.name},
            {'name':'manufacturer','content':self.appliance_obj.manufacturer},
            {'name':'model','content':self.appliance_obj.model},
            {'name':'serial_num','content':self.appliance_obj.serial_num},
            {'name':'warranty','content':self.appliance_obj.warranty},
            {'name':'appliance_status','content':self.problem_description},
            {'name':'service_type','content':self.priority},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'accept_link','content':'<a class="mcnButton " title="ACCEPT" href="' + estimation_link + '&action=accept' + '" target="_blank" style="font-weight: bold;letter-spacing: normal;line-height: 100%;text-align: center;text-decoration: none;color: #FFFFFF;">ACCEPT</a>'},
            {'name':'reject_link','content':'<a class="mcnButton " title="REJECT" href="' + estimation_link + '&action=reject' + '" target="_blank" style="font-weight: bold;letter-spacing: normal;line-height: 100%;text-align: center;text-decoration: none;color: #FFFFFF;">REJECT</a>'},
            {'name':'fix_by','content':fix_by},
        ]
        to = [{'email': self.provider_user.key().name(),'name':self.provider_user.name,'type':'to'}]
        merge_vars = [{"rcpt": self.provider_user.key().name(),"vars": [{"name":"ROLE", "content":"provider"}]},
                      {"rcpt": self.owner_user.key().name(),"vars": [{"name":"ROLE", "content":"owner"}]},
                      {"rcpt": self.manager_user.key().name(),"vars": [{"name":"ROLE", "content":"manager"}]}]
        send_mandrill_email('work-order-created-3', template_content, to, "Service Order created", merge_vars)

    def send_wo_approval_email(self, estimate, service_date, technician):
        link = 'http://onepointstaging.appspot.com/work_order/list?work_order='+str(self.key().id())
        template_content = [
            {'name':'work_order_id','content':self.display_id},
            {'name':'store_name','content':self.appliance_obj.store.name},
            {'name':'fix_by','content':service_date},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'provider_address','content':self.provider_obj.address},
            {'name':'owner_name','content':self.owner_user.name},
            {'name':'estimate','content':estimate},
            {'name':'store_name','content':self.store.name},
            {'name':'store_manager_name','content':self.manager_user.name},
            {'name':'store_manager_phone','content':self.manager_user.phone},
            {'name':'store_address','content':self.store.address},
            {'name':'store_billing_address','content':self.store.billing_address},
            {'name':'appliance_name','content':self.appliance_obj.name},
            {'name':'manufacturer','content':self.appliance_obj.manufacturer},
            {'name':'model','content':self.appliance_obj.model},
            {'name':'serial_num','content':self.appliance_obj.serial_num},
            {'name':'warranty','content':self.appliance_obj.warranty},
            {'name':'application_status','content':self.problem_description},
            {'name':'technician','content':technician},
            {'name':'action_link','content':'<a class="mcnButton " title="TAKE ACTION" href="'+ link + '" target="_blank" style="font-weight: bold;letter-spacing: normal;line-height: 100%;text-align: center;text-decoration: none;color: #FFFFFF;">TAKE ACTION</a>'},
        ]
        to = [{'email':self.owner_user.key().name(),'name':self.owner_user.name,'type':'to'}]
        merge_vars = [{"rcpt": self.owner_user.key().name(),"vars": [{"name":"ROLE", "content":"owner"}]},
                      {"rcpt": self.manager_user.key().name(),"vars": [{"name":"ROLE", "content":"manager"}]}]
        send_mandrill_email('approve-work-order-3', template_content, to, "Service Order - Request for approval", merge_vars)

    def send_wo_disapproved_email(self, notes):
        template_content = [
            {'name':'work_order_id','content':self.display_id},
            {'name':'store_name','content':self.appliance_obj.store.name},
            {'name':'provider_address','content':self.provider_obj.address},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'fix_by','content':self.fix_by.strftime('%Y-%m-%d')},
            {'name':'store_name','content':self.store.name},
            {'name':'store_manager_name','content':self.manager_user.name},
            {'name':'store_manager_phone','content':self.manager_user.phone},
            {'name':'store_address','content':self.store.address},
            {'name':'store_billing_address','content':self.store.billing_address},
            {'name':'owner_name','content':self.owner_user.name},
            {'name':'appliance_name','content':self.appliance_obj.name},
            {'name':'manufacturer','content':self.appliance_obj.manufacturer},
            {'name':'model','content':self.appliance_obj.model},
            {'name':'serial_num','content':self.appliance_obj.serial_num},
            {'name':'warranty','content':self.appliance_obj.warranty},
            {'name':'application_status','content':self.problem_description},
            {'name':'remarks','content':notes}
        ]
        to = [{'email':self.provider_user.key().name(),'name':self.provider_user.name,'type':'to'}]
        send_mandrill_email('work-order-disapproved-3', template_content, to, "Service Order denied by owner of the store")

    def send_wo_approved_email(self, notes):
        woh = WorkOrderHistory.get_by_id(self.history[work_order_states.index(["ESTIMATED", "REJECTED"])]).details
        service_date, estimate_str, technician = woh.split(separator)
        template_content = [
            {'name':'work_order_id','content':self.display_id},
            {'name':'store_name','content':self.appliance_obj.store.name},
            {'name':'provider_address','content':self.provider_obj.address},
            {'name':'fix_by','content':self.fix_by.strftime('%Y-%m-%d')},
            {'name':'owner_name','content':self.owner_user.name},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'store_name','content':self.store.name},
            {'name':'store_manager_name','content':self.manager_user.name},
            {'name':'store_manager_phone','content':self.manager_user.phone},
            {'name':'store_address','content':self.store.address},
            {'name':'store_billing_address','content':self.store.billing_address},
            {'name':'appliance_name','content':self.appliance_obj.name},
            {'name':'manufacturer','content':self.appliance_obj.manufacturer},
            {'name':'model','content':self.appliance_obj.model},
            {'name':'serial_num','content':self.appliance_obj.serial_num},
            {'name':'warranty','content':self.appliance_obj.warranty},
            {'name':'application_status','content':self.problem_description},
            {'name':'technician','content':technician},
            {'name':'estimate','content':estimate_str},
            {'name':'remarks','content':notes}
        ]
        to = [{'email':self.provider_user.key().name(),'name':self.provider_user.name,'type':'to'}]
        send_mandrill_email('work-order-approved-3', template_content, to, "Service Order scheduled")

    def send_wo_completed_email(self, wo_id, notes, woh):
        template_content = [
            {'name':'work_order_id','content':self.display_id},
            {'name':'store_name','content':self.appliance_obj.store.name},
            {'name':'fix_by','content':self.fix_by.strftime('%Y-%m-%d')},
            {'name':'provider_address','content':self.provider_obj.address},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'store_name','content':self.store.name},
            {'name':'store_manager_name','content':self.manager_user.name},
            {'name':'store_manager_phone','content':self.manager_user.phone},
            {'name':'store_address','content':self.store.address},
            {'name':'store_billing_address','content':self.store.billing_address},
            {'name':'appliance_name','content':self.appliance_obj.name},
            {'name':'manufacturer','content':self.appliance_obj.manufacturer},
            {'name':'model','content':self.appliance_obj.model},
            {'name':'serial_num','content':self.appliance_obj.serial_num},
            {'name':'warranty','content':self.appliance_obj.warranty},
            {'name':'application_status','content':self.problem_description},
            {'name':'remarks','content':notes},
            {'name':'time_taken','content':self.time_to_service(woh)}
        ]
        to = [{'email':self.provider_user.key().name(),'name':self.provider_user.name,'type':'to'}]
        subject = "Service Order Completed - " + str(self.display_id) + ". Service Provider - " + self.provider_obj.name
        send_mandrill_email('work-order-completed-3', template_content, to, subject)

    def send_wo_rejected_email(self, remarks):
        template_content = [
            {'name':'work_order_id','content':self.display_id},
            {'name':'store_name','content':self.appliance_obj.store.name},
            {'name':'fix_by','content':self.fix_by.strftime('%Y-%m-%d')},
            {'name':'provider_address','content':self.provider_obj.address},
            {'name':'store_manager_name','content':self.manager_user.name},
            {'name':'store_manager_phone','content':self.manager_user.phone},
            {'name':'store_address','content':self.store.address},
            {'name':'store_billing_address','content':self.store.billing_address},
            {'name':'manager_name','content':self.manager_user.name},
            {'name':'store_name','content':self.store.name},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'appliance_name','content':self.appliance_obj.name},
            {'name':'manufacturer','content':self.appliance_obj.manufacturer},
            {'name':'model','content':self.appliance_obj.model},
            {'name':'serial_num','content':self.appliance_obj.serial_num},
            {'name':'warranty','content':self.appliance_obj.warranty},
            {'name':'appliance_status','content':self.problem_description},
            {'name':'reject_remarks','content':remarks},
        ]
        to = [{'email':self.owner_user.key().name(),'name':self.owner_user.name,'type':'to'}]
        send_mandrill_email('work-order-rejected-3', template_content, to, "Service request rejected by vendor")

    def send_wo_auto_approved_email(self, estimate_str, service_date, technician):
        template_content = [
            {'name':'work_order_id','content':self.display_id},
            {'name':'store_name','content':self.appliance_obj.store.name},
            {'name':'provider_address','content':self.provider_obj.address},
            {'name':'fix_by','content':service_date},
            {'name':'owner_name','content':self.owner_user.name},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'store_name','content':self.store.name},
            {'name':'store_manager_name','content':self.manager_user.name},
            {'name':'store_manager_phone','content':self.manager_user.phone},
            {'name':'store_address','content':self.store.address},
            {'name':'store_billing_address','content':self.store.billing_address},
            {'name':'appliance_name','content':self.appliance_obj.name},
            {'name':'manufacturer','content':self.appliance_obj.manufacturer},
            {'name':'model','content':self.appliance_obj.model},
            {'name':'serial_num','content':self.appliance_obj.serial_num},
            {'name':'warranty','content':self.appliance_obj.warranty},
            {'name':'application_status','content':self.problem_description},
            {'name':'technician','content':technician},
            {'name':'estimate','content':estimate_str},
        ]
        to = [{'email':self.provider_user.key().name(),'name':self.provider_user.name,'type':'to'}]
        send_mandrill_email('work-order-approved-3', template_content, to, "Service Order scheduled")

    def send_wo_cancelled_email(self):
        template_content = [
            {'name':'work_order_id','content':self.display_id},
            {'name':'store_name','content':self.appliance_obj.store.name},
            {'name':'provider_address','content':self.provider_obj.address},
            {'name':'fix_by','content':self.fix_by.strftime('%Y-%m-%d')},
            {'name':'owner_name','content':self.owner_user.name},
            {'name':'provider_name','content':self.provider_obj.name},
            {'name':'store_name','content':self.store.name},
            {'name':'store_manager_name','content':self.manager_user.name},
            {'name':'store_manager_phone','content':self.manager_user.phone},
            {'name':'store_address','content':self.store.address},
            {'name':'store_billing_address','content':self.store.billing_address},
            {'name':'appliance_name','content':self.appliance_obj.name},
            {'name':'manufacturer','content':self.appliance_obj.manufacturer},
            {'name':'model','content':self.appliance_obj.model},
            {'name':'serial_num','content':self.appliance_obj.serial_num},
            {'name':'warranty','content':self.appliance_obj.warranty},
            {'name':'appliance_status','content':self.problem_description},
            {'name':'service_type','content':self.priority}
        ]
        to = [{'email':self.provider_user.key().name(),'name':self.provider_user.name,'type':'to'}]
        subject = "Service Order Cancelled - " + str(self.display_id) + ". Service Provider - " + self.provider_obj.name
        send_mandrill_email('work-order-cancelled-3', template_content, to, subject)

    def store_login(self, role):
        if role == 'manager' or role == 'owner':
            return True
        return False

    def provider_login(self, role):
        if role == 'provider':
            return True
        return False

    def owner_login(self, role):
        if role == 'owner':
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
            self.fix_by = datetime.strptime(params['fix_by'], '%m/%d/%y')
            notes = params['remarks'] + separator + params['priority'] + separator + params['fix_by']
            self.problem_description = params['remarks']
            self.priority = params['priority']
            woh = self.create_wo_history(notes)
            self.put()
            self.send_wo_created_email(self.key().id(), params['fix_by'])
        elif self.curr_state == 'ESTIMATED':
            if not self.owner_login(role):
                ret_val = {'status':'error', 'message':'Only a store owner can approve a work order'}
                return ret_val
            if params['approval'] == '1':
                self.curr_state = 'APPROVED'
                self.send_wo_approved_email(params['notes'])
            else:
                self.curr_state = 'DISAPPROVED'
                self.send_wo_disapproved_email(params['notes'])
            self.create_wo_history(params['notes'])
            self.put()
        elif self.curr_state == 'APPROVED':
            self.curr_state = work_order_states[work_order_states.index(["APPROVED", "DISAPPROVED"]) + 1]
            self.create_wo_history(None)
            self.put()
        elif self.curr_state == 'PROVIDER_CHECKED_IN':
            self.curr_state = work_order_states[work_order_states.index('PROVIDER_CHECKED_IN') + 1]
            woh = self.create_wo_history(params['notes'])
            self.put()
            self.send_wo_completed_email(self.key().id(), params['notes'], woh)
        return ret_val

    def estimate(self, approval_str, params):
        ret_val = {'status':'success', 'id':self.key().id()}
        if self.curr_state != 'CREATED':
            msg = 'Unable to schedule this Service Order, since an action has already been taken on it.'
            if self.curr_state == 'CANCELLED':
                msg = 'Unable to schedule this Service Order, since it has been cancelled already by the Requestor.'
            ret_val = {'status':'error', 'message':msg}
            return ret_val
        approval = int(approval_str)
        self.create_wo_history(params)
        if approval == 1:
            service_date, estimate_str, technician = params.split(separator)
            estimate = long(estimate_str) if estimate_str != 'TBD' else 0
            if estimate > 250:
                self.curr_state = "ESTIMATED"
                self.send_wo_approval_email(estimate_str, service_date, technician)
            else:
                self.curr_state = 'APPROVED'
                self.send_wo_auto_approved_email(estimate_str, service_date, technician)
                self.create_wo_history(None)
            self.fix_by = datetime.strptime(service_date, '%m/%d/%y')
        else:
            self.curr_state = "REJECTED"
        self.put()
        return ret_val

    def cancel(self):
        self.curr_state = "CANCELLED"
        self.create_wo_history(None)
        self.put()
        self.send_wo_cancelled_email()

    def get_action_url(self, role):
        if self.curr_state == 'CANCELLED':
            return None
        elif self.curr_state == 'CREATED':
            return self.action_url if role == 'provider' else None
        elif self.curr_state == 'ESTIMATED':
            return self.action_url if role == 'owner' else None
        elif self.curr_state == 'APPROVED':
            return self.action_url if role == 'owner' or role == 'manager' else None
        elif self.curr_state == 'PROVIDER_CHECKED_IN':
            return self.action_url if role == 'owner' or role == 'manager' else None
        return None
