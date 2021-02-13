import base64
import json
import logging
import os
import smtplib
import time
from datetime import datetime, timedelta
from email.header import Header
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from pprint import pprint
from uuid import uuid4

import google.auth
import holidays
import requests
from bs4 import BeautifulSoup as Soup
from google.cloud import secretmanager
from google.oauth2 import service_account
from html2text import html2text
from sqlalchemy import or_
from workdays import networkdays

from db_model import *

if os.getenv('IS_CLOUD') == 'True':
    logger = logging.getLogger('send_email')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    logger = logging.getLogger('send_email')
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

def get_sendgrid_sender(sender_id):
    url = "https://api.sendgrid.com/v3/verified_senders"

    res = requests.request("GET", url, headers=get_sendgrid_headers())
    if res.ok:
        res_json = res.json()
        if senders := res_json['results']:
            for sender in senders:
                if str(sender['id']) == sender_id:
                    return sender
        else:
            logger.warning("Get sender returned an empty array")
            return None
    else:
        logger.error(str("Request to get sender failed. {}".format(res.text)))
        return None

def add_footer(email_html, contact_id, contact_email):
    opt_out_url = str(os.getenv('EMAIL_OPT_OUT_URL'))
    opt_out_url += "?contact_id={}&landing=1&contact_email={}".format(contact_id, contact_email)
    soup = Soup(email_html, 'html.parser')
    div = soup.new_tag('div')
    email_preferences = r"""
        <p style="text-align: left;font-size: 10px;">Received this email by mistake? Click <a href="{opt_out_url}">here</a>.
        </p>
        """
    p_soup = Soup(email_preferences, 'html.parser')
    div.append(p_soup)
    soup.append(div)

    return str(soup).replace(r'{opt_out_url}', opt_out_url)

def send_email_with_sendgrid(details, session):
    url = "https://api.sendgrid.com/v3/mail/send"

    action_id = str(uuid4())
    api_key = get_sendgrid_key()
    sender = get_sendgrid_sender(details['sendgrid_sender_id'])

    message = add_footer(details['email_body'], details['contact_id'], details['contact_email'])

    if sender:
        payload = {
            "personalizations": [
                {
                    "to": [
                        {
                            "email": details['contact_email'],
                            "name": details['contact_first_name']
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
                    "value": html2text(message)
                },
                {
                    "type": "text/html",
                    "value": message
                }
            ],
            "headers": {"janium_action_id": action_id},
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
        logger.warning("Sender is empty")
        return None
    try:
        res = requests.post(url=url, json=payload, headers=get_sendgrid_headers())
        if res.ok:
            if details['testing'] == 'true':
                pass
            else:
                action = Action(action_id, details["contact_id"], 4, mtn_time, message)
                session.add(action)
                session.commit()
            return details['contact_email']
    except Exception as err:
        logger.error(str("There was an error while sending an email to {} for client {}. Error: {}".format(details['contact_email'], sender['from_name'], err)))
        return None

def send_email(details, session):
    username, password = details['email_creds']
    if details['testing'] == 'true':
        if details['mail-tester'] == 'true':
            recipient = 'narnold113-KFWW@srv1.mail-tester.com'
        else:
            recipient = 'nic@janium.io'
    else:
        recipient = details['contact_email']

    contact_id = details['contact_id']
    action_id = str(uuid4())

    main_email = EmailMessage()
    main_email.make_alternative()


    main_email['Subject'] = details['email_subject']
    main_email['From'] = str(Header('{} <{}>')).format(details['client_full_name'], username)
    main_email['To'] = recipient
    main_email['Message-ID'] = make_msgid()
    main_email.add_header('Action-ID', action_id) 
    main_email['MIME-Version'] = '1.0'

    # email_html = add_tracker(details['email_body'], contactid, messageid)
    email_html = add_footer(details['email_body'], contact_id, details['contact_email'])
    email_html = email_html.replace(r"{FirstName}", details['contact_first_name'])

    main_email.add_alternative(html2text(email_html), 'plain')
    main_email.add_alternative(email_html, 'html')


    try:
        with smtplib.SMTP(details['smtp_address'], 587) as server:
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.send_message(main_email)
            # print("Sent an email to {} for client {}".format(details['contactid'], details['client_fullname']))

        if details['testing'] == 'true' or details['mail-tester'] =='true':
            pass
        else:
            action = Action(action_id, contact_id, 4, mtn_time, email_html)
            session.add(action)
            session.commit()
        return details['contact_email']

    except Exception as err:
        logger.error(str("There was an error while sending an email to {} for client {}. Error: {}".format(details['contact_email'], details['client_fullname'], err)))
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

    if now_date not in us_holidays:
        if payload_json['testing'] == 'true':
            clients = session.query(Client).filter(Client.client_id == '8a52cdff-6722-4d26-9a6a-55fe952bbef1').all() # Jonny Karate
        else:
            clients = session.query(Client).filter(Client.is_active == 1)\
                                           .filter(Client.is_sending_emails == 1)\
                                           .filter(Client.email_config_id != Email_config.dummy_email_config_id)\
                                           .all()
        clients_list = []
        for client in clients:
            is_sendgrid = True if client.email_config.is_sendgrid and client.email_config.sendgrid_sender_id else False
            for janium_campaign in client.campaigns.filter(Janium_campaign.is_active == 1).all():
                logger.debug('{}'.format(janium_campaign.janium_campaign_name))

                # steps = janium_campaign.janium_campaign_steps.filter(Janium_campaign_step.janium_campaign_step_type_id == 2).order_by(Janium_campaign_step.janium_campaign_step_delay).all()
                steps = janium_campaign.janium_campaign_steps.order_by(Janium_campaign_step.janium_campaign_step_delay).all()

                contacts = [
                    contact 
                    for contact 
                    in janium_campaign.contacts.filter(Contact.email1 != None).order_by(Contact.full_name).all() 
                    if not contact.actions.filter(Action.action_type_id.in_([2,6,7,11,15])).first()
                ]
                email_targets_list = []
                for contact in contacts:
                    cnxn_date = contact.actions.filter(or_(Action.action_type_id == 1, Action.action_type_id == 14)).order_by(Action.action_type_id.desc()).first().action_timestamp
                    for i, step in enumerate(steps):
                        if step.janium_campaign_step_type_id == 2:
                            add_contact = False
                            if i + 1 < len(steps):
                                if step.janium_campaign_step_delay <= networkdays(cnxn_date, mtn_time) < steps[i + 1].janium_campaign_step_delay:
                                    add_contact = True
                            else:
                                if step.janium_campaign_step_delay <= networkdays(cnxn_date, mtn_time) < step.janium_campaign_step_delay + 2:
                                    add_contact = True
                            if add_contact:
                                email_targets_list.append(
                                    {
                                        "is_sendgrid": is_sendgrid,
                                        "sendgrid_sender_id": client.email_config.sendgrid_sender_id if is_sendgrid else None,
                                        "client_full_name": client.full_name,
                                        "smtp_address": None if is_sendgrid else client.email_config.email_server.smtp_address,
                                        "smtp_port": None if is_sendgrid else client.email_config.email_server.smtp_tls_port,
                                        "email_creds": None if is_sendgrid else (client.email_config.credentials.username, client.email_config.credentials.password),
                                        "contact_id": contact.contact_id,
                                        "contact_first_name": contact.first_name,
                                        "contact_email": contact.email1,
                                        "email_subject": step.janium_campaign_step_subject,
                                        "email_body": step.janium_campaign_step_body,
                                        "testing": payload_json['testing'],
                                        "mail-tester": payload_json['mail-tester']
                                        
                                    }
                                )
                recipient_list = []
                for email_target in email_targets_list:
                    logger.debug(email_target)
                #     if email_target['is_sendgrid']:
                #         send_email_res = send_email_with_sendgrid(email_target, session)
                #     else:
                #         send_email_res = send_email(email_target, session)
                #     recipient_list.append(send_email_res)
                #     clients_list.append(client.full_name)
                # logger.info('Sent emails to {} for client {} in campaign {} with {}'.format(recipient_list, client.full_name, janium_campaign.janium_campaign_name, 'sendgrid' if is_sendgrid else 'email app'))
    else:
        logger.info("It's a holiday!")

if __name__ == '__main__':
    payload = {
    "testing": "true",
    "mail-tester": "false"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)

    # print(get_sendgrid_sender('1326405'))
