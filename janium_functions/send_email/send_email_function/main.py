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
import pytz

import requests
from bs4 import BeautifulSoup as Soup
from html2text import html2text
from sqlalchemy import or_, and_
from workdays import networkdays

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('send_email_function')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('send_email_function')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

# mtn_time = datetime.utcnow() - timedelta(hours=7)
PROJECT_ID = os.getenv('PROJECT_ID')

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
        "authorization": "Bearer {}".format(os.getenv('SENDGRID_API_KEY'))
    }
    return headers

def get_sendgrid_sender(sender_id):
    url = "https://api.sendgrid.com/v3/verified_senders"

    res = requests.request("GET", url, headers=get_sendgrid_headers())
    if res.ok:
        res_json = res.json()
        # pprint(res_json)
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
    opt_out_url = "https://us-central1-{}.cloudfunctions.net/email-opt-out-function".format(PROJECT_ID)
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

def send_email_with_sendgrid(details, session, account_local_time):
    url = "https://api.sendgrid.com/v3/mail/send"

    action_id = str(uuid4())
    # api_key = get_sendgrid_key()
    sender = get_sendgrid_sender(details['sendgrid_sender_id'])

    # message = add_footer(details['email_body'], details['contact_id'], details['contact_email'])
    message = details['email_body']

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
            action = Action(action_id, details["contact_id"], 4, datetime.utcnow(), message, to_email_addr=details['contact_email'])
            session.add(action)
            session.commit()
            return details['contact_email']
    except Exception as err:
        logger.error(str("There was an error while sending an email to {} for account {}. Error: {}".format(details['contact_email'], sender['from_name'], err)))
        return None

def send_email(details, session, account_local_time):
    username, password = details['email_creds']

    recipient = details['contact_email']

    contact_id = details['contact_id']
    action_id = str(uuid4())

    main_email = EmailMessage()
    main_email.make_alternative()


    main_email['Subject'] = details['email_subject']
    main_email['From'] = str(Header('{} <{}>')).format(details['from_full_name'], username)
    main_email['To'] = recipient
    main_email['Message-ID'] = make_msgid()
    main_email.add_header('Action-ID', action_id) 
    main_email['MIME-Version'] = '1.0'

    # email_html = add_tracker(details['email_body'], contactid, messageid)
    # email_html = add_footer(details['email_body'], contact_id, details['contact_email'])
    email_html = details['email_body']
    email_html = email_html.replace(r"{FirstName}", details['contact_first_name'])

    main_email.add_alternative(html2text(email_html), 'plain')
    main_email.add_alternative(email_html, 'html')


    try:
        with smtplib.SMTP(details['smtp_address'], 587) as server:
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.send_message(main_email)
            # print("Sent an email to {} for account {}".format(details['contactid'], details['account_fullname']))

        action = Action(action_id, contact_id, 4, datetime.utcnow(), email_html, to_email_addr=recipient)
        session.add(action)
        session.commit()
        return details['contact_email']

    except Exception as err:
        logger.error(str("There was an error while sending an email to {} for account {}. Error: {}".format(details['contact_email'], details['account_full_name'], err)))
        return None

def get_email_targets(account, janium_campaign, is_sendgrid, account_local_time):
    # steps = janium_campaign.janium_campaign_steps.filter(Janium_campaign_step.janium_campaign_step_type_id == 2).order_by(Janium_campaign_step.janium_campaign_step_delay).all()
    steps = janium_campaign.janium_campaign_steps.filter(Janium_campaign_step.janium_campaign_step_type_id != 4).order_by(Janium_campaign_step.janium_campaign_step_delay).all()

    ### Only get contacts who have not been email blacklisted or who have bounced email actions ###
    contacts = [
        contact 
        for contact 
        in janium_campaign.contacts
        if not contact.actions.filter(Action.action_type_id.in_([7,15])).first() and len(contact.get_emails()) > 0
    ]

    email_targets_list = []
    for contact in contacts:
        if previous_received_messages := contact.actions.filter(Action.action_type_id.in_([2, 6, 11, 21])).order_by(Action.action_timestamp.desc()).all():
            if continue_campaign_action := contact.actions.filter(Action.action_type_id == 14).order_by(Action.action_timestamp.desc()).first():
                if previous_received_messages[0].action_timestamp > continue_campaign_action.action_timestamp:
                    continue
            else:
                continue

        if cnxn_action := contact.actions.filter(Action.action_type_id == 1).order_by(Action.action_timestamp.desc()).first():
            sent_emails = contact.actions.filter(Action.action_type_id == 4).filter(Action.action_timestamp >= cnxn_action.action_timestamp).order_by(Action.action_timestamp.desc()).all()
            num_sent_emails = len(sent_emails) if sent_emails else 0
            last_sent_email = sent_emails[0] if sent_emails else None

            if continue_campaign_action := contact.actions.filter(Action.action_type_id == 14).order_by(Action.action_timestamp.desc()).first():
                cnxn_timestamp = cnxn_action.action_timestamp
                if last_sent_email:
                    days_to_add = networkdays(last_sent_email.action_timestamp, continue_campaign_action.action_timestamp) - 1
                else:
                    days_to_add = networkdays(previous_received_messages[0].action_timestamp, continue_campaign_action.action_timestamp) - 1
                while days_to_add > 0:
                    cnxn_timestamp += timedelta(days=1)
                    if cnxn_timestamp.weekday() >= 5: # sunday = 6
                        continue
                    days_to_add -= 1
            else:
                cnxn_timestamp = cnxn_action.action_timestamp
            
            cnxn_timestamp = pytz.utc.localize(cnxn_timestamp).astimezone(pytz.timezone(account.time_zone.time_zone_code)).replace(tzinfo=None)
            day_diff = networkdays(cnxn_timestamp, account_local_time) - 1

            for i, step in enumerate(steps):
                add_contact = False
                if step.janium_campaign_step_type_id == 2:
                    if i + 1 < len(steps):
                        if step.janium_campaign_step_delay <= day_diff < steps[i + 1].janium_campaign_step_delay:
                            if num_sent_emails < i + 1:
                                add_contact = True
                                body = step.janium_campaign_step_body
                                subject = step.janium_campaign_step_subject
                                break
                            else:
                                continue
                        else: 
                            continue
                    else:
                        if step.janium_campaign_step_delay <= day_diff <= step.janium_campaign_step_delay + 1:
                            if num_sent_emails < i + 1:
                                add_contact = True
                                body = step.janium_campaign_step_body
                                subject = step.janium_campaign_step_subject
                                break
                            else:
                                continue
                        else:
                            continue
        else: # Pre connection email targets made possible by data enrichment
            if cnxn_req_action := contact.actions.filter(Action.action_type_id == 19).order_by(Action.action_timestamp.desc()).first():
                sent_emails = contact.actions.filter(Action.action_type_id == 4).filter(Action.action_timestamp >= cnxn_req_action.action_timestamp).order_by(Action.action_timestamp.desc()).all()
                num_sent_emails = 0
                last_sent_email = None
                if sent_emails:
                    last_sent_email = sent_emails[0]
                    num_sent_emails = len(sent_emails)

                if len(contact.get_emails()):
                    cnxn_req_timestamp = pytz.utc.localize(cnxn_req_action.action_timestamp).astimezone(pytz.timezone(account.time_zone.time_zone_code)).replace(tzinfo=None)
                    day_diff = networkdays(cnxn_req_timestamp, account_local_time) - 1

                    steps = janium_campaign.janium_campaign_steps.filter(Janium_campaign_step.janium_campaign_step_type_id == 4).order_by(Janium_campaign_step.janium_campaign_step_delay).all()
                    for i, step in enumerate(steps):
                        add_contact = False
                        if i + 1 < len(steps):
                            if step.janium_campaign_step_delay <= day_diff < steps[i + 1].janium_campaign_step_delay:
                                # print(i + 1)
                                if num_sent_emails < i + 1:
                                    print(i + 1)
                                    add_contact = True
                                    body = step.janium_campaign_step_body
                                    subject = step.janium_campaign_step_subject
                                    break
                        else:
                            if step.janium_campaign_step_delay <= day_diff < step.janium_campaign_step_delay + 2:
                                if num_sent_emails < i + 1:
                                    add_contact = True
                                    body = step.janium_campaign_step_body
                                    subject = step.janium_campaign_step_subject
                                    break
        if add_contact:
            email_targets_list.append(
                {
                    "is_sendgrid": is_sendgrid,
                    "sendgrid_sender_id": janium_campaign.email_config.sendgrid_sender_id if is_sendgrid else None,
                    "from_full_name": janium_campaign.email_config.from_full_name,
                    "smtp_address": None if is_sendgrid else janium_campaign.email_config.email_server.smtp_address,
                    "smtp_port": None if is_sendgrid else janium_campaign.email_config.email_server.smtp_tls_port,
                    "email_creds": None if is_sendgrid else (janium_campaign.email_config.credentials.username, janium_campaign.email_config.credentials.password),
                    "contact_id": contact.contact_id,
                    "contact_first_name": contact.contact_info['ulinc']['first_name'],
                    "contact_full_name": str(contact.contact_info['ulinc']['first_name'] + ' ' + contact.contact_info['ulinc']['last_name']),
                    "contact_email": contact.get_emails()[0],
                    "email_subject": subject,
                    "email_body": body
                }
            )
    return email_targets_list

def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    session = get_session()

    if account := session.query(Account).filter(Account.account_id == payload_json['account_id']).first():
        account_local_time = datetime.now(pytz.timezone('UTC')).astimezone(pytz.timezone(account.time_zone.time_zone_code)).replace(tzinfo=None)
        for janium_campaign in account.janium_campaigns:
            is_sendgrid = True if janium_campaign.email_config.is_sendgrid and janium_campaign.email_config.sendgrid_sender_id else False
            effective_dates_dict = janium_campaign.get_effective_dates(account.time_zone.time_zone_code)
            queue_times_dict = janium_campaign.get_queue_times(account.time_zone.time_zone_code)
            if (effective_dates_dict['start'] <= account_local_time <= effective_dates_dict['end']) and (queue_times_dict['start'].hour <= account_local_time.hour <= queue_times_dict['end'].hour):
                email_targets_list = get_email_targets(account, janium_campaign, is_sendgrid, account_local_time)
                pprint(email_targets_list)

                ### Divide the email targets list to evenly distribute over the queue start and end time ###
                xx = int((queue_times_dict['end'].hour - queue_times_dict['start'].hour) / 0.5)

                # recipient_list = []
                # for email_target in email_targets_list[0:xx]:
                #     if email_target['is_sendgrid']:
                #         send_email_res = send_email_with_sendgrid(email_target, session, account_local_time)
                #     else:
                #         send_email_res = send_email(email_target, session, account_local_time)
                #     recipient_list.append({"contact_full_name": email_target['contact_full_name'], "contact_email_address": email_target['contact_email'], "contact_id": email_target['contact_id']})
                # logger_message = 'Sent emails to {} for account {} in campaign {} with {}'.format(recipient_list, account.account_id, janium_campaign.janium_campaign_name, 'sendgrid' if is_sendgrid else 'email app')
                # logger.info(logger_message)

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
    # session = get_session()
    # action1 = session.query(Action).filter(Action.action_type_id == 1).first()
    # action2 = session.query(Action).filter(Action.action_type_id == 11).first()

    # print(networkdays(action1.action_timestamp, datetime.now(), holidays=[]))
    # print(networkdays(action1.action_timestamp, action2.action_timestamp, holidays=[]))
    # get_sendgrid_sender('123')
