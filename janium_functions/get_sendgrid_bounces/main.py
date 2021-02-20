import base64
import json
import logging
import os
from pprint import pprint
from uuid import uuid4

import requests
from sqlalchemy import or_

if not os.getenv('LOCAL_DEV'):
    from model import *
    logger = logging.getLogger('get_sendgrid_bounces')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('get_sendgrid_bounces')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)


def get_sendgrid_headers():
    headers = {
        "authorization": "Bearer {}".format(os.getenv('SENDGRID_API_KEY'))
    }
    return headers

def get_bounces():
    url = "https://api.sendgrid.com/v3/suppression/bounces"

    response = requests.get(url=url, headers=get_sendgrid_headers())
    if response.ok:
        return [item['email'] for item in response.json()]

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    bounced_emails = get_bounces()

    contacts = session.query(Contact).filter(Contact.actions.any(Action.action_type_id == 4)).all()

    for contact in contacts:
        if any(check in contact.get_emails() for check in bounced_emails):
            if not contact.actions.filter(Action.action_type_id == 15).first():
                bounced_action = Action(str(uuid4()), contact.contact_id, 15, mtn_time, None)
                session.add(bounced_action)
                session.commit()
                logger.info("Email to contact {} bounced".format(contact.full_name))


if __name__ == '__main__':
    payload = {
        "testing": "true"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
