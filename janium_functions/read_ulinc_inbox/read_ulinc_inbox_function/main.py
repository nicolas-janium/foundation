import base64
import email
import json
import logging
import os
import re
import ssl
from datetime import datetime, timedelta
from pprint import pprint
from uuid import uuid4

import pytz
import requests
from bs4 import BeautifulSoup as Soup
from html2text import html2text

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('read_ulinc_inbox_function')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('read_ulinc_inbox_function')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

def get_ulinc_inbox(account, ulinc_campaign, contact):
    req_session = requests.Session()
    ulinc_client_id = account.ulinc_config.ulinc_client_id
    url = "https://ulinc.co/{}/campaigns/{}/?act=contact_info&id={}".format(ulinc_client_id, ulinc_campaign.ulinc_ulinc_campaign_id, contact.get_short_ulinc_id(ulinc_client_id))

    ulinc_cookie = account.ulinc_config.cookie.cookie_json_value
    jar = requests.cookies.RequestsCookieJar()
    jar.set('usr', ulinc_cookie['usr'])
    jar.set('pwd', ulinc_cookie['pwd'])

    res = req_session.get(url=url, cookies=jar)
    if res.ok:
        res2 = req_session.get(url="https://ulinc.co/{}/campaigns/{}/?act=mark_conv&ids={}&id=1".format(ulinc_client_id, ulinc_campaign.ulinc_ulinc_campaign_id, contact.get_short_ulinc_id(ulinc_client_id)), cookies=jar)
        if res2.ok:
            print("Set contact back to unread")
            return res.text

def handle_ulinc_inbox(account, janium_campaign, ulinc_campaign, contact, session):
    inbox_html = get_ulinc_inbox(account, ulinc_campaign, contact)
    inbox_soup = Soup(inbox_html, 'html.parser')
    for message in inbox_soup.find_all('div', **{"class": "direct-chat-msg"}):
        message_content = message.find('div', **{"class": "direct-chat-text"})
        message_content_html = str(message_content.prettify()).replace("\n", "")

        message_info = message.find('div', **{"class": "direct-chat-info"})
        message_sender = message_info.find('span', **{"class": "direct-chat-name"}).get_text().rstrip()
        message_timestamp_string = message_info.find('span', **{"class": "direct-chat-timestamp"}).get_text().rstrip()
        message_timestamp = datetime.strptime(message_timestamp_string, "%m/%d/%Y @ %H:%M").astimezone(pytz.timezone(account.time_zone.time_zone_code)).astimezone(pytz.utc).replace(tzinfo=None)

        if existing_action := contact.actions.filter(Action.action_message == message_content_html).filter(Action.action_timestamp == message_timestamp).first():
            pass
        else:
            new_action = Action(str(uuid4()), contact.contact_id, 3 if message_sender == 'You' else 2, message_timestamp, message_content_html, None)
            session.add(new_action)
            session.commit()


def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)
    
    session = get_session()

    if account := session.query(Account).filter(Account.account_id == payload_json['account_id']).first():
        account_local_time = datetime.now(pytz.timezone('UTC')).astimezone(pytz.timezone(account.time_zone.time_zone_code)).replace(tzinfo=None)
        for janium_campaign in account.janium_campaigns:
            effective_dates_dict = janium_campaign.get_effective_dates(account.time_zone.time_zone_code)
            if (effective_dates_dict['start'] <= account_local_time <= effective_dates_dict['end']):
                for ulinc_campaign in janium_campaign.ulinc_campaigns.filter(Ulinc_campaign.ulinc_is_active == 1).all():
                    for contact in ulinc_campaign.contacts:
                        handle_ulinc_inbox(account, janium_campaign, ulinc_campaign, contact, session)

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
