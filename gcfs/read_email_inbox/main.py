import base64
import email
import json
import ssl
from datetime import datetime, timedelta

import google.auth
import requests
from google.cloud import secretmanager
from imapclient import IMAPClient

from db_model import *

mtn_time = datetime.utcnow() - timedelta(hours=7)

def get_inbox(username, password, imap_address, port):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    with IMAPClient(host=imap_address, ssl_context=ssl_context, port=port) as client:
        client.login(username, password)
        client.select_folder('INBOX', readonly=True)

        since = mtn_time - timedelta(days=100)
        since_date = since.date()

        search_response = client.search([u'SINCE', since_date])
        inbox = client.fetch(search_response, b'RFC822')
        return_list =[]
        for id, data in inbox.items():
            return_list.append(email.message_from_bytes(data[b'RFC822']))
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
        # print(inbox)

        contacts = [
            contact for contact in client.contacts.order_by(Contact.full_name) if contact.actions.filter(Action.action_type_id.in_([4])).first()
        ]

        for contact in contacts:
            for message in inbox:
                pass
                # if message['FROM'] in contact.emails:
                    # new_action = Action(str(uuid4()), contact.contact_id, 6, mtn_time, message[])

        for message in inbox:
            print(message._headers)






        # active_campaigns = session.query(Campaign).filter(Campaign.clientid == client.id)\
        #                                             .filter(Campaign.isactive == 1)\
        #                                             .all()

        # for campaign in active_campaigns:
        #     campaign_email_server = session.query(Email_server).filter(Email_server.id == campaign.email_server_id).first()
        #     if campaign_email_server:
        #         inbox = get_inbox(campaign.email_app_username, campaign.email_app_password, campaign_email_server.imap_address, campaign_email_server.imap_ssl_port)
        #     # else:
        #     #     inbox = get_inbox(client.email_app_username, client.email_app_password, email_server.imap_address, email_server.imap_ssl_port, client.dateadded)
        #     with db_engine.connect() as conn:
        #         email_sends = conn.execute("call fetch_email_sends('{}')".format(campaign.id))
        #         email_sends = list(email_sends)

        #     for email_send in email_sends:
        #         bounce = has_bounced(email_send[1], bounces)
        #         if bounce:
        #             print("Email to {} bounced for client {} {}.".format(email_send[0], client.firstname, client.lastname))
        #             new_activity = Activity(email_send[0], datetime.fromtimestamp(bounce['created']), 10, None, email_send[2], False, None)
        #             session.add(new_activity)
        #             session.commit()
        #             continue
        #         for item in inbox:
        #             if email_send[1] in item['FROM']:
        #                 new_response = item
        #                 print("Email response from {} for client {} {}".format(email_send[1], client.firstname, client.lastname))
        #                 new_activity = Activity(email_send[0], new_response['received_datetime'], 6, None, new_response['janium_message_id'], False, None)
        #                 session.add(new_activity)
        #                 session.commit()

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

    # print(len(get_inbox('nic@janium.io', 'nagxjkybavuiviyw', 'imap.gmail.com', 993)))