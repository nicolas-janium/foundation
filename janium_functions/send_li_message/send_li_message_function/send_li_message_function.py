import base64
import json
import logging
import os
from datetime import datetime
from pprint import pprint

import requests
import urllib3
from bs4 import BeautifulSoup as Soup
from sqlalchemy import or_
from workdays import networkdays

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('send_li_message_function')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('send_li_message_function')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)


def send_li_message(details):
    req_session = requests.Session()
    url = 'https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=send_message'.format(details['client_ulinc_id'], int(details['ulinc_campaign_id']))

    jar = requests.cookies.RequestsCookieJar()
    jar.set('usr', details['cookie_usr'])
    jar.set('pwd', details['cookie_pwd'])

    headers = {
        "Accept": "application/json"
    }

    message = str(details['message_text'])
    if message.__contains__('<p>'):
        soup = Soup(message, 'html.parser')
        bs = ''
        for p in soup.find_all('p'):
            bs += str(str(p.text).rstrip() + '\n')
        message = bs.rstrip()
    elif message.__contains__('<div>'):
        message = html2text(message)
        message = message.rstrip()
    else:
        pass

    payload = {
        "message[contact_id]": details['contact_ulinc_id'],
        "message[text]": message
    }

    res = req_session.post(url=url, cookies=jar, headers=headers, data=payload, verify=False)
    if res.ok:
        res_json = res.json()
        if res_json['status'] == 'ok':
            # print("Sent li message to contact {} for client {}".format(details['contactid'], details['client_fullname']))

            status_url = "https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=continue_sending&id={}".format(details['client_ulinc_id'], int(details['ulinc_campaign_id']), details['contact_ulinc_id'])
            status_res = req_session.get(url=status_url, cookies=jar, headers=headers, verify=False)
            if status_res.ok:
                # print("Updated Ulinc status to connected for contact {} for client {}".format(details['contactid'], details['client_fullname']))
                return details['contact_first_name']
            else:
                print("Failed to update status to connected for contact {} at request level. Response: {}".format(details['contact_id'], res.text))
                return details['contact_first_name']
        else:
            print("Li message to contact {} failed. Response: {}".format(details['contact_id'], res.text))
            return None
    else:
        print("Li message to contact {} failed at request level. Response: {}".format(details['contact_id'], res.text))
        return None

def get_li_message_targets(client, janium_campaign):
    steps = janium_campaign.janium_campaign_steps.order_by(Janium_campaign_step.janium_campaign_step_delay).all()
    contacts = [
        contact 
        for contact 
        in janium_campaign.contacts.order_by(Contact.full_name).all()
        if not contact.actions.filter(Action.action_type_id.in_([2,6,7,11])).first()
    ]
    li_message_targets_list = []
    for contact in contacts:
        cnxn_date = contact.actions.filter(or_(Action.action_type_id == 1, Action.action_type_id == 14)).order_by(Action.action_type_id.desc()).first().action_timestamp
        for i, step in enumerate(steps):
            if step.janium_campaign_step_type_id == 1:
                add_contact = False
                if i + 1 < len(steps):
                    if step.janium_campaign_step_delay <= networkdays(cnxn_date, mtn_time) < steps[i + 1].janium_campaign_step_delay:
                        add_contact = True
                else:
                    if step.janium_campaign_step_delay <= networkdays(cnxn_date, mtn_time) < step.janium_campaign_step_delay + 2:
                        add_contact = True
                if add_contact:
                    li_message_targets_list.append(
                        {
                            "client_full_name": client.full_name,
                            "client_ulinc_id": client.ulinc_config.client_ulinc_id,
                            "contact_id": contact.contact_id,
                            "contact_first_name": contact.first_name,
                            "contact_ulinc_id": str(contact.ulinc_id).replace(str(client.ulinc_config.client_ulinc_id), ''),
                            "message_text": step.janium_campaign_step_body,
                            "ulinc_campaign_id": contact.ulinc_ulinc_campaign_id,
                            "cookie_usr": client.ulinc_config.cookie.cookie_json_value['usr'],
                            "cookie_pwd": client.ulinc_config.cookie.cookie_json_value['pwd']
                        }
                    )
    return li_message_targets_list

def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)
    
    session = Session()
    client = session.query(Client).filter(Client.client_id == payload_json['client_id']).first()

    for janium_campaign in client.janium_campaigns.filter(Janium_campaign.is_active == 1).all():
        li_message_targets_list = get_li_message_targets(client, janium_campaign)
        pprint(li_message_targets_list)

        recipient_list = []
        for li_message_target in li_message_targets_list:
            logger.debug(li_message_target)
            recipient_list.append(send_li_message(li_message_target))
        logger.info('Sent LI messages to {} for client {} in campaign {}'.format(recipient_list, client.full_name, janium_campaign.janium_campaign_name))


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