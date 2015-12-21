import webapp2
import urllib2
import json
from model.member import Member
from handlers.web.web_request_handler import WebRequestHandler

class FacebookLoginHandler(WebRequestHandler):
    def any_previous_sessions(self):
        session_id = self.session['email'] if 'email' in self.session else None
        return (session_id != None)

    def get_user_details_from_fb(self):
        print('https://graph.facebook.com/v2.5/'+self['fb_id']+'?access_token='+self['accessToken'])
        user_deets = json.loads(urllib2.urlopen('https://graph.facebook.com/v2.5/'+self['fb_id']+'?fields=id,name,email&access_token='+self['accessToken']).read())
        return user_deets

    def post(self):
        if self.any_previous_sessions():
            print("Returning")
            return
        user_deets = self.get_user_details_from_fb()
        member = Member.get_by_key_name(user_deets['email'])
        if not member:
            member = Member(key_name=user_deets['email'], name=user_deets['name'])
            member.put()
        self.session['email'] = user_deets['email']
        self.session['name'] = user_deets['name']
        self.session['role'] = member.role
        print(self.session['name'])

class LogoutHandler(WebRequestHandler):
    def get(self):
        del self.session['email']
        del self.session['name']
        del self.session['role']


app = webapp2.WSGIApplication([
    ('/rest/fb_login', FacebookLoginHandler),
    ('/rest/logout', LogoutHandler)
])