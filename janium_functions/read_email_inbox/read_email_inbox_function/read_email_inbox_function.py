import base64
import email
import json
import logging
import os
import quopri
import re
import ssl
from datetime import datetime, timedelta
from email import policy
from email.message import EmailMessage
from uuid import uuid4

import requests
from imapclient import IMAPClient

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('read_email_inbox_function')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('read_email_inbox_function')
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

def get_email_sends_contacts(client):
    return [
        contact for contact in client.contacts.order_by(Contact.full_name) if contact.actions.filter(Action.action_type_id.in_([4])).first()
    ]

def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    session = Session()
    client = session.query(Client).filter(Client.client_id == payload_json['client_id']).first()

    email_server = client.email_config.email_server
    inbox = get_inbox(client.email_config.credentials.username, client.email_config.credentials.password, email_server.imap_address, email_server.imap_ssl_port)

    contacts = get_email_sends_contacts(client)

    contacts_list = []
    for contact in contacts:
        # logger.debug(contact.full_name)
        for message in inbox:
            from_addr = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", message['FROM'])[0]
            body = message.get_body()
            body = str(body.get_payload())
            body = str(quopri.decodestring(body))
            if from_addr in contact.get_emails():
                existing_action = contact.actions.filter(Action.contact_id == contact.contact_id).filter(Action.action_type_id == 6).first()
                if existing_action := contact.actions.filter(Action.contact_id == contact.contact_id).filter(Action.action_type_id == 6).first():
                    logger.debug(str('Existing Action: ' + str(existing_action.action_type_id)))
                else:
                    new_action = Action(str(uuid4()), contact.contact_id, 6, mtn_time, body)
                    session.add(new_action)
                    session.commit()
                    contacts_list.append({"contact_full_name": contact.full_name, "contact_email_address": from_addr, "contact_id": contact.contact_id})
    if len(contacts_list) > 0:
        logger.info("Client {} had new responses from these contacts: {}".format(client.full_name, contacts_list))

if __name__ == '__main__':
    payload = {
        "client_id": "67e736f3-9f35-4bf0-992f-1e8a5afa261a"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
