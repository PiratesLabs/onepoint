from google.appengine.api import urlfetch
import json

def send_mandrill_email(template_slug):
    json_mandrill = {
        "key": "rwb7RGauJGM5H1hhTI9vFw",
        "template_name": template_slug,
        "template_content": [
        ],
        "message": {
            "subject": "example subject",
            "from_email": "russ@hirepirates.com",
            "from_name": "Russ Wolf",
            "to": [
                {
                    "email": "ranju@hirepirates.com",
                    "name": "Niranjan Salimath",
                    "type": "to"
                }
            ],
        },
    }
    url = "https://mandrillapp.com/api/1.0/messages/send-template.json"
    result = urlfetch.fetch(url=url,
        payload=json.dumps(json_mandrill),
        method=urlfetch.POST,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})
    print(result.content)
    return result