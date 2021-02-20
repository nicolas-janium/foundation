import base64
import json
from datetime import datetime
from uuid import uuid4
import logging
import os

import requests
from bs4 import BeautifulSoup as Soup

if not os.getenv('LOCAL_DEV'):
    from model import *
    logger = logging.getLogger('refresh_ulinc_cookie')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('refresh_ulinc_cookie')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)

def get_cookie(ulinc_clientid, username, password):
    login_url = 'https://ulinc.co/login/?email={}&password={}&sign=1'.format(username, password)

    req_session = requests.Session()
    login = req_session.post(url=login_url)

    ulinc_cookie = {}
    for cookie in login.history[0].cookies:
        if cookie.name == 'PHPSESSID':
            continue
        elif cookie.name == 'usr':
            ulinc_cookie['usr'] = cookie.value
            ulinc_cookie['expires'] = datetime.fromtimestamp(cookie.expires).strftime(r'%Y-%m-%d %H:%M:%S')
        elif cookie.name == 'pwd':
            ulinc_cookie['pwd'] = cookie.value
    return ulinc_cookie

def refresh_ulinc_cookie(client, session):
    ulinc_cookie = get_cookie(client.ulinc_config.client_ulinc_id, client.ulinc_config.credentials.username, client.ulinc_config.credentials.password)
    if client.ulinc_config.cookie_id == Cookie.unassigned_cookie_id:
        new_cookie = Cookie(str(uuid4()), 1, ulinc_cookie)
        session.add(new_cookie)
    else:
        client.ulinc_config.cookie.cookie_json_value = ulinc_cookie
    session.commit()
    return 1

def extract_campaign_id(url):
    return url.split('/')[-2]

def get_ulinc_campaigns(client, ulinc_cookie):
    req_session = requests.Session()
    get_connector_campaigns_url = 'https://ulinc.co/{}/?do=campaigns&act=campaigns'.format(client.ulinc_config.client_ulinc_id)
    get_messenger_campaigns_url = 'https://ulinc.co/{}/?do=campaigns&act=bulk_campaigns'.format(client.ulinc_config.client_ulinc_id)

    usr = ulinc_cookie.cookie_json_value['usr']
    pwd = ulinc_cookie.cookie_json_value['pwd']
    jar = requests.cookies.RequestsCookieJar()
    jar.set('usr', usr)
    jar.set('pwd', pwd)

    campaigns = {
        "connector": [],
        "messenger": []
    }

    connector_campaigns_table = req_session.get(url=get_connector_campaigns_url, cookies=jar)
    c_soup = Soup(connector_campaigns_table.text, 'html.parser')
    c_table_body = c_soup.find('tbody')
    if len(c_table_body.find_all('tr')) > 0:
        for tr in c_table_body.find_all('tr'):
            td_list = tr.find_all('td')
            camp_dict = {
                "name": td_list[0].text,
                "ulinc_campaign_id": str(extract_campaign_id(td_list[0].find('a')['href'])),
                "is_active": True if td_list[1].find('span').text == 'Active' else False
            }
            campaigns['connector'].append(camp_dict)

    messenger_campaigns_table = req_session.get(url=get_messenger_campaigns_url, cookies=jar)
    m_soup = Soup(messenger_campaigns_table.text, 'html.parser')
    m_table_body = m_soup.find('tbody')
    if len(m_table_body.find_all('tr')) > 0:
        for tr in m_table_body.find_all('tr'):
            td_list = tr.find_all('td')
            ulinc_campaign_id = str(extract_campaign_id(td_list[0].find('a')['href']))
            camp_dict = {
                "name": td_list[0].text,
                "ulinc_campaign_id": ulinc_campaign_id,
                "is_active": True if td_list[1].find('span').text == 'Active' else False
            }
            campaigns['messenger'].append(camp_dict)

    return campaigns

def insert_campaigns(ulinc_campaign_dict, client_id, session):
    for ulinc_campaign in ulinc_campaign_dict['connector']:
        existing_ulinc_campaign = session.query(Ulinc_campaign).filter(Ulinc_campaign.client_id == client_id).filter(Ulinc_campaign.ulinc_ulinc_campaign_id == ulinc_campaign['ulinc_campaign_id']).first()
        if existing_ulinc_campaign:
            existing_ulinc_campaign.ulinc_campaign_name = ulinc_campaign['name']
            existing_ulinc_campaign.ulinc_is_active = ulinc_campaign['is_active']
        else:
            new_Ulinc_campaign = Ulinc_campaign(
                str(uuid4()),
                client_id,
                '9d6c1500-233f-42e2-9e02-725a22c831dc',
                ulinc_campaign['name'],
                ulinc_campaign['is_active'],
                ulinc_campaign['ulinc_campaign_id'],
                False,
                None
            )
            session.add(new_Ulinc_campaign)

    for ulinc_campaign in ulinc_campaign_dict['messenger']:
        existing_ulinc_campaign = session.query(Ulinc_campaign).filter(Ulinc_campaign.client_id == client_id).filter(Ulinc_campaign.ulinc_ulinc_campaign_id == ulinc_campaign['ulinc_campaign_id']).first()
        if existing_ulinc_campaign:
            existing_ulinc_campaign.ulinc_campaign_name = ulinc_campaign['name']
            existing_ulinc_campaign.ulinc_is_active = ulinc_campaign['is_active']
        else:
            new_Ulinc_campaign = Ulinc_campaign(
                str(uuid4()),
                client_id,
                '9d6c1500-233f-42e2-9e02-725a22c831dc',
                ulinc_campaign['name'],
                ulinc_campaign['is_active'],
                ulinc_campaign['ulinc_campaign_id'],
                True,
                None
            )
            session.add(new_Ulinc_campaign)

    session.commit()

def refresh_ulinc_campaigns(client, session):
    if client.ulinc_config.cookie_id != Cookie.unassigned_cookie_id:
        ulinc_campaign_dict = get_ulinc_campaigns(client, client.ulinc_config.cookie)
        if ulinc_campaign_dict:
            insert_campaigns(ulinc_campaign_dict, client.client_id, session)
        else:
            logger.info('Campaign dict empty. Error or no campaigns')
    else:
        logger.info('Client ulinc cookie does not exist for {}'.format(client.full_name))

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    client = session.query(Client).filter(Client.client_id == payload_json['client_id']).first()

    refresh_ulinc_cookie(client, session)

    refresh_ulinc_campaigns(client, session)

    return 1


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
