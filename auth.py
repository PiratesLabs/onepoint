import urllib
import logging
from model.member import Member

def set_redirect_url(handler):
    handler.session['redirect_url'] = handler.request.url

def _member_logged_in(handler):
    if not 'email' in handler.session:
        set_redirect_url(handler)
        handler.redirect("/")
        return False
    member = Member.get_by_key_name(handler.session['email'])
    if not member:
        set_redirect_url(handler)
        handler.redirect("/")
        return False
    return True

def login_required(fn):
    def check_login(self, *args):
        if _member_logged_in(self):
            fn(self, *args)
    return check_login

def _provider_logged_in(handler):
    if not 'email' in handler.session:
        return False
    member = Member.get_by_key_name(handler.session['email'])
    if not member:
        return False
    if member.role != 'provider':
        return False
    return True

def provider_login_required(fn):
    def check_provider_login(self, *args):
        if _provider_logged_in(self):
            fn(self, *args)
        else:
            self.write('<h1>401 Unauthorized access</h1><p>You are not logged in as a provider to be able to do this action</p>', 401)
    return check_provider_login