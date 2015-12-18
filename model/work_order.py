from google.appengine.ext import db

work_order_states = ["CREATED", "ESTIMATED", ["APPROVED", "DISAPPROVED"], "PROVIDER_CHECKED_IN", "PROVIDER_CHECKED_OUT", "COMPLETED"]

class WorkOrderHistory(db.Model):
	time = db.DateTimeProperty(auto_now=True)
	details = db.StringProperty(indexed=False)

class WorkOrder(db.Model):
    appliance = db.StringProperty(indexed=True)
    provider = db.StringProperty(indexed=True)
    history = db.ListProperty(str)
    curr_state = db.IntProperty(indexed=True)
    state_idx = -1

    def update_state(self, params):
    	if state_idx == -1:
    		state_idx += 1
    		if isinstance(work_order_states[state_idx], str):
    			curr_state = work_order_states[state_idx]
    		appliance = params['appliance']
    		provider = params['provider']
    		woh = WorkOrderHistory()
    		history = [woh]
    	self.put()
