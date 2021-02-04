import base64
import json
from datetime import datetime
from uuid import uuid4

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_model import Client, Session, Ulinc_cookie


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

    clients = session.query(Client).filter(Client.is_active == 1).filter(Client.ulinc_username != None).filter(Client.ulinc_password != None).all()

    for client in clients:
        ulinc_cookie = get_cookie(client.ulinc_id, client.ulinc_username, client.ulinc_password)
        if client.ulinc_cookie:
            client.ulinc_cookie.usr = ulinc_cookie['usr']
            client.ulinc_cookie.pwd = ulinc_cookie['pwd']
            client.ulinc_cookie.expires = ulinc_cookie['expires']
        else:
            new_ulinc_cookie = Ulinc_cookie(str(uuid4()), client.id, ulinc_cookie['usr'], ulinc_cookie['pwd'], ulinc_cookie['expires'])
            session.add(new_ulinc_cookie)
        session.commit()


if __name__ == '__main__':
    payload = {
        "from": "retool",
        "lpass_ulinc": "3930558453453060520"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
