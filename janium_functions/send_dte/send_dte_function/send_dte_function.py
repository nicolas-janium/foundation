import base64
import json
import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.header import Header
from email.message import EmailMessage
from pprint import pprint

from bs4 import BeautifulSoup as Soup
from sqlalchemy import and_, or_
from workdays import networkdays, workday

if not os.getenv('LOCAL_DEV'):
    from model import *
    logger = logging.getLogger('send_dte_function')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('send_dte_function')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)
PROJECT_ID = os.getenv('PROJECT_ID')

def populate_table(email_body, data_set_dict, client_id):
    soup = Soup(email_body, 'html.parser')
    if data_set_dict['type'] == 'connection':
        tbody = soup.find("div", id="new-connections").tbody
    elif data_set_dict['type'] == 'message':
        tbody = soup.find("div", id="new-messages").tbody
    elif data_set_dict['type'] == 'voicemail':
        tbody = soup.find("div", id="new-voicemail-tasks").tbody
    for i, row in enumerate(data_set_dict['data']):
        tr_tag = soup.new_tag("tr", **{'class': 'table-row'})
        for j, item in enumerate(row):
            if i % 2 == 0:
                if j == 0:
                    if data_set_dict['type'] == 'connection':
                        redirect_url = "https://us-central1-{}.cloudfunctions.net/dte-profile-redirect-function?contact_id={}&redirect_url={}&from=connection".format(PROJECT_ID, row[8], str(row[7]))
                    elif data_set_dict['type'] == 'message':
                        redirect_url = "https://us-central1-{}.cloudfunctions.net/dte-profile-redirect-function?contact_id={}&redirect_url={}&from=message".format(PROJECT_ID, row[9], str(row[8]))
                    else:
                        redirect_url = "https://us-central1-{}.cloudfunctions.net/dte-profile-redirect-function?contact_id={}&redirect_url={}&from=voicemail".format(PROJECT_ID, row[6], str(row[7]))

                    td = soup.new_tag("td", **{'class': 'tg-kmlv'})
                    name = soup.new_tag("a", href=redirect_url)
                    name.string = str(item)
                    td.append(name)
                    tr_tag.append(td)
                elif j == 1:
                    if data_set_dict['type'] == 'connection':
                        td = soup.new_tag("td", **{'class': 'tg-kmlv'})
                        dq_url = "https://us-central1-{}.cloudfunctions.net/dte-dq-contact-function?contact_id={}&contact_full_name={}&client_id={}".format(PROJECT_ID, str(row[8]), str(row[0]), client_id)
                        dq_button = soup.new_tag("a", href=dq_url, **{'class': 'btn-remove', 'style': 'color:red'})
                        dq_button.string = 'DQ'
                        td.append(dq_button)
                        tr_tag.append(td)
                    elif data_set_dict['type'] == 'message':
                        td = soup.new_tag("td", **{'class': 'tg-kmlv'})
                        resume_url = "https://us-central1-{}.cloudfunctions.net/dte-resume-campaign-function?action_id={}&contact_full_name={}&contact_id={}&client_id={}".format(PROJECT_ID, str(row[10]), str(row[0]), str(row[9]), client_id)
                        resume_button = soup.new_tag("a", href=resume_url, **{'class': 'btn-continue', 'style': 'color:green'})
                        resume_button.string = 'Continue'
                        td.append(resume_button)
                        tr_tag.append(td)
                    else:
                        pass
                else:
                    td = soup.new_tag("td", **{'class': 'tg-kmlv'})
                    td.string = str(item)
                    tr_tag.append(td)
            else:
                if j == 0:
                    if data_set_dict['type'] == 'connection':
                        redirect_url = "https://us-central1-{}.cloudfunctions.net/dte-profile-redirect-function?contact_id={}&redirect_url={}&from=connection".format(PROJECT_ID, row[8], str(row[7]))
                    elif data_set_dict['type'] == 'message':
                        redirect_url = "https://us-central1-{}.cloudfunctions.net/dte-profile-redirect-function?contact_id={}&redirect_url={}&from=message".format(PROJECT_ID, row[9], str(row[8]))
                    else:
                        redirect_url = "https://us-central1-{}.cloudfunctions.net/dte-profile-redirect-function?contact_id={}&redirect_url={}&from=voicemail".format(PROJECT_ID, row[6], str(row[7]))

                    td = soup.new_tag("td", **{'class': 'tg-vmfx'})
                    name = soup.new_tag("a", href=redirect_url)
                    name.string = str(item)
                    td.append(name)
                    tr_tag.append(td)
                elif j == 1:
                    if data_set_dict['type'] == 'connection':
                        td = soup.new_tag("td", **{'class': 'tg-vmfx'})
                        dq_url = "https://us-central1-{}.cloudfunctions.net/dte-dq-contact-function?contact_id={}&contact_full_name={}&client_id={}".format(PROJECT_ID, str(row[8]), str(row[0]), client_id)
                        dq_button = soup.new_tag("a", href=dq_url, **{'class': 'btn-remove', 'style': 'color:red'})
                        dq_button.string = 'DQ'
                        td.append(dq_button)
                        tr_tag.append(td)
                    elif data_set_dict['type'] == 'message':
                        td = soup.new_tag("td", **{'class': 'tg-vmfx'})
                        resume_url = "https://us-central1-{}.cloudfunctions.net/dte-resume-campaign-function?activityid={}&contact_full_name={}&contact_id={}&client_id={}".format(PROJECT_ID, str(row[10]), str(row[0]), str(row[9]), client_id)
                        resume_button = soup.new_tag("a", href=resume_url, **{'class': 'btn-continue', 'style': 'color:green'})
                        resume_button.string = 'Continue'
                        td.append(resume_button)
                        tr_tag.append(td)
                    else:
                        pass
                else:
                    td = soup.new_tag("td", **{'class': 'tg-vmfx'})
                    td.string = str(item)
                    tr_tag.append(td)
        new_tr_tag = soup.new_tag("tr", **{'class': 'table-row'})
        if data_set_dict['type'] == 'connection':
            for tag in tr_tag.find_all('td')[0:7]:
                new_tr_tag.append(tag)
        elif data_set_dict['type'] == 'message':
            for tag in tr_tag.find_all('td')[0:8]:
                new_tr_tag.append(tag)
        else:
            for tag in tr_tag.find_all('td')[0:6]:
                new_tr_tag.append(tag)
        tbody.append(new_tr_tag)
    return str(soup)

def tailor_email(email_body, client_ulinc_id, client_firstname):
    email_body = email_body.replace(r'{FirstName}', client_firstname)
    soup = Soup(email_body, 'html.parser')

    ulinc_inbox_tag = soup.find("a", id="ulinc-inbox")
    ulinc_inbox_tag['href'] = "https://ulinc.co/{}/all".format(client_ulinc_id)

    return str(soup)

def send_dte(email_body, subject, details):
    username, password = details['dte_sender_creds']

    main_email = EmailMessage()
    main_email['Subject'] = subject
    main_email['From'] = str(Header('{} <{}>')).format(details['dte_sender_name'], username)
    main_email['To'] = details['client_email']
    if details['assistant_email']:
        main_email['Cc'] = details['assistant_email']
    if details['campaign_management_email']:
        main_email['Bcc'] = details['campaign_management_email']

    main_email.set_content(email_body, 'html')

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.send_message(main_email)
        server.close()

        return details['client_email']
    except Exception as err:
        print(err)
        return None

def get_new_connections(client_id, session):
    nc_contacts = [
        contact for contact in session.query(Contact).filter(and_(Contact.ulinc_ulinc_campaign_id != '1', Contact.client_id == client_id, Contact.actions.any(Action.action_type_id == 1))).all()
        if not contact.actions.filter(Action.action_type_id.in_([2,3,4,6,8,11])).first()
    ]
    nc_contacts2 = []
    for contact in nc_contacts:
        if cnxn_date := contact.actions.filter(or_(Action.action_type_id == 1, Action.action_type_id == 14)).order_by(Action.action_type_id.desc()).first().action_timestamp:
            if networkdays(cnxn_date, mtn_time) <= 3:
                nc_contacts2.append(
                    [
                        contact.full_name,
                        'Place_holder',
                        contact.title,
                        contact.company,
                        contact.location,
                        contact.contact_ulinc_campaign.ulinc_campaign_name,
                        cnxn_date.date(),
                        contact.li_profile_url, 
                        contact.contact_id
                    ]
                )
    return nc_contacts2

def get_new_messages(client_id, session):
    nm_contacts = [
        contact for contact in session.query(Contact).filter(and_(Contact.ulinc_ulinc_campaign_id != '1', Contact.client_id == client_id, Contact.actions.any(Action.action_type_id.in_([2,6])))).all()
        if not contact.actions.filter(Action.action_type_id.in_([9,11])).first()
    ]
    nm_contacts2 = []
    for contact in nm_contacts:
        if msg_action := contact.actions.filter(or_(Action.action_type_id == 2, Action.action_type_id == 6)).order_by(Action.action_timestamp).first():
            if networkdays(msg_action.action_timestamp, mtn_time) <= 3:
                nm_contacts2.append(
                    [
                        contact.full_name,
                        'Place_holder',
                        contact.title,
                        contact.company,
                        contact.location,
                        contact.contact_ulinc_campaign.ulinc_campaign_name,
                        'LI' if msg_action.action_type_id == 2 else 'Email',
                        msg_action.action_timestamp.date(),
                        contact.li_profile_url,
                        contact.contact_id,
                        msg_action.action_id
                    ]
                )
    return nm_contacts2

def get_new_voicemail_tasks(client_id, vm_delay, session):
    vm_contacts = [
        contact for contact in session.query(Contact).filter(and_(Contact.ulinc_ulinc_campaign_id != '1', Contact.client_id == client_id, Contact.phone != None)).all()
        if not contact.actions.filter(Action.action_type_id.in_([2,6,10,11])).first()
    ]
    vm_contacts2 = []
    for contact in vm_contacts:
        if cnxn_date := contact.actions.filter(or_(Action.action_type_id == 1, Action.action_type_id == 14)).order_by(Action.action_type_id.desc()).first().action_timestamp:
            if vm_delay <= networkdays(cnxn_date, mtn_time) <= vm_delay + 3:
                vm_contacts2.append(
                    [
                        contact.full_name,
                        'Placeholder',
                        contact.title,
                        contact.company,
                        contact.location,
                        contact.phone,
                        contact.contact_ulinc_campaign.ulinc_campaign_name,
                        contact.contact_id,
                        contact.li_profile_url
                    ]
                )
    return vm_contacts2

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    client = session.query(Client).filter(Client.client_id == payload_json['client_id']).first()

    # logger.debug(client.full_name)
    client_group = client.client_group
    dte_sender = client_group.dte_sender
    details = {
        "client_id": client.client_id,
        "client_first_name": client.first_name,
        "client_email": client.alternate_dte_email if client.alternate_dte_email else client.primary_email,
        "client_ulinc_id": client.ulinc_config.client_ulinc_id,
        "campaign_management_email": client.campaign_management_email,
        "dte_sender_creds": (dte_sender.email_config.credentials.username, dte_sender.email_config.credentials.password),
        "dte_sender_name": dte_sender.full_name,
        "dte_id": client_group.dte_id,
        "assistant_email": client.assistant_email if client.is_assistant else None
    }
    # logger.debug(details)
    dte_subject = client_group.dte.subject
    dte_body = client_group.dte.body


    ### New Connection contacts for the New Connection table ###
    nc_contacts2 = get_new_connections(client.client_id, session)
    # logger.debug(nc_contacts2)

    ### New Messages contacts for the New Messages table ###
    nm_contacts2 = get_new_messages(client.client_id, session)

    ### New Voicemail contacts for the New Voicemail table ###
    vm_contacts2 = get_new_voicemail_tasks(client.client_id, client.voicemail_task_delay, session)
    # logger.debug(vm_contacts2)
    
    data_sets = [
        {"type": "connection", "data": nc_contacts2},
        {"type": "message", "data": nm_contacts2},
        {"type": "voicemail", "data": vm_contacts2}
    ]
    for data_set in data_sets:
        dte_body = populate_table(dte_body, data_set, client.client_id)

    dte_body = tailor_email(dte_body, details['client_ulinc_id'], client.first_name)

    send_dte_res = send_dte(dte_body, dte_subject, details)
    if send_dte_res:
        logger.info('Sent DTE to {}'.format({"client_id": client.client_id, "client_full_name": client.full_name}))
        return send_dte_res


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
