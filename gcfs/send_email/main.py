import base64
import json
import os
import smtplib
from datetime import datetime, timedelta
from email.header import Header
from email.message import EmailMessage
from uuid import uuid4

import holidays
from bs4 import BeautifulSoup as Soup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sal_db import Activity, Campaign, Client, Email_server, get_db_url
from db_model import Client, Campaign, Action, Email_server, Session

if os.getenv('IS_CLOUD') == 'True':
    pass
else:
    from dotenv import load_dotenv
    load_dotenv()


def add_tracker(email_html, contactid, messageid):
    tracker_url = str(os.getenv('TRACKER_URL'))
    tracker_url += "?contactid={}&messageid={}".format(contactid, messageid)
    soup = Soup(email_html, 'html.parser')
    div = soup.new_tag('div')
    img = soup.new_tag('img', attrs={'height': '0', 'width': '0', 'src': tracker_url})
    div.append(img)
    soup.append(div)
    return str(soup)

def add_footer(email_html, contactid, contact_email):
    opt_out_url = str(os.getenv('EMAIL_OPT_OUT_URL'))
    opt_out_url += "?contactid={}&landing=1&contact_email={}".format(contactid, contact_email)
    soup = Soup(email_html, 'html.parser')
    div = soup.new_tag('div')
    email_preferences = r"""
        <p style="text-align: left;font-size: 10px;">Received this email by mistake? Click <a href="{opt_out_url}">here</a>.
        </p>
        """
        # <br>
        # Privacy and Confidentiality Notice: This e-mail message contains information that is confidential and/or privileged. 
        # If you are not the intended recipient, please advise the sender. Thank you.
    p_soup = Soup(email_preferences, 'html.parser')
    div.append(p_soup)
    soup.append(div)

    return str(soup).replace(r'{opt_out_url}', opt_out_url)

def send_email(details, session):
    username, password = details['email_creds']
    if details['trigger'] == 'test':
        recipient = 'nic@janium.io'
    else:
        recipient = details['contact_email']

    contactid = details['contact_id']
    messageid = str(uuid4())
    main_email = EmailMessage()

    main_email['Subject'] = details['email_subject']
    main_email['From'] = str(Header('{} <{}>')).format(details['client_fullname'], username)
    main_email['To'] = recipient
    main_email['Message-ID'] = messageid

    # email_html = add_tracker(details['email_body'], contactid, messageid)
    email_html = add_footer(details['email_body'], contactid, details['contact_email'])
    email_html = email_html.replace(r"{FirstName}", details['contact_firstname'])
    main_email.set_content(email_html, 'html')

    try:
        with smtplib.SMTP(details['client_smtp_address'], 587) as server:
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.send_message(main_email)
            # print("Sent an email to {} for client {}".format(details['contactid'], details['client_fullname']))

        if details['test'] == 'true':
            pass
        else:
            action = Action(str(uuid4()), contactid, datetime.now() - timedelta(hours=7), 4, email_html, messageid, False, None)
            session.add(action)
            session.commit()
        return details['contact_email']

    except Exception as err:
        print("There was an error while sending an email to {} for client {}. Error: {}".format(details['contact_email'], details['client_fullname'], err))
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

    if payload_json['from'] == 'test normal':
        client = session.query(Client).filter(Client.id == payload_json['data'][0]['client_id']).first()
        campaign = session.query(Campaign).filter(Campaign.id == payload_json['data'][0]['campaign_id']).first()
        email_server = session.query(Email_server).filter(Email_server.id == client.email_server_id).first()
        payload_json['data'][0]['client_fullname'] = client.firstname + ' ' + client.lastname
        payload_json['data'][0]['client_smtp_address'] = email_server.smtp_address
        payload_json['data'][0]['email_subject'] = campaign.email_after_c_subject
        payload_json['data'][0]['email_body'] = campaign.email_after_c_body
        payload_json['data'][0]['email_creds'] = (client.email_app_username, client.email_app_password)
        send_email(payload_json['data'][0], session)
    elif payload_json['from'] == 'janium-send-email-schedule':
        if now_date not in us_holidays:
            if payload_json['testing'] == 'true':
                active_clients = session.query(Client).filter(Client.id == '63bf6eca-1d2b-11eb-9daa-42010a8002ff').all() # Nicolas Arnold Client record
            else:
                active_clients = session.query(Client).filter(Client.is_active == 1)\
                                                      .filter(Client.is_sending_emails == 1)\
                                                      .filter(Client.email_server_id != None)\
                                                      .filter(Client.email_app_username != None)\
                                                      .filter(Client.email_app_password != None)\
                                                      .filter(Client.is_sendgrid == 0)\
                                                      .all()
            clients_list = []
            for client in active_clients:
                if client.is_sendgrid == 0 or client.id == '63bf6eca-1d2b-11eb-9daa-42010a8002ff':
                    active_campaigns = session.query(Campaign).filter(Campaign.client_id == client.id).filter(Campaign.is_active == 1).all()
                    for active_campaign in active_campaigns:
                        email_server = session.query(Email_server).filter(Email_server.id == active_campaign.email_server_id).first()
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
                                                                                and active_campaign.email_after_wm_body != None \
                                                                                and active_campaign.email_after_wm_subject != None:
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
                            # print("Email targets for client {}: {}".format(client.firstname, email_targets))

                            email_targets_list = []
                            for email_target in email_targets:
                                email_target_dict = {
                                    "contact_id": email_target[0],
                                    "contact_firstname": email_target[1],
                                    "contact_email": email_target[2],
                                    "email_subject": email_target[3],
                                    "email_body": email_target[4],
                                    "client_fullname": email_target[5],
                                    "client_smtp_address": email_server.smtp_address if email_server else email_target[6],
                                    "email_creds": (active_campaign.email_app_username, active_campaign.email_app_password) if email_server else (client.email_app_username, client.email_app_password),
                                    "trigger": payload_json['from'],
                                    "test": payload_json['testing']
                                }
                                email_targets_list.append(email_target_dict)

                            recipient_list = []
                            for item in email_targets_list:
                                recipient_list.append(send_email(item, session))
                                clients_list.append('{} {}'.format(client.firstname, client.lastname))
                                if payload_json['from'].lower() == 'test':
                                    print('Sent emails for clients {}'.format(sorted(list(set(clients_list)))))
                                    return
                            print("Sent emails to {} for client {} {} in campaign {}".format(recipient_list, client.firstname, client.lastname, active_campaign.name))
                        except Exception as err:
                            print("There was an error in fetching email_targets. Error: {}".format(err))
            # print('Sent emails for clients {}'.format(sorted(list(set(clients_list)))))
        else:
            print("It's a holiday!")
    else:
        pass
