import webapp2
import urllib2
import json
from model.member import Member
from handlers.web.web_request_handler import WebRequestHandler

class FacebookLoginHandler(WebRequestHandler):
    def any_previous_sessions(self):
        session_id = self.session['fb_id'] if 'fb_id' in self.session else None
        return (session_id != None)

    def get_user_details_from_fb(self):
        print('https://graph.facebook.com/v2.5/'+self['fb_id']+'?access_token='+self['accessToken'])
        user_deets = json.loads(urllib2.urlopen('https://graph.facebook.com/v2.5/'+self['fb_id']+'?fields=id,name,email&access_token='+self['accessToken']).read())
        return user_deets

    def post(self):
        if self.any_previous_sessions():
            return
        user_deets = self.get_user_details_from_fb()
        member = Member.get_by_key_name(user_deets['id'])
        if not member:
        	Member(key_name=user_deets['id'], name=user_deets['name'], email=user_deets['email']).put()
        self.session['fb_id'] = user_deets['id']

app = webapp2.WSGIApplication([
    ('/rest/fb_login', FacebookLoginHandler)
])