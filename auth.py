import urllib
import logging

def _member_logged_in(handler):
    if not 'fb_id' in handler.session:
        return False
    member = Member.get_by_id(handler.session['fb_id'])
    if not member:
        return False
    return True

def login_required(fn):
    def check_login(self, *args):
        if _member_logged_in(self):
            fn(self, *args)
    return check_login