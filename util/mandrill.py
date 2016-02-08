from google.appengine.api import urlfetch
import json

def send_mandrill_email(template_slug, template_content, to, merge_vars=[]):
    json_mandrill = {
        "key": "rwb7RGauJGM5H1hhTI9vFw",
        "template_name": template_slug,
        "template_content": template_content,
        "message": {
            "from_email": "workorder@genius.repair",
            "from_name": "Genius Admin",
            "to": to,
            "merge_vars": merge_vars,
        },
    }
    url = "https://mandrillapp.com/api/1.0/messages/send-template.json"
    result = urlfetch.fetch(url=url,
        payload=json.dumps(json_mandrill),
        method=urlfetch.POST,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        deadline=30)
    return result