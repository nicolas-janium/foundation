import base64
import json
import logging
import os
from email.message import EmailMessage

import google.auth
import requests
from google.cloud import secretmanager

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('function_error_notifier_function')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('function_error_notifier_function')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)


def get_sendgrid_headers():
    headers = {
        "authorization": "Bearer {}".format(os.getenv('SENDGRID_API_KEY'))
    }
    return headers

def send_email(body, function_name):
    payload = {
        "personalizations": [
            {
                "to": [
                    {
                        "email": 'nic@janium.io',
                        "name": 'Nicolas Arnold'
                    }
                ],
                "subject": "Function Error in {} {}".format(os.getenv('PROJECT_ID'), function_name)
            }
        ],
        "from": {
            "email": 'nic@janium.io',
            "name": 'Nicolas Arnold'
        },
        "reply_to": {
            "email": 'nic@janium.io',
            "name": 'Nicolas Arnold'
        },
        "content": [
            {
                "type": "text/plain",
                "value": body
            }
        ],
        "tracking_settings": {
            "click_tracking": {
                "enable": False,
                "enable_text": False
            },
            "open_tracking": {
                "enable": False
            }
        }
    }

    url = "https://api.sendgrid.com/v3/mail/send"

    res = requests.post(url=url, json=payload, headers=get_sendgrid_headers())
 
def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)
    print(payload_json)

    # email_message = EmailMessage()
    # print("Error in {}".format(payload_json['resource']['labels']['function_name']))
    send_email(payload_json['textPayload'], payload_json['resource']['labels']['function_name'])
