import base64
import json
import logging
from pprint import pprint
from uuid import uuid4

import google.auth
import requests
from sqlalchemy import or_

from db_model import *

if os.getenv('IS_CLOUD') == 'True':
    logger = logging.getLogger('get_sendgrid_bounces')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    logger = logging.getLogger('get_sendgrid_bounces')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)


def get_sendgrid_key():
    creds, project = google.auth.default()
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    secret_name = "sendgrid-api-key"
    project_id = "janium-foundation"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def get_sendgrid_headers():
    headers = {
        "authorization": "Bearer {}".format(get_sendgrid_key())
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
