import base64
import email
import json
import quopri
import re
import ssl
from datetime import datetime, timedelta
from email import policy
from email.message import EmailMessage
from uuid import uuid4
import logging

import google.auth
import requests
from google.cloud import secretmanager
from imapclient import IMAPClient

from db_model import *

if os.getenv('IS_CLOUD') == 'True':
    logger = logging.getLogger('read_inbox')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    logger = logging.getLogger('read_inbox')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)

def get_inbox(username, password, imap_address, port):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    with IMAPClient(host=imap_address, ssl_context=ssl_context, port=port) as client:
        client.login(username, password)
        client.select_folder('INBOX', readonly=True)

        since = mtn_time - timedelta(days=1) # Run this function daily
        since_date = since.date()

        search_response = client.search([u'SINCE', since_date])
        inbox = client.fetch(search_response, b'RFC822')
        return_list =[]
        for id, data in inbox.items():
            return_list.append(email.message_from_bytes(data[b'RFC822'], policy=policy.default))
    return return_list

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    if payload_json['testing'] == 'true':
        clients = session.query(Client).filter(Client.client_id == '8a52cdff-6722-4d26-9a6a-55fe952bbef1').all() # Jonny Karate
    else:
        clients = session.query(Client).filter(Client.is_active == 1)\
                                       .filter(Client.is_sending_emails == 1)\
                                       .filter(Client.email_config_id != Email_config.dummy_email_config_id)\
                                       .all()
    for client in clients:
        email_server = client.email_config.email_server
        inbox = get_inbox(client.email_config.credentials.username, client.email_config.credentials.password, email_server.imap_address, email_server.imap_ssl_port)

        contacts = [
            contact for contact in client.contacts.order_by(Contact.full_name) if contact.actions.filter(Action.action_type_id.in_([4])).first()
        ]

        contacts_list = []
        for contact in contacts:
            for message in inbox:
                from_addr = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", message['FROM'])[0]
                body = message.get_body()
                body = str(body.get_payload())
                body = str(quopri.decodestring(body))
                if from_addr in contact.get_emails():
                    existing_action = contact.actions.filter(Action.contact_id == contact.contact_id).filter(Action.action_type_id == 6).first()
                    logger.debug(existing_action)
                    if not existing_action:
                        new_action = Action(str(uuid4()), contact.contact_id, 6, mtn_time, body)
                        session.add(new_action)
                        session.commit()
                        contacts_list.append(contact.full_name)
        if len(contacts_list) > 0:
            logger.info("Client {} had new responses from these contacts: {}".format(client.full_name, contacts_list))

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
