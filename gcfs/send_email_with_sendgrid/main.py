import base64
import html
import json
import os
import random
import smtplib
import string
from datetime import datetime, timedelta
from email.header import Header
from email.message import EmailMessage
from email.utils import make_msgid
from uuid import uuid4

import google.auth
import holidays
import html2text
import requests
from google.cloud import secretmanager
from google.oauth2 import service_account
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sal_db import Activity, Campaign, Client, Email_server, get_db_url
from db_model import Client, Campaign, Action, Session

if os.getenv('IS_CLOUD') == 'True':
    pass
else:
    from dotenv import load_dotenv
    load_dotenv()


def get_sendgrid_key():
    if os.getenv('IS_CLOUD') == 'True':
        creds, project = google.auth.default()
    else:
        creds = service_account.Credentials.from_service_account_file('/home/nicolas/gcp/key.json')
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    secret_name = "sendgrid-api-key"
    project_id = "janium0-0"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def get_sendgrid_headers():
    headers = {
        "authorization": "Bearer {}".format(get_sendgrid_key())
    }
    return headers

def get_sendgrid_sender(sender_id):
    url = "https://api.sendgrid.com/v3/verified_senders"

    res = requests.request("GET", url, headers=get_sendgrid_headers())
    if res.ok:
        res_json = res.json()
        if senders := res_json['results']:
            for sender in senders:
                if sender['id'] == sender_id:
                    return sender
        else:
            print("Get sender returned an empty array")
            return None
    else:
        print("Request to get sender failed. {}".format(res.text))
        return None

def send_email(details, session):
    url = "https://api.sendgrid.com/v3/mail/send"

    messageid = str(uuid4())
    api_key = get_sendgrid_key()
    sender = get_sendgrid_sender(details['sendgrid_sender_id'])

    if sender:
        payload = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": details['contact_email'],
                            "name": details['contact_firstname']
                        }
                    ],
                    "subject": details['email_subject']
                }
            ],
            "from": {
                "email": sender['from_email'],
                "name": sender['from_name']
            },
            "reply_to": {
                "email": sender['reply_to'],
                "name": sender['reply_to_name']
            },
            "content": [
                {
                    "type": "text/plain",
                    "value": html2text.html2text(details['email_body'])
                },
                {
                    "type": "text/html",
                    "value": details['email_body']
                }
            ],
            "headers": {"janium_message_id": messageid},
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
    else:
        print("Sender is empty")
        return None

    try:
        res = requests.post(url=url, json=payload, headers=get_sendgrid_headers())
        if res.ok:
            # print("Sent an email to {} for client {}".format(details['contactid'], sender['from_name']))
            if details['testing'] == 'true':
                pass
            else:
                action = Action(str(uuid4()), details["contact_id"], datetime.now() - timedelta(hours=7), 4, None, messageid, False, None)
                session.add(action)
                session.commit()
            return details['contact_email']
    except Exception as err:
        print("There was an error while sending an email to {} for client {}. Error: {}".format(details['contact_email'], sender['from_name'], err))
        return None

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    now = datetime.now()
    now_date = now.date()
    us_holidays = holidays.US()
    us_holidays.append(datetime(now.year, 12, 24)) # Christmas Eve
    us_holidays.append(datetime(now.year, 12, 31)) # New Years Eve
    us_holidays.append(datetime(now.year, 1, 1)) # New Years Day

    if payload_json['from'] == 'test sendgrid':
        client = session.query(Client).filter(Client.id == payload_json['data']['client_id']).first()
        campaign = session.query(Campaign).filter(Campaign.id == payload_json['data']['campaign_id']).first()

        payload_json['data']['sendgrid_sender_id'] = client.sendgrid_sender_id
        payload_json['data']['sendgrid_template_id'] = campaign.email_after_c_sendgrid_template_id

        send_email(payload_json['data'], session)
    else:
        if now_date not in us_holidays or payload_json['testing'] == 'true':
            if payload_json['testing'] == 'true':
                active_clients = session.query(Client).filter(Client.id == '63bf6eca-1d2b-11eb-9daa-42010a8002ff').all() # Nicolas Arnold Client record
            else:
                active_clients = session.query(Client).filter(Client.is_active == 1)\
                                                      .filter(Client.is_sending_emails == 1)\
                                                      .filter(Client.is_sendgrid == 1)\
                                                      .filter(Client.sendgrid_sender_id != None)\
                                                      .all()
            clients_list = []
            for client in active_clients:
                if client.is_sendgrid == 1 or client.id == '63bf6eca-1d2b-11eb-9daa-42010a8002ff':
                    active_campaigns = session.query(Campaign).filter(Campaign.client_id == client.id)\
                                                              .filter(Campaign.is_active == 1)\
                                                              .all()
                    for active_campaign in active_campaigns:
                        try:
                            email_targets_after_wm = []
                            followup1_email_targets = []
                            followup2_email_targets = []
                            followup3_email_targets = []
                            with db_engine.connect() as conn:
                                if active_campaign.is_messenger:
                                    if active_campaign.send_followup1_email == 1 and active_campaign.automate_followup1_email == 1 \
                                                                                 and active_campaign.followup1_email_body != None \
                                                                                 and active_campaign.followup1_email_subject != None:
                                        query = "call fetch_followup1_email_targets('{}', 'true');".format(active_campaign.id)
                                        followup1_email_targets = conn.execute(query)

                                    if active_campaign.send_followup2_email == 1 and active_campaign.automate_followup2_email == 1 \
                                                                                 and active_campaign.followup2_email_body != None \
                                                                                 and active_campaign.followup2_email_subject != None:
                                        query = "call fetch_followup2_email_targets('{}', 'true');".format(active_campaign.id)
                                        followup2_email_targets = conn.execute(query)

                                    if active_campaign.send_followup3_email == 1 and active_campaign.automate_followup3_email == 1 \
                                                                                 and active_campaign.followup3_email_body != None \
                                                                                 and active_campaign.followup3_email_subject != None:
                                        query = "call fetch_followup3_email_targets('{}', 'true');".format(active_campaign.id)
                                        followup3_email_targets = conn.execute(query)
                                else:
                                    if active_campaign.send_email_after_wm == 1 and active_campaign.automate_email_after_wm == 1 \
                                                                                and active_campaign.email_after_c_body != None \
                                                                                and active_campaign.email_after_c_subject != None:
                                        query = "call fetch_email_after_wm_targets('{}');".format(active_campaign.id)
                                        email_targets_after_wm = conn.execute(query)

                                    if active_campaign.send_followup1_email == 1 and active_campaign.automate_followup1_email == 1 \
                                                                                 and active_campaign.followup1_email_body != None \
                                                                                 and active_campaign.followup1_email_subject != None:
                                        query = "call fetch_followup1_email_targets('{}', 'false');".format(active_campaign.id)
                                        followup1_email_targets = conn.execute(query)

                                    if active_campaign.send_followup2_email == 1 and active_campaign.automate_followup2_email == 1 \
                                                                                 and active_campaign.followup2_email_body != None \
                                                                                 and active_campaign.followup2_email_subject != None:
                                        query = "call fetch_followup2_email_targets('{}', 'false');".format(active_campaign.id)
                                        followup2_email_targets = conn.execute(query)

                                    if active_campaign.send_followup3_email == 1 and active_campaign.automate_followup3_email == 1 \
                                                                                 and active_campaign.followup3_email_body != None \
                                                                                 and active_campaign.followup3_email_subject != None:
                                        query = "call fetch_followup3_email_targets('{}', 'false');".format(active_campaign.id)
                                        followup3_email_targets = conn.execute(query)

                            email_targets = list(email_targets_after_wm) + list(followup1_email_targets) + list(followup2_email_targets) + list(followup3_email_targets)

                            email_targets_list = []
                            for email_target in email_targets:
                                email_target_dict = {
                                    "contact_id": email_target[0],
                                    "contact_firstname": email_target[1],
                                    "contact_email": email_target[2],
                                    "email_subject": email_target[3],
                                    "email_body": str(email_target[4]).replace(r"{FirstName}", email_target[1]),
                                    "sendgrid_sender_id": active_campaign.sendgrid_sender_id if active_campaign.sendgrid_sender_id else client.sendgrid_sender_id,
                                    # "sendgrid_template_id": email_target[8],
                                    "trigger": payload_json['from'],
                                    "testing": payload_json['testing']
                                }
                                email_targets_list.append(email_target_dict)

                            recipient_list = []
                            # print(len(email_targets_list))
                            for item in email_targets_list:
                                recipient_list.append(send_email(item, session))
                            print("Sent emails to {} for client {} {} in campaign {}".format(recipient_list, client.firstname, client.lastname, active_campaign.name))
                        except Exception as err:
                            print("There was an error in fetching email_targets. Error: {}".format(err))
            # print('Sent emails for clients {}'.format(sorted(list(set(clients_list)))))
        else:
            print("It's a holiday!")

if __name__ == '__main__':
    payload = {
    "trigger-type": "function",
    "from": "test",
    "testing": "true"
    }
    payload = json.dumps(payload)

    payload = base64.b64encode(str(payload).encode("utf-8"))

    event = {
        "data": payload
    }

    main(event, 1)
