from model.store import Store
from model.work_order import WorkOrder
from model.appliance import Appliance
from model.member import Member
from model.provider import Provider
import logging

def convert_to_grid_format(items, tabs):
    items_dict = {}
    for tab in tabs:
        rows = []
        curr_row = []
        for idx,item in enumerate(items):
            if idx != 0 and idx % 3 == 0:
                rows.append(curr_row)
                curr_row = []
            curr_row.append(item)
        if len(curr_row) > 0:
            rows.append(curr_row)
        items_dict[tab] = rows
    return items_dict

def get_appliances_for_logged_in_user(self):
    email = self.session['email']
    role = self.session['role']
    store = Store.all().filter(role + ' =', email).get()
    appliances = [appliance for appliance in Appliance.all().filter('store =', store).fetch(100)]
    return appliances

def get_work_orders_for_logged_in_user(self):
    email = self.session['email']
    workorders = []
    if is_store_login(self):
        store = Store.all().filter(self.session['role'] + ' =', email).get()
        appliances = [appliance.id for appliance in Appliance.all().filter('store =', store).fetch(100)]
        for appliance in appliances:
            print appliance
            workorders.extend([wo for wo in WorkOrder.all().filter('appliance =', str(appliance))])
    elif is_provider_login(self):
        providers = [p for p in Provider.all().fetch(100) if p.owner.key().name() == email]
        for provider in providers:
            workorders.extend([wo for wo in WorkOrder.all().filter('provider =', str(provider.key().id()))])
    return workorders

def is_store_login(self):
    role = self.session['role']
    if role == 'manager' or role == 'owner':
        return True
    return False

def is_provider_login(self):
    role = self.session['role']
    if role == 'provider':
        return True
    return False