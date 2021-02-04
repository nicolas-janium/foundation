import base64
import json
import uuid
from datetime import datetime, timedelta

import requests
from nameparser import HumanName
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib3.exceptions import InsecureRequestWarning

import demoji_module as demoji
from model_db import (Client, Campaign, Ulinc_campaign, Contact, Activity, Webhook_res, Session)

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # pylint: disable=no-member


base_contact_dict = dict({
    'campaign_id': 0,
    'id': None,
    'first_name': None,
    'last_name': None,
    'title': None,
    'company': None,
    'location': None,
    'email': None,
    'phone': None,
    'website': None,
    'profile': None
})

def scrub_name(name):
    return HumanName(demoji.replace(name.replace(',', ''), ''))

def create_new_contact(contact_info, campaignid, clientid, wh_id, wh_type):
    data = {**base_contact_dict, **contact_info}
    contactid = str(uuid.uuid4())
    name = scrub_name(data['first_name'] + ' ' + data['last_name'])
    return Contact(
        contactid,
        str(campaignid),
        str(clientid),
        data['id'],
        data['campaign_id'],
        "internal_ulinc_campaign_id",
        str(name.first).replace(" ", ""),
        str(name.last).replace(" ", ""),
        data['title'],
        data['company'],
        data['location'],
        data['email'],
        data['phone'],
        data['website'],
        data['profile'],
        wh_id
    )

def create_new_action(contactid, action_timestamp, action_code, message, open_messageid, is_origin, ulinc_campaign_id):
    return Action(str(uuid.uuid4()), str(contactid), action_timestamp, action_code, message, open_messageid, is_origin, ulinc_campaign_id)

def save_webhook_res(clientid, res, res_type, session):
    resid = str(uuid.uuid4())
    if res_type == 'new_connection':
        inst = New_connection_wh_res(resid, clientid, res)
    elif res_type == 'new_message':
        inst = New_message_wh_res(resid, clientid, res)
    elif res_type == 'send_message':
        inst = Send_message_wh_res(resid, clientid, res)
    session.add(inst)
    session.commit()
    return resid

def poll_webhook(wh_url):
    try:
        return requests.get(wh_url, verify=False).json()
    except Exception as err:
        print('Error in polling this webhook url: {} \nError: {}'.format(wh_url, err))

def handle_jdata(client, wh_res_id_dict, session):
    wh_type = wh_res_id_dict['type']
    wh_id = wh_res_id_dict['id']

    if wh_type == 'new_connection':
        wh_res = session.query(New_connection_wh_res).filter(New_connection_wh_res.id == wh_id).first().jdata
        for item in wh_res:
            if contact := session.query(Contact).filter(Contact.ulinc_id == str(item['id'])).first(): # if contact exists in the contact table
                contact_id = contact.id
                if session.query(Action).filter(Action.contact_id == contact_id).filter(Action.action_code == 1).first(): # if activity exists in the Activity table
                    pass # activity DOES exist in Activity table
                else:
                    new_action = create_new_action(contact_id, None, 1, None, None, False, None)
                    session.add(new_action)
            else:
                if query := session.query(Ulinc_campaign).filter(Ulinc_campaign.client_id == client.id).filter(Ulinc_campaign.ulinc_campaign_id == str(item['campaign_id'])).first():
                    janium_campaign_id = query.janium_campaign_id
                else:
                    janium_campaign_id = 'a4fc093e-1551-11eb-9daa-42010a8002ff' # Unknown campaign/unassigned

                new_contact = create_new_contact(item, janium_campaign_id, client.id, wh_id, wh_type)
                contact_id = new_contact.id
                session.add(new_contact)
                new_action = create_new_action(contact_id, None, 1, None, None, False, None)
                session.add(new_action)

    elif wh_type in ('new_message', 'send_message'):
        if wh_type == 'new_message':
            wh_res = session.query(New_message_wh_res).filter(New_message_wh_res.id == wh_id).first().jdata
        else:
            wh_res = session.query(Send_message_wh_res).filter(Send_message_wh_res.id == wh_id).first().jdata
        for item in wh_res:
            # print(client.id, str(item['campaign_id']))
            ulinc_campaign = session.query(Ulinc_campaign).filter(Ulinc_campaign.client_id == client.id).filter(Ulinc_campaign.ulinc_campaign_id == str(item['campaign_id'])).first()
            if contact := session.query(Contact).filter(Contact.ulinc_id == str(item['id'])).first(): # if contact exists in the contact table
                contact_id = contact.id
            else:
                new_contact = create_new_contact(item, ulinc_campaign.janium_campaign_id if ulinc_campaign else 'a4fc093e-1551-11eb-9daa-42010a8002ff', client.id, wh_id, wh_type)
                contact_id = new_contact.id
                session.add(new_contact)
            is_origin = False
            if ulinc_campaign and wh_type == 'send_message':
                if ulinc_campaign.ulinc_is_messenger:
                    existing_origin_message = session.query(Action).filter(Action.contact_id == contactid)\
                                                                    .filter(Action.is_ulinc_messenger_origin == 1)\
                                                                    .filter(Action.ulinc_messenger_campaign_id == str(item['campaign_id']))\
                                                                    .first()
                    if existing_origin_message:
                        pass
                    else:
                        is_origin = True

            # new_activity = create_new_activity(contactid, datetime.strptime(item['time'], "%B %d, %Y, %I:%M %p") - timedelta(hours=2), 2 if wh_type == 'new_message' else 3, item['message'], None, False, None)
            new_activity = create_new_action(
                contact_id,
                datetime.strptime(item['time'], "%B %d, %Y, %I:%M %p") - timedelta(hours=2),
                2 if wh_type == 'new_message' else 3, item['message'],
                None,
                True if is_origin else False,
                str(item['campaign_id']) if is_origin else None
            )
            session.add(new_action)
    else:
        print('Webhook type ({}) not recognized'.format(wh_type))
        return

    session.commit()

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    if payload_json['from'].lower() == 'test':
        active_clients = session.query(Client).filter(Client.id == 'e98f3c45-2f62-11eb-865a-42010a3d0004').all()
    else:
        active_clients = session.query(Client).filter(Client.is_active == 1).filter(Client.new_connection_wh != None).all()

    polled_clients = []
    for client in active_clients:
        webhooks = [
                {"url": client.new_connection_wh, "type": "new_connection"},
                {"url": client.new_message_wh, "type": "new_message"},
                {"url": client.send_message_wh, "type": "send_message"}
            ]
        wh_res_id_list = []
        empty_webhooks = []
        for wh in webhooks:
            wh_res = poll_webhook(wh['url'])
            polled_clients.append('{} {}'.format(client.firstname, client.lastname))
            if len(wh_res) > 0:
                wh_res_id = save_webhook_res(client.id, wh_res, wh['type'], session) #  Save the webhook response into the mysql instance
                wh_res_id_list.append(
                    {
                        'type': wh['type'],
                        'id': wh_res_id
                    }
                )
            else:
                empty_webhooks.append(wh['type'])
        print('Empty webhooks for client {} {}: {}'.format(client.firstname, client.lastname, empty_webhooks))

        if len(wh_res_id_list) > 0:
            for item_dict in wh_res_id_list:
                handle_jdata(client, item_dict, session) #  Handle the jdata from the webhook response by parsing and inserting into the contacts and activity tables
    print('Polled webhooks for {}'.format(sorted(list(set(polled_clients)))))
