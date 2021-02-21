import base64
import json
import logging
import os
from datetime import datetime, timedelta
from uuid import uuid4

import requests
from nameparser import HumanName
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # pylint: disable=no-member

if not os.getenv('LOCAL_DEV'):
    from model import *
    from model_types import *
    import demoji_module as demoji
    demoji.download_codes()

    logger = logging.getLogger('poll_webhook')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *
    from db.model_types import *
    import janium_functions.poll_webhook.poll_webhook_function.demoji_module as demoji

    logger = logging.getLogger('poll_webhook')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)

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

def create_new_contact(contact_info, client_id, campaign_id, existing_ulinc_campaign_id, wh_id):
    data = {**base_contact_dict, **contact_info}
    name = scrub_name(data['first_name'] + ' ' + data['last_name'])
    return Contact(
        str(uuid4()),
        client_id,
        campaign_id,
        existing_ulinc_campaign_id,
        wh_id,
        data['id'],
        data['campaign_id'],
        str(name.first).replace(" ", ""),
        str(name.last).replace(" ", ""),
        data['title'],
        data['company'],
        data['location'],
        data['email'],
        None,
        None,
        data['phone'],
        data['website'],
        data['profile'],
        None
    )

def poll_webhook(wh_url, webhook_type):
    try:
        if not os.getenv('LOCAL_DEV'):
            return requests.get(wh_url, verify=False).json()
        else:
            f = open('./janium_functions/poll_webhook/poll_webhook_function/webhook_sample_data/{}.json'.format(webhook_type), 'r')
            return json.loads(f.read())
    except Exception as err:
        print('Error in polling this webhook url: {} \nError: {}'.format(wh_url, err))

def handle_webhook_response(client, webhook_response_id, session):
    webhook_response = session.query(Webhook_response).filter(Webhook_response.webhook_response_id == webhook_response_id).first()
    for item in webhook_response.webhook_response_value:
        existing_contact = session.query(Contact).filter(Contact.ulinc_id == str(item['id'])).first() # if contact exists in the contact table
        existing_ulinc_campaign = session.query(Ulinc_campaign).filter(Ulinc_campaign.client_id == client.client_id).filter(Ulinc_campaign.ulinc_ulinc_campaign_id == str(item['campaign_id'])).first()
        if webhook_response.webhook_response_type_id == webhook_response_type_dict['ulinc_new_connection']['id']:
            if existing_contact: # if contact exists in the contact table
                if len([action for action in existing_contact.actions if action.action_type_id == webhook_response_type_dict['ulinc_new_connection']['id']]) > 0:
                    pass
                else:
                    connection_action = Action(str(uuid4()), existing_contact.contact_id, webhook_response_type_dict['ulinc_new_connection']['id'], None, None)
                    session.add(connection_action)
            else:
                if existing_ulinc_campaign:
                    existing_ulinc_campaign_id = existing_ulinc_campaign.ulinc_campaign_id
                    if existing_ulinc_campaign.parent_janium_campaign:
                        janium_campaign_id = existing_ulinc_campaign.parent_janium_campaign.janium_campaign_id
                    else:
                        janium_campaign_id = Janium_campaign.unassigned_janium_campaign_id # Unassigned janium campaign id value
                else:
                    existing_ulinc_campaign_id = Ulinc_campaign.unassigned_ulinc_campaign_id
                    janium_campaign_id = Janium_campaign.unassigned_janium_campaign_id # Unassigned janium campaign id value
                
                new_contact = create_new_contact(item, client.client_id, janium_campaign_id, existing_ulinc_campaign_id, webhook_response_id)
                connection_action = Action(str(uuid4()), new_contact.contact_id, action_type_dict['li_new_connection']['id'], mtn_time, None)
                session.add(new_contact)
                session.add(connection_action)
        elif webhook_response.webhook_response_type_id == webhook_response_type_dict['ulinc_new_message']['id']:
            if existing_contact:
                contact_id = existing_contact.contact_id
            else:
                if existing_ulinc_campaign:
                    new_contact = create_new_contact(item, client.client_id, existing_ulinc_campaign.parent_janium_campaign.janium_campaign_id, existing_ulinc_campaign.ulinc_campaign_id, webhook_response_id)
                else:
                    new_contact = create_new_contact(item, client.client_id, Janium_campaign.unassigned_janium_campaign_id, Ulinc_campaign.unassigned_ulinc_campaign_id, webhook_response_id)
                session.add(new_contact)
                contact_id = new_contact.contact_id
            new_message_action = Action(
                str(uuid4()),
                contact_id,
                action_type_dict['li_new_message']['id'],
                datetime.strptime(item['time'], "%B %d, %Y, %I:%M %p") - timedelta(hours=2),
                item['message']
            )
            session.add(new_message_action)
        elif webhook_response.webhook_response_type_id == webhook_response_type_dict['ulinc_send_message']['id']:
            if existing_contact:
                contact_id = existing_contact.contact_id
            else:
                if existing_ulinc_campaign:
                    new_contact = create_new_contact(item, client.client_id, existing_ulinc_campaign.parent_janium_campaign.janium_campaign_id, existing_ulinc_campaign.ulinc_campaign_id, webhook_response_id)
                else:
                    new_contact = create_new_contact(item, client.client_id, Janium_campaign.unassigned_janium_campaign_id, Ulinc_campaign.unassigned_ulinc_campaign_id, webhook_response_id)
                session.add(new_contact)
                contact_id = new_contact.contact_id

            if existing_ulinc_campaign:
                if existing_ulinc_campaign.parent_janium_campaign.is_messenger:
                    if existing_origin_message := session.query(Action).filter(Action.contact_id == contact_id).filter(Action.action_id == action_type_dict['ulinc_origin_messenger_message']['id']).first():
                        is_origin = False
                    else:
                        is_origin = True
                else:
                    is_origin = False
            else:
                is_origin = False

            if is_origin:
                new_action = Action(
                    str(uuid4()),
                    contact_id,
                    action_type_dict['ulinc_origin_messenger_message']['id'],
                    datetime.strptime(item['time'], "%B %d, %Y, %I:%M %p") - timedelta(hours=2),
                    item['message']
                )
            else:
                new_action = Action(
                    str(uuid4()),
                    contact_id,
                    action_type_dict['li_send_message']['id'],
                    datetime.strptime(item['time'], "%B %d, %Y, %I:%M %p") - timedelta(hours=2),
                    item['message']
                )
            session.add(new_action)
        else:
            logger.error('Unknown webhook response type')

        session.commit()

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    client = session.query(Client).filter(Client.client_id == payload_json['client_id']).first()
    
    webhooks = [
        {"url": client.ulinc_config.new_connection_webhook, "type": "ulinc_new_connection"},
        {"url": client.ulinc_config.new_message_webhook, "type": "ulinc_new_message"},
        {"url": client.ulinc_config.send_message_webhook, "type": "ulinc_send_message"}
    ]

    webhook_response_id_list = []
    empty_webhook_responses = []
    for webhook in webhooks:
        webhook_request_response = poll_webhook(webhook['url'], webhook['type'])
        if len(webhook_request_response) > 0:
            webhook_response = Webhook_response(str(uuid4()), client.client_id, webhook_request_response, webhook_response_type_dict[webhook['type']]['id'])
            session.add(webhook_response)
            webhook_response_id_list.append(webhook_response.webhook_response_id)
        else:
            empty_webhook_responses.append(webhook['type'])
    session.commit()
    logger.info('Empty Webhooks for client {}: {}'.format(client.full_name, empty_webhook_responses))

    if len(webhook_response_id_list) > 0:
        for webhook_response_id in webhook_response_id_list:
            handle_webhook_response(client, webhook_response_id, session)
    logger.info('Polled webhooks for {}'.format(client.full_name))


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
