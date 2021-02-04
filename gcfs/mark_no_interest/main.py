import base64
import json
from datetime import datetime, timedelta
from uuid import uuid4
import numpy as np

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_model import Action, Client, Contact, Ulinc_cookie, Session, engine


def main(event, context):
    session = Session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    active_clients = session.query(Client).filter(Client.is_active == 1).filter(Client.is_dte == 1).all()
    client_list = []
    for client in active_clients:
        client_ulinc_id = client.ulinc_id

        ulinc_cookie = client.ulinc_cookie

        if ulinc_cookie:
            if ulinc_cookie.dateadded > datetime.now():
                print("Cookie expired for client {}".format(client.firstname + ' ' + client.lastname))
                break

            session2 = requests.Session()
            jar = requests.cookies.RequestsCookieJar()
            jar.set('usr', ulinc_cookie.usr)
            jar.set('pwd', ulinc_cookie.pwd)

            contacts = client.contacts
            contact_list = []
            data = []
            for contact in contacts:
                actions = contact.actions
                for action in actions:
                    data.append([client.id, client.ulinc_id, contact.id, contact.ulinc_id, contact.ulinc_campaign_id, action.action_code, action.dateadded])

            a = np.array(data)
            a = a[a[:,6].argsort()[::-1]]

            prev_action_codes = a[:,5]
            last_action = a[0]

            if (
                1 in prev_action_codes and
                not any(item in prev_action_codes for item in [2,4,7,9]) and
                last_action[5] == 8 and
                abs(datetime.now() - last_action[6]) > timedelta(hours=24)
            ):
                ulinc_contact_id = str(last_action[3]).replace(str(last_action[1]), '')
                url = 'https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=change_status&id={}&status=21'.format(last_action[1], last_action[4], ulinc_contact_id)

                r = session2.get(url=url, cookies=jar)

                if r.ok:
                    res = r.text
                    if len(res) == 0:
                        print("Invalid contact_ulinc_id")
                    elif len(res) < 500:
                        action = Action(str(uuid4()), last_action[2], datetime.now(), 9, None, False, None)
                        session.add(action)
                        session.commit()
                        contact_list.append(contact.fullname)
                    elif len(res) > 500:
                        print("Invalid cookie")
                else:
                    print(r.text)
            print("Contacts marked to no interest for client {}: {}".format(client.firstname + ' ' + client.lastname, contact_list))
        else:
            print("no cookie for client {}".format(client.firstname + ' ' + client.lastname))

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