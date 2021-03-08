import base64
import io
import json
import logging
import os
from datetime import datetime, timedelta
from uuid import uuid4
import csv

import pandas as pd
import requests
from nameparser import HumanName
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # pylint: disable=no-member

if not os.getenv('LOCAL_DEV'):
    import demoji_module as demoji
    from model import *
    from model_types import *
    demoji.download_codes()

    logger = logging.getLogger('poll_ulinc_csv')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    import janium_functions.poll_ulinc_csv.poll_ulinc_csv_function.demoji_module as demoji
    from db.model import *
    from db.model_types import *

    logger = logging.getLogger('poll_ulinc_csv')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

mtn_time = datetime.utcnow() - timedelta(hours=7)

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

def create_new_contact(contact_info, client_id, campaign_id, existing_ulinc_campaign_id, wh_id):
    data = {**base_contact_dict, **contact_info}
    name = scrub_name(data['first_name'] + ' ' + data['last_name'])
    return Contact(
        str(uuid4()),
        client_id,
        campaign_id,
        existing_ulinc_campaign_id,
        wh_id,
        data['id'],
        data['campaign_id'],
        str(name.first).replace(" ", ""),
        str(name.last).replace(" ", ""),
        data['title'],
        data['company'],
        data['location'],
        data['email'],
        None,
        None,
        data['phone'],
        data['website'],
        data['profile'],
        None
    )

def get_csv(client_ulinc_id, ulinc_campaign_id, ulinc_cookie_json_value):
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    usr = ulinc_cookie_json_value['usr']
    pwd = ulinc_cookie_json_value['pwd']
    jar = requests.cookies.RequestsCookieJar()
    jar.set('usr', usr)
    jar.set('pwd', pwd)

    data = {"status": "1", "id": "{}".format(campaign_id)}

    res = requests.post(url='https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=export'.format(client_ulinc_id, ulinc_campaign_id), headers=header, data=data, cookies=jar)
    # print(res.text)
    if res.ok:
        return res.content.decode('utf-8')

# def handle_csv_data(client_ulinc_id, campaign_id, ulinc_cookie_json_value, session, client_id, janium_campaign_id):
def handle_csv_data(client, janium_campaign, ulinc_camapign, session):
    data = get_csv(client.ulinc_id, ulinc_campaign.ulinc_ulinc_campaign_id, client.ulinc_config.cookie.cookie_json_value)
    # df = pd.read_csv(io.StringIO(data))
    # print(df.iloc[0])

    reader = csv.reader(io.StringIO(data))
    d_list = list(reader)
    # print(d_list[1])

    # ulinc_id_list = [str(client_ulinc_id + item[12]) for item in d_list[1:] if item[10] == 'In Queue']
    # # print(ulinc_id_list[:10])
    # existing_contacts = session.query(Contact).filter(Contact.ulinc_id.in_(ulinc_id_list)).all()
    # # print(existing_contacts)
    # # for contact in existing_contacts:
    # #     for action in contact.actions:
    # #         print(action.action_type_id)

    for row in d_list[1:]:
        existing_contact = session.query(Contact).filter(Contact.ulinc_id == str(client_ulinc_id + row[12])).first()
        if row[10] == 'In Queue':
            if existing_contact:
                if existing_action := existing_contact.actions.filter(Action.action_type_id == 18).first():
                    continue
                else:
                    new_action = Action(str(uuid4()), existing_contact.contact_id, 18, mtn_time, None)
                    session.add(new_action)
            else:
                new_contact = create_new_contact(
                    row, client.client_id, janium_campaign.janium_campaign_id, ulinc_camapign.ulinc_campaign_id,Webhook_response.unassigned_webhook_response_id
                )
                session.add(new_contact)
                new_action = Action(str(uuid4()), new_contact.contact_id, 18, mtn_time, None)
                session.add(new_action)
        elif row[10] == 'Connect Req':
            if existing_contact:
                if existing_action := existing_contact.actions.filter(Action.action_type_id == 19).first():
                    continue
                else:
                    existing_contact.li_profile_url = row[1]
                    new_action = Action(str(uuid4()), existing_contact.contact_id, 19, mtn_time, None)
                    session.add(new_action)
            else:
                new_contact = create_new_contact(
                    row, client.client_id, janium_campaign.janium_campaign_id, ulinc_camapign.ulinc_campaign_id,Webhook_response.unassigned_webhook_response_id
                )
                session.add(new_contact)
                new_action = Action(str(uuid4()), new_contact.contact_id, 19, mtn_time, None)
                session.add(new_action)
        elif row[10] == 'Connected':
            if existing_contact:
                if last_new_message := existing_contact.actions.filter(Action.action_type_id.in_(2 )).order_by(Action.action_timestamp.desc()).first():
                    continue_campaign_action = Action(str(uuid4()), existing_contact.contact_id, 20, mtn_time, None)
                    session.add(continue_campaign_action)
                else:
                    pass
            else:
                pass




def main(event, context):
    session = get_session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    client = session.query(Client).filter(Client.client_id == payload_json['client_id']).first()
    janium_campaign = client.janium_campaigns[0]
    ulinc_campaign = janium_campaign.ulinc_campaigns[0]

    handle_csv_data(client, janium_campaign, ulinc_camapign, session)

    # for janium_campaign in client.janium_campaigns:
    #     for ulinc_campaign in janium_campaign.ulinc_campaigns:
    #         handle_csv_data(client, janium_campaign, ulinc_camapign, session)



if __name__ == '__main__':
    payload = {
        "client_id": "a77a723d-09ea-4282-8c96-9be09937dc69"
    }
    payload = json.dumps(payload)
    payload = base64.b64encode(str(payload).encode("utf-8"))
    event = {
        "data": payload
    }
    main(event, 1)
