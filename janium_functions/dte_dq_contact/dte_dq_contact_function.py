from datetime import datetime, timedelta
from uuid import uuid4
import os

import requests

from model import *

if not os.getenv('LOCAL_DEV'):
    from model import *
    logger = logging.getLogger('dte_dq_contact')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('dte_dq_contact')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)
PROJECT_ID = os.getenv('PROJECT_ID')


def main(request):
    args = request.args
    client_id = args['client_id']
    contact_id = args['contact_id']

    session = Session()

    if contact := session.query(Contact).filter(Contact.contact_id == contact_id).first():
        client = session.query(Client).filter(Client.client_id == client_id).first()

        new_action = Action(str(uuid4()), contact_id, 11, datetime.now() - timedelta(hours=7), None)
        session.add(new_action)  # pylint: disable=no-member
        session.commit()  # pylint: disable=no-member

        if client.ulinc_config.cookie_id != Cookie.dummy_cookie_id:
            session2 = requests.Session()
            jar = requests.cookies.RequestsCookieJar()
            jar.set('usr', client.ulinc_config.cookie.cookie_json_value['usr'])
            jar.set('pwd', client.ulinc_config.cookie.cookie_json_value['pwd'])

            ulinc_contact_id = str(contact.ulinc_id)
            ulinc_contact_id = ulinc_contact_id.replace(str(client.ulinc_config.client_ulinc_id), '')
            url = 'https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=change_status&id={}&status=21'.format(client.ulinc_config.client_ulinc_id, contact.ulinc_ulinc_campaign_id, ulinc_contact_id)

            r = session2.get(url=url, cookies=jar)

            if r.ok:
                res = r.text
                if len(res) == 0:
                    logger.info("Invalid contact_ulincid")
                elif len(res) < 500:
                    logger.info("Contact {} marked to no interest in Ulinc".format(contact.full_name))
                    return r"""\
                    <h1 style="text-align: center;">Janium: Disqualify Contact</h1>
                    <h4 style="text-align: center;">Contact/Propsect: {contact}</h4>
                    <hr />
                    <p style="text-align: center;">This contact has been disqualified. They will not receive any other messaging, and they were marked to "No Interest" in Ulinc.</p>\
                    """.replace(r"{contact}", contact.full_name)
                elif len(res) > 500:
                    logger.info("Invalid Cookie")
            else:
                logger.error(r.text)
            
            return r"""\
            <h1 style="text-align: center;">Janium: Disqualify Contact</h1>
            <h4 style="text-align: center;">Contact/Propsect: {contact}</h4>
            <hr />
            <p style="text-align: center;">This contact has been disqualified. They will not receive any other messaging.</p>\
            """.replace(r"{contact}", contact.full_name)
        else:
            logger.warning(f"No Ulinc Cookie for {client.full_name}")
    else:
        return 'Contact {} does not exist in the Janium database'.format(contact.full_name)
