import urllib
import logging
from model.member import Member

def _member_logged_in(handler):
    if not 'email' in handler.session:
        return False
    member = Member.get_by_key_name(handler.session['email'])
    if not member:
        return False
    return True

def login_required(fn):
    def check_login(self, *args):
        if _member_logged_in(self):
            fn(self, *args)
    return check_login