import base64
import json
import logging
import os
from datetime import datetime, timedelta
from uuid import uuid4
import pytz
from pprint import pprint

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

mtn_tz = pytz.timezone('US/Mountain')
mtn_time = datetime.now(pytz.timezone('UTC')).astimezone(mtn_tz)

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

def create_new_contact(contact_info, account_id, campaign_id, existing_ulinc_campaign_id, contact_source_id):
    data = {**base_contact_dict, **contact_info}
    name = scrub_name(data['first_name'] + ' ' + data['last_name'])
    return Contact(
        str(uuid4()),
        contact_source_id,
        account_id,
        campaign_id,
        existing_ulinc_campaign_id,
        data['id'],
        data['campaign_id'],
        {
            'ulinc': {
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'title': data['title'],
                'company': data['company'],
                'location': data['location'],
                'email': data['email'],
                'phone': data['phone'],
                'website': data['website'],
                'li_salesnav_profile_url': None,
                'li_profile_url': data['profile']
            }
        },
        None,
        User.system_user_id
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

def handle_webhook_response(account, contact_source_id, session):
    webhook_response = session.query(Contact_source).filter(Contact_source.contact_source_id == contact_source_id).first()
    for item in webhook_response.contact_source_json:
        existing_contact = session.query(Contact).filter(Contact.ulinc_id == str(item['id'])).first() # if contact exists in the contact table
        existing_ulinc_campaign = session.query(Ulinc_campaign).filter(Ulinc_campaign.account_id == account.account_id).filter(Ulinc_campaign.ulinc_ulinc_campaign_id == str(item['campaign_id'])).first()
        if webhook_response.contact_source_type_id == 1:
            if existing_contact: # if contact exists in the contact table
                # if len([action for action in existing_contact.actions if action.action_type_id == action_type_dict['ulinc_new_connection']['id']]) > 0:
                if existing_cnxn_action := existing_contact.actions.filter(Action.action_type_id == 1).first():
                    pass
                else:
                    existing_contact_info = json.loads(existing_contact.contact_info)
                    new_contact_info = {**base_contact_dict, **item}
                    existing_contact_info['ulinc']['email'] = new_contact_info['email']
                    existing_contact_info['ulinc']['phone'] = new_contact_info['phone']
                    existing_contact_info['ulinc']['website'] = new_contact_info['website']
                    existing_contact_info['ulinc']['li_profile_url'] = new_contact_info['profile']
                    existing_contact.contact_info = existing_contact_info
                    connection_action = Action(str(uuid4()), existing_contact.contact_id, action_type_dict['li_new_connection']['id'], None, None)
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
                
                new_contact = create_new_contact(item, account.account_id, janium_campaign_id, existing_ulinc_campaign_id, contact_source_id)
                connection_action = Action(str(uuid4()), new_contact.contact_id, action_type_dict['li_new_connection']['id'], mtn_time, None)
                session.add(new_contact)
                session.add(connection_action)
        elif webhook_response.contact_source_type_id == 2:
            if existing_contact:
                contact_id = existing_contact.contact_id
                existing_contact_info = json.loads(existing_contact.contact_info)
                new_contact_info = {**base_contact_dict, **item}
                existing_contact_info['ulinc']['email'] = new_contact_info['email']
                existing_contact_info['ulinc']['phone'] = new_contact_info['phone']
                existing_contact_info['ulinc']['website'] = new_contact_info['website']
                existing_contact_info['ulinc']['li_profile_url'] = new_contact_info['profile']
                existing_contact.contact_info = existing_contact_info
            else:
                if existing_ulinc_campaign:
                    new_contact = create_new_contact(item, account.account_id, existing_ulinc_campaign.parent_janium_campaign.janium_campaign_id, existing_ulinc_campaign.ulinc_campaign_id, contact_source_id)
                else:
                    new_contact = create_new_contact(item, account.account_id, Janium_campaign.unassigned_janium_campaign_id, Ulinc_campaign.unassigned_ulinc_campaign_id, contact_source_id)
                session.add(new_contact)
                contact_id = new_contact.contact_id
            new_message_action = Action(
                str(uuid4()),
                contact_id,
                action_type_dict['li_new_message']['id'],
                mtn_time,
                item['message']
            )
            session.add(new_message_action)
        elif webhook_response.contact_source_type_id == 3:
            if existing_contact:
                contact_id = existing_contact.contact_id
                existing_contact_info = json.loads(existing_contact.contact_info)
                new_contact_info = {**base_contact_dict, **item}
                existing_contact_info['ulinc']['email'] = new_contact_info['email']
                existing_contact_info['ulinc']['phone'] = new_contact_info['phone']
                existing_contact_info['ulinc']['website'] = new_contact_info['website']
                existing_contact_info['ulinc']['li_profile_url'] = new_contact_info['profile']
                existing_contact.contact_info = existing_contact_info
            else:
                if existing_ulinc_campaign:
                    new_contact = create_new_contact(item, account.account_id, existing_ulinc_campaign.parent_janium_campaign.janium_campaign_id, existing_ulinc_campaign.ulinc_campaign_id, contact_source_id)
                else:
                    new_contact = create_new_contact(item, account.account_id, Janium_campaign.unassigned_janium_campaign_id, Ulinc_campaign.unassigned_ulinc_campaign_id, contact_source_id)
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
                    action_type_dict['ulinc_messenger_origin_message']['id'],
                    mtn_time,
                    item['message']
                )
            else:
                new_action = Action(
                    str(uuid4()),
                    contact_id,
                    action_type_dict['li_send_message']['id'],
                    mtn_time,
                    item['message']
                )
            session.add(new_action)
        else:
            logger.error('Unknown webhook response type')

        session.commit()

def main(event, context):
    session = get_session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    # client = session.query(Client).filter(Client.client_id == payload_json['client_id']).first()
    account = session.query(Account).filter(Account.account_id == payload_json['account_id']).first()

    if account:
        webhooks = [
            {"url": account.ulinc_config.new_connection_webhook, "type": 1},
            {"url": account.ulinc_config.new_message_webhook, "type": 2},
            {"url": account.ulinc_config.send_message_webhook, "type": 3}
        ]

        contact_source_id_list = []
        empty_webhook_responses = []
        for webhook in webhooks:
            webhook_request_response = poll_webhook(webhook['url'], webhook['type'])
            if len(webhook_request_response) > 0:
                contact_source = Contact_source(str(uuid4()), account.account_id, webhook['type'], webhook_request_response)
                # webhook_response = Webhook_response(str(uuid4()), account.account_id, webhook_request_response, webhook_response_type_dict[webhook['type']]['id'])
                session.add(contact_source)
                contact_source_id_list.append(contact_source.contact_source_id)
            else:
                empty_webhook_responses.append(webhook['type'])
        session.commit()
        logger.info('Empty Webhooks for account {}: {}'.format(account.account_id, empty_webhook_responses))

        if len(contact_source_id_list) > 0:
            for contact_source_id in contact_source_id_list:
                handle_webhook_response(account, contact_source_id, session)
        logger.info('Polled webhooks for {}'.format(account.account_id))


if __name__ == '__main__':
    payload = {
        "account_id": "8acafb6b-3ce5-45b5-af81-d357509ba457"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
