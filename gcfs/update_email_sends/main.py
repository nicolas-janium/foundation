import base64
import email
import json
import ssl
from datetime import datetime, timedelta

import google.auth
import requests
from google.cloud import secretmanager
from imapclient import IMAPClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sal_db import Activity, Campaign, Client, Email_server, get_db_url


def get_sendgrid_key():
    creds, project = google.auth.default()
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    secret_name = "sendgrid-api-key"
    project_id = "janium0-0"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def has_bounced(from_email, bounces):
    for bounce in bounces:
        if bounce['email'] == from_email:
            return bounce
    return None

def get_bounces():
    url = "https://api.sendgrid.com/v3/suppression/bounces"
    headers = {
        'authorization': "Bearer {}".format(get_sendgrid_key()),
        'accept': "application/json"
    }
    response = requests.get(url=url, headers=headers)
    if response.ok:
        return response.json()

def get_inbox(username, password, smtp_server, port):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    with IMAPClient(host=smtp_server, ssl_context=ssl_context, port=port) as client:
        client.login(username, password)
        client.select_folder('INBOX')

        since = datetime.now() - timedelta(days=2)
        since_date = since.date()

        search_response = client.search([u'SINCE', since_date])
        inbox = client.fetch(search_response, 'RFC822')
        return_list =[]
        for id, data in inbox.items():
            return_list.append(email.message_from_bytes(data[b'RFC822']))
    return return_list

def main(event, context):
    db_url = get_db_url()
    db_engine = create_engine(db_url, echo=False)
    session = sessionmaker(bind=db_engine)()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    bounces = get_bounces()

    if payload_json['from'] == 'test':
        pass
    else:
        active_clients = session.query(Client).filter(Client.isactive == 1)\
                                              .filter(Client.is_sending_emails == 1)\
                                              .filter(Client.email_app_username != None)\
                                              .filter(Client.email_app_password != None)\
                                              .filter(Client.email_server_id != None)\
                                              .all()
        for client in active_clients:
            email_server = session.query(Email_server).filter(Email_server.id == client.email_server_id).first()

            inbox = get_inbox(client.email_app_username, client.email_app_password, email_server.imap_address, email_server.imap_ssl_port)

            active_campaigns = session.query(Campaign).filter(Campaign.clientid == client.id)\
                                                      .filter(Campaign.isactive == 1)\
                                                      .all()

            for campaign in active_campaigns:
                campaign_email_server = session.query(Email_server).filter(Email_server.id == campaign.email_server_id).first()
                if campaign_email_server:
                    inbox = get_inbox(campaign.email_app_username, campaign.email_app_password, campaign_email_server.imap_address, campaign_email_server.imap_ssl_port)
                # else:
                #     inbox = get_inbox(client.email_app_username, client.email_app_password, email_server.imap_address, email_server.imap_ssl_port, client.dateadded)
                with db_engine.connect() as conn:
                    email_sends = conn.execute("call fetch_email_sends('{}')".format(campaign.id))
                    email_sends = list(email_sends)

                for email_send in email_sends:
                    bounce = has_bounced(email_send[1], bounces)
                    if bounce:
                        print("Email to {} bounced for client {} {}.".format(email_send[0], client.firstname, client.lastname))
                        new_activity = Activity(email_send[0], datetime.fromtimestamp(bounce['created']), 10, None, email_send[2], False, None)
                        session.add(new_activity)
                        session.commit()
                        continue
                    for item in inbox:
                        if email_send[1] in item['FROM']:
                            new_response = item
                            print("Email response from {} for client {} {}".format(email_send[1], client.firstname, client.lastname))
                            new_activity = Activity(email_send[0], new_response['received_datetime'], 6, None, new_response['janium_message_id'], False, None)
                            session.add(new_activity)
                            session.commit()
