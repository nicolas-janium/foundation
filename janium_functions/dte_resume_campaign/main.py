from datetime import datetime, timedelta
import os
import logging

import requests

if not os.getenv('LOCAL_DEV'):
    from model import *
    logger = logging.getLogger('dte_resume_campaign')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('dte_resume_campaign')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

PROJECT_ID = os.getenv('PROJECT_ID')
mtn_time = datetime.utcnow() - timedelta(hours=7)

def main(request):
    args = request.args
    client_id = args['client_id']
    contact_id = args['contact_id']
    contact_full_name = args['contact_full_name']
    action_id = args['action_id']

    session = Session()

    action = session.query(Action).filter(Action.action_id == action_id).first()
    action.action_type_id = 12
    session.commit()

    client = session.query(Client).filter(Client.client_id == client_id).first()
    if client.ulinc_config_id != Ulinc_config.unassigned_ulinc_config_id and client.ulinc_config.cookie_id != Cookie.unassigned_cookie_id:
        session2 = requests.Session()
        jar = requests.cookies.RequestsCookieJar()
        jar.set('usr', client.ulinc_config.cookie.cookie_json_value['usr'])
        jar.set('pwd', client.ulinc_config.cookie.cookie_json_value['pwd'])

        contact = session.query(Contact).filter(Contact.contact_id == contact_id).first()

        contact_ulinc_id = str(contact.ulinc_id)
        contact_ulinc_id = contact_ulinc_id.replace(str(client.ulinc_config.client_ulinc_id), '')
        url = 'https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=change_status&id={}&status=10'.format(client.ulinc_config.client_ulinc_id, contact.ulinc_ulinc_campaign_id, contact_ulinc_id)

        r = session2.get(url=url, cookies=jar)

        if r.ok:
            res = r.text
            if len(res) == 0:
                print("Invalid contact_ulincid")
            elif len(res) < 500:
                print("Contact {} marked to Replied in Ulinc".format(contact_full_name))

                url = "https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=continue_sending&id={}".format(client.ulinc_config.client_ulinc_id, contact.ulinc_ulinc_campaign_id, contact_ulinc_id)
                rr = session2.get(url=url, cookies=jar)
                if rr.ok:
                    print("Contact {} marked to Connected in Ulinc".format(contact_full_name))
            elif len(res) > 500:
                print("Invalid cookie")
        else:
            print(r.text)

    return r"""\
        <h1 style="text-align: center;">Janium Continue Campaign</h1>
        <h4 style="text-align: center;">Contact/Propsect: {contact}</h4>
        <hr />
        <p style="text-align: center;">This contact has had its campaign resumed, and they were marked to Connected in Ulinc. They will receive further messaging.</p>\
        """.replace(r"{contact}", contact_full_name)
