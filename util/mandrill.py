from google.appengine.api import urlfetch
import json

def send_mandrill_email(template_slug, template_content, to):
    json_mandrill = {
        "key": "xgkxelhSdAwZr2Yn0uPDIA",
        "template_name": template_slug,
        "template_content": template_content,
        "message": {
            "subject": "example subject",
            "from_email": "russ@hirepirates.com",
            "from_name": "Russ Wolf",
            "to": to,
        },
    }
    url = "https://mandrillapp.com/api/1.0/messages/send-template.json"
    result = urlfetch.fetch(url=url,
        payload=json.dumps(json_mandrill),
        method=urlfetch.POST,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})
    return result