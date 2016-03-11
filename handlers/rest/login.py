import webapp2
import urllib2
import json
from model.member import Member
from handlers.web.web_request_handler import WebRequestHandler
from auth import login_required

class FacebookLoginHandler(WebRequestHandler):
    def any_previous_sessions(self):
        session_id = self.session['email'] if 'email' in self.session else None
        return (session_id != None)

    def get_user_details_from_fb(self):
        user_deets = json.loads(urllib2.urlopen('https://graph.facebook.com/v2.5/'+self['fb_id']+'?fields=id,name,email&access_token='+self['accessToken']).read())
        return user_deets

    def post(self):
        if self.any_previous_sessions():
            return
        user_deets = self.get_user_details_from_fb()
        member = Member.get_by_key_name(user_deets['email'])
        if not member:
            member = Member(key_name=user_deets['email'], name=user_deets['name'])
            member.put()
        self.session['email'] = user_deets['email']
        self.session['name'] = user_deets['name']
        self.session['fb_id'] = user_deets['id']
        self.session['role'] = member.role

class LogoutHandler(WebRequestHandler):
    @login_required
    def get(self):
        del self.session['email']
        del self.session['name']
        del self.session['fb_id']
        del self.session['role']
        self.redirect('/')

class TempLoginHandler(WebRequestHandler):
    def post(self):
        success = False
        url = '/'
        member = Member.get_by_key_name(self['email'])
        error = ''
        if member:
            if member.role != 'provider':
                self.session['email'] = member.key().name()
                self.session['name'] = member.name
                self.session['fb_id'] = "123"
                self.session['role'] = member.role
                success = True
                url = '/appliance/list'
            else:
                error = "Access for users of role 'Provider' is not allowed"
        else:
            error = 'User not found'
        self.write(json.dumps({'success':success, 'url':url, 'error':error}))

app = webapp2.WSGIApplication([
    ('/rest/fb_login', FacebookLoginHandler),
    ('/rest/logout', LogoutHandler),
    ('/rest/temp_login', TempLoginHandler)
])