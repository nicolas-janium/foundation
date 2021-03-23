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

def get_email_send_contacts(janium_campaign):
    return [
        contact for contact in janium_campaign.contacts.order_by(Contact.contact_id) if contact.actions.filter(Action.action_type_id.in_([4])).first()
    ]

def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)
    
    session = get_session()

    if account := session.query(Account).filter(Account.account_id == payload_json['account_id']).first():
        account_local_time = datetime.now(pytz.timezone('UTC')).astimezone(pytz.timezone(account.time_zone.time_zone_code)).replace(tzinfo=None)
        for janium_campaign in account.janium_campaigns:
            if janium_campaign.email_config.email_config_id != Email_config.unassigned_email_config_id and janium_campaign.email_config.is_email_forward == 0:

                email_server = janium_campaign.email_config.email_server
                inbox = get_inbox(janium_campaign.email_config.credentials.username, janium_campaign.email_config.credentials.password, email_server.imap_address, email_server.imap_ssl_port)
                contacts = get_email_send_contacts(janium_campaign)

                contact_list = []
                for contact in contacts:
                    for message in inbox:
                        from_addr = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", message['FROM'])[0]
                        body = message.get_body()
                        body = str(body.get_payload())
                        body = str(quopri.decodestring(body))
                        if from_addr in contact.get_emails():
                            if existing_action := contact.actions.filter(Action.contact_id == contact.contact_id).filter(Action.action_type_id == 6).first():
                                if continue_campaign_action:= contact.actions.filter(Action.contact_id == contact.contact_id).filter(Action.action_type_id == 14).first():
                                    if existing_action.action_timestamp < continue_campaign_action.action_timestamp:
                                        new_action = Action(str(uuid4()), contact.contact_id, 6, mtn_time, body)
                                        session.add(new_action)
                                        session.commit()
                                        contact_list.append(
                                            {
                                                "contact_first_name": contact.contact_info['ulinc']['first_name'],
                                                "contact_email_address": from_addr,
                                                "contact_id": contact.contact_id,
                                                "janium_campaign": janium_campaign.janium_campaign_name
                                            }
                                        )
                                    else:
                                        pass
                                else:
                                    pass
                            else:
                                new_action = Action(str(uuid4()), contact.contact_id, 6, mtn_time, body)
                                session.add(new_action)
                                session.commit()
                                contact_list.append(
                                        {
                                            "contact_first_name": contact.contact_info['ulinc']['first_name'],
                                            "contact_email_address": from_addr,
                                            "contact_id": contact.contact_id,
                                            "janium_campaign": janium_campaign.janium_campaign_name
                                        }
                                    )
    if len(contact_list) > 0:
        logger.info("Account {} had new responses from these contacts: {}".format(account.account_id, contact_list))

if __name__ == '__main__':
    payload = {
        "account_id": "ee4c4be2-14ac-43b2-9a2d-8cd49cd534f3"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
