import base64
import json
import os
import smtplib
from email.header import Header
from email.message import EmailMessage
from datetime import datetime, timedelta

from bs4 import BeautifulSoup as Soup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from workdays import networkdays

from db_model import Client, Dte, Dte_sender, Session

mtn_time = datetime.utcnow() - timedelta(hours=7)


def populate_table(email_body, data_set_dict):
    soup = Soup(email_body, 'html.parser')
    if data_set_dict['type'] == 'connection':
        tbody = soup.find("div", id="new-connections").tbody
    elif data_set_dict['type'] == 'message':
        tbody = soup.find("div", id="new-messages").tbody
    for i, row in enumerate(data_set_dict['data']):
        tr_tag = soup.new_tag("tr", **{'class': 'table-row'})
        if i % 2 == 0:
            pass
        else:
            pass


        for j, item in enumerate(row):
            if j == 6:
                break
            if i % 2 == 0:
                if j == 0:
                    td = soup.new_tag("td", **{'class': 'tg-kmlv'})
                    if data_set_dict['type'] == 'connection':
                        redirect_url = str(os.getenv('DTE_PROFILE_REDIRECT_URL')) + '?contactid={}&redirect_url={}'.format(str(row[7]), str(row[6]))
                        name = soup.new_tag("a", href=redirect_url)
                    else:
                        name = soup.new_tag("a", href=str(row[6]))
                    name.string = str(item)
                    td.append(name)
                    tr_tag.append(td)
                else:
                    td = soup.new_tag("td", **{'class': 'tg-kmlv'})
                    td.string = str(item)
                    tr_tag.append(td)
            else:
                if j == 0:
                    td = soup.new_tag("td", **{'class': 'tg-vmfx'})
                    if data_set_dict['type'] == 'connection':
                        redirect_url = str(os.getenv('DTE_PROFILE_REDIRECT_URL')) + '?contactid={}&redirect_url={}'.format(str(row[7]), str(row[6]))
                        name = soup.new_tag("a", href=redirect_url)
                    else:
                        name = soup.new_tag("a", href=str(row[6]))
                    name.string = str(item)
                    td.append(name)
                    tr_tag.append(td)
                else:
                    td = soup.new_tag("td", **{'class': 'tg-vmfx'})
                    td.string = str(item)
                    tr_tag.append(td)
        tbody.append(tr_tag)
    return str(soup)

def tailor_email(email_body, client_ulinc_id, client_firstname):
    email_body = email_body.replace(r'{FirstName}', client_firstname)
    soup = Soup(email_body, 'html.parser')

    ulinc_inbox_tag = soup.find("a", id="ulinc-inbox")
    ulinc_inbox_tag['href'] = "https://ulinc.co/{}/all".format(client_ulinc_id)

    # ulinc_dashboard_tag = soup.find("a", id="ulinc-dashboard")
    # ulinc_dashboard_tag['href'] = "https://ulinc.co/{}/".format(client_ulinc_id)

    return str(soup)

def send_email(email_body, subject, details, session):
    username, password = details['dte_sender_creds']

    main_email = EmailMessage()
    if details['trigger'].lower() == 'test':
        main_email['Subject'] = 'Test for send-daily-tasks-function'
        main_email['From'] = str(Header('{} <{}>')).format('Tester', username)
        main_email['To'] = 'nic@janium.io'
    else:
        main_email['Subject'] = subject
        main_email['From'] = str(Header('{} <{}>')).format(details['dte_sender_name'], username)
        main_email['To'] = details['client_dte_email'] if details['client_dte_email'] else details['client_email']
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
    except Exception as err:
        print(err)
    finally:
        server.close()

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    active_clients = session.query(Client).filter(Client.is_active == 1).filter(Client.is_dte == 1).filter(Client.dte_id != None).all()

    recipients_list = []
    for client in active_clients:
        dte_sender = client.client_dte_sender

        details = {
            "client_id": client.id,
            "client_firstname": client.firstname,
            "client_email": client.email,
            "client_dte_email": client.dte_email,
            "client_ulinc_id": client.ulinc_id,
            "campaign_management_email": client.campaign_management_email,
            "dte_sender_creds": (dte_sender.email_app_username, dte_sender.email_app_password),
            "dte_sender_name": dte_sender.fullname,
            "dte_id": client.dte_id,
            "assistant_email": client.assistant_email,
            "trigger": payload_json['from']
        }

        contacts = client.contacts
        new_connections = []
        new_messages = []
        for contact in contacts:
            actions = contact.actions
            last_action = actions[0]
            if (
                last_action.action_code == 1 and \
                networkdays(last_action.dateadded, mtn_time) in range(7) and \
                str(contact.ulinc_campaign_id) != '1'
            ):
                new_connections.append(contact)
            elif (
                last_action.action_code == 2 and \
                networkdays(last_action.action_timestamp, mtn_time) in range(3) and \
                str(contact.ulinc_campaign_id) != '1'
            ):
                new_messages.append(contact)

        data_sets = [
            {
                'type': 'connection',
                'data': new_connections
            },
            {
                'type': 'message',
                'data': new_messages
            }
        ]

        client_dte = client.client_dte
        email_body = client_dte.body
        email_subject = client_dte.subject
        # for data_set in data_sets:
        #     email_body = populate_table(email_body, data_set)

        # email_body = tailor_email(email_body, details['client_ulinc_id'], details['client_firstname'])
        # send_email(email_body, email_subject, details, session)
        # recipients_list.append('{} {}'.format(client.firstname, client.lastname))
    print('Sent the daily tasks email to {}'.format(sorted(recipients_list)))

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
