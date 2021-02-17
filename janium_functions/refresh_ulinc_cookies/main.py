import base64
import json
from datetime import datetime
from uuid import uuid4
import logging

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_model import *

if not os.getenv('LOCAL_DEV'):
    logger = logging.getLogger('refresh_ulinc_cookie')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    logger = logging.getLogger('refresh_ulinc_cookie')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

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

def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    if payload_json['testing'] == 'true':
        clients = session.query(Client).filter(Client.client_id == '8a52cdff-6722-4d26-9a6a-55fe952bbef1').all()
    else:
        clients = session.query(Client).filter(Client.is_active == 1).filter(Client.ulinc_config != None).all()

    for client in clients:
        logger.debug(client.ulinc_config.credentials.username + ' ' + client.ulinc_config.credentials.password)
        ulinc_cookie = get_cookie(client.ulinc_config.client_ulinc_id, client.ulinc_config.credentials.username, client.ulinc_config.credentials.password)
        logger.debug(ulinc_cookie)
        if client.ulinc_config.cookie_id == Cookie.dummy_cookie_id:
            new_cookie = Cookie(str(uuid4()), 1, ulinc_cookie)
            session.add(new_cookie)
        else:
            client.ulinc_config.cookie.cookie_json_value = ulinc_cookie
        session.commit()


if __name__ == '__main__':
    payload = {
        "testing": "true"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
