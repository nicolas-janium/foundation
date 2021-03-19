import base64
import json
import logging
import os
from datetime import datetime
from pprint import pprint
import pytz

import requests
import urllib3
from bs4 import BeautifulSoup as Soup
from sqlalchemy import or_, and_
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

mtn_tz = pytz.timezone('US/Mountain')
mtn_time = datetime.now(pytz.timezone('UTC')).astimezone(mtn_tz)

def send_li_message(details):
    req_session = requests.Session()
    url = 'https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=send_message'.format(details['ulinc_client_id'], int(details['ulinc_campaign_id']))

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

            status_url = "https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=continue_sending&id={}".format(details['ulinc_client_id'], int(details['ulinc_campaign_id']), details['contact_ulinc_id'])
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

def get_li_message_targets(account, janium_campaign, account_local_time):
    steps = janium_campaign.janium_campaign_steps.order_by(Janium_campaign_step.janium_campaign_step_delay).all()
    contacts = [
        contact 
        for contact 
        in janium_campaign.contacts.all()
        if not contact.actions.filter(Action.action_type_id.in_([7,11])).first()
    ]
    li_message_targets_list = []
    for contact in contacts:
        messages_count = len(contact.actions.filter(or_(Action.action_type_id == 2, Action.action_type_id == 6)).all())
        continue_campaign_count = len(contact.actions.filter(or_(Action.action_type_id == 14)).all())
        if (messages_count <= continue_campaign_count) or (continue_campaign_count == 0 and messages_count == 0):
            if cnxn_action := contact.actions.filter(or_(Action.action_type_id == 1, Action.action_type_id == 14)).order_by(Action.action_type_id.desc()).first():
                cnxn_timestamp = cnxn_action.action_timestamp
                for i, step in enumerate(steps):
                    if step.janium_campaign_step_type_id == 1:
                        add_contact = False
                        if i + 1 < len(steps):
                            if step.janium_campaign_step_delay <= networkdays(cnxn_timestamp, account_local_time) < steps[i + 1].janium_campaign_step_delay:
                                add_contact = True
                        else:
                            if step.janium_campaign_step_delay <= networkdays(cnxn_timestamp, account_local_time) < step.janium_campaign_step_delay + 2:
                                add_contact = True
                        if add_contact:
                            li_message_targets_list.append(
                                {
                                    # "client_full_name": client.full_name,
                                    "ulinc_client_id": account.ulinc_config.ulinc_client_id,
                                    "contact_id": contact.contact_id,
                                    "contact_first_name": contact.contact_info['ulinc']['first_name'],
                                    "contact_ulinc_id": str(contact.ulinc_id).replace(str(account.ulinc_config.ulinc_client_id), ''),
                                    "message_text": step.janium_campaign_step_body,
                                    "ulinc_campaign_id": contact.ulinc_ulinc_campaign_id,
                                    "cookie_usr": account.ulinc_config.cookie.cookie_json_value['usr'],
                                    "cookie_pwd": account.ulinc_config.cookie.cookie_json_value['pwd']
                                }
                            )
    return li_message_targets_list

def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    session = get_session()
    account = session.query(Account).filter(Account.account_id == payload_json['account_id']).first()

    account_local_time = datetime.now(pytz.timezone('UTC')).astimezone(pytz.timezone(account.time_zone.time_zone_code)).replace(tzinfo=None)


    for janium_campaign in account.janium_campaigns.filter(and_(Janium_campaign.effective_start_date < account_local_time, Janium_campaign.effective_end_date > account_local_time)).all():
        li_message_targets_list = get_li_message_targets(account, janium_campaign, account_local_time)
        # pprint(li_message_targets_list)

        recipient_list = []
        for li_message_target in li_message_targets_list:
            logger.debug(li_message_target)
            recipient_list.append(send_li_message(li_message_target))
        logger.info('Sent LI messages to {} for account {} in campaign {}'.format(recipient_list, account.account_id, janium_campaign.janium_campaign_name))


if __name__ == '__main__':
    payload = {
        "account_id": "6bc4e64d-b32f-40a9-92ad-52a32f62e455"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
