import base64
import csv
import io
import json
import logging
import os
from datetime import datetime, timedelta
from pprint import pprint
from uuid import uuid4

import pandas as pd
import pytz
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

base_contact_dict = dict({
    'Campaign ID': 0,
    'Contact ID': None,
    'Name': None,
    'Title': None,
    'Company': None,
    'Location': None,
    'Email': None,
    'Phone': None,
    'Website': None,
    'LinkedIn profile': None
})

def scrub_name(name):
    return HumanName(demoji.replace(name.replace(',', ''), ''))

def create_new_contact(contact_info, account_id, campaign_id, existing_ulinc_campaign_id, contact_source_id, ulinc_client_id):
    conv = lambda i : i or None
    data = {**base_contact_dict, **contact_info}
    name = scrub_name(data['Name'])
    return Contact(
        str(uuid4()),
        contact_source_id,
        account_id,
        campaign_id,
        existing_ulinc_campaign_id,
        str(ulinc_client_id + data['Contact ID']),
        data['Campaign ID'],
        {
            'ulinc': {
                'first_name': name.first,
                'last_name': name.last,
                'title': conv(data['Title']),
                'company': conv(data['Company']),
                'location': conv(data['Location']),
                'email': conv(data['Email']),
                'phone': conv(data['Phone']),
                'website': conv(data['Website']),
                'li_salesnav_profile_url': data['LinkedIn profile'] if 'sales' in data['LinkedIn profile'] else None,
                'li_profile_url': data['LinkedIn profile'] if 'sales' not in data['LinkedIn profile'] else None
            }
        },
        None,
        User.system_user_id
    )


def poll_and_save_csv(ulinc_client_id, ulinc_campaign_id, ulinc_cookie_json_value, account_id, session):
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

    data = {"status": "1", "id": "{}".format(ulinc_campaign_id)}

    res = requests.post(url='https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=export'.format(ulinc_client_id, ulinc_campaign_id), headers=header, data=data, cookies=jar)
    # print(res.text)
    if res.ok:
        reader = csv.DictReader(io.StringIO(res.content.decode('utf-8')))
        contact_source_id = str(uuid4())
        contact_source = Contact_source(contact_source_id, account_id, 4, list(reader))
        session.add(contact_source)
        session.commit()
        return contact_source_id

def handle_csv_data(account, janium_campaign, ulinc_campaign, session):
    contact_source_id = poll_and_save_csv(account.ulinc_config.ulinc_client_id, ulinc_campaign.ulinc_ulinc_campaign_id, account.ulinc_config.cookie.cookie_json_value,  account.account_id, session)
    # contact_source_id = poll_and_save_csv('5676186', '13', {'usr': '48527', 'pwd': '93fd3060131f8f9e8410775809f0a231'}, account.account_id, session)
    d_list = session.query(Contact_source).filter(Contact_source.contact_source_id == contact_source_id).first().contact_source_json
    # df = pd.read_csv(io.StringIO(data))
    # print(df.iloc[0])

    # ulinc_id_list = [str(client_ulinc_id + item[12]) for item in d_list[1:] if item[10] == 'In Queue']
    # # print(ulinc_id_list[:10])
    # existing_contacts = session.query(Contact).filter(Contact.ulinc_id.in_(ulinc_id_list)).all()
    # # print(existing_contacts)
    # # for contact in existing_contacts:
    # #     for action in contact.actions:
    # #         print(action.action_type_id)
    if d_list:
        print('Length of csv export: {}'.format(len(d_list)))
        for item in d_list:
            # existing_contact = session.query(Contact).filter(Contact.ulinc_id == str(account.ulinc_config.ulinc_client_id + item['Contact ID'])).first()
            existing_contact = session.query(Contact).filter(Contact.ulinc_id == str('5676186' + item['Contact ID'])).first()
            if item['Status'] == 'In Queue':
                if existing_contact:
                    if existing_action := existing_contact.actions.filter(Action.action_type_id == 18).first():
                        continue
                    else:
                        new_action = Action(str(uuid4()), existing_contact.contact_id, 18, datetime.utcnow(), None)
                        session.add(new_action)
                else:
                    new_contact = create_new_contact(
                        item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, account.ulinc_config.ulinc_client_id
                    )
                    # new_contact = create_new_contact(
                    #     item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, '5676186'
                    # )
                    session.add(new_contact)
                    new_action = Action(str(uuid4()), new_contact.contact_id, 18, datetime.utcnow(), None)
                    session.add(new_action)
            elif item['Status'] == 'Connect Req':
                if existing_contact:
                    if existing_action := existing_contact.actions.filter(Action.action_type_id == 19).first():
                        continue
                    else:
                        existing_contact_info = json.loads(existing_contact.contact_info)
                        existing_contact_info['li_profile_url'] = item['LinkedIn profile']
                        existing_contact.contact_info = existing_contact_info
                        new_action = Action(str(uuid4()), existing_contact.contact_id, 19, datetime.utcnow(), None)
                        session.add(new_action)
                else:
                    new_contact = create_new_contact(
                        item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, account.ulinc_config.ulinc_client_id
                    )
                    # new_contact = create_new_contact(
                    #     item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, '5676186'
                    # )
                    session.add(new_contact)
                    new_action = Action(str(uuid4()), new_contact.contact_id, 19, datetime.utcnow(), None)
                    session.add(new_action)
            elif item['Status'] == 'Connect Error':
                if existing_contact:
                    if existing_action := existing_contact.actions.filter(Action.action_type_id == 20).first():
                        continue
                    else:
                        new_action = Action(str(uuid4()), existing_contact.contact_id, 20, datetime.utcnow(), None)
                        session.add(new_action)
                else:
                    new_contact = create_new_contact(
                        item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, account.ulinc_config.ulinc_client_id
                    )
                    session.add(new_contact)
                    new_action = Action(str(uuid4()), new_contact.contact_id, 20, datetime.utcnow(), None)
                    session.add(new_action)
            elif item['Status'] == 'Later':
                if existing_contact:
                    if existing_action := existing_contact.actions.filter(Action.action_type_id == 21).first():
                        continue
                    else:
                        new_action = Action(str(uuid4()), existing_contact.contact_id, 21, datetime.utcnow(), None)
                        session.add(new_action)
                else:
                    new_contact = create_new_contact(
                        item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, account.ulinc_config.ulinc_client_id
                    )
                    session.add(new_contact)
                    new_action = Action(str(uuid4()), new_contact.contact_id, 21, datetime.utcnow(), None)
                    session.add(new_action)
            elif item['Status'] == 'No Interest':
                if existing_contact:
                    if existing_action := existing_contact.actions.filter(Action.action_type_id == 11).first():
                        continue
                    else:
                        new_action = Action(str(uuid4()), existing_contact.contact_id, 11, datetime.utcnow(), None)
                        session.add(new_action)
                else:
                    new_contact = create_new_contact(
                        item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, account.ulinc_config.ulinc_client_id
                    )
                    session.add(new_contact)
                    new_action = Action(str(uuid4()), new_contact.contact_id, 11, datetime.utcnow(), None)
                    session.add(new_action)
            elif item['Status'] == 'Connected':
                if existing_contact:
                    if existing_cnxn_action := existing_contact.actions.filter(Action.action_type_id.in_([1])).first():
                        if stop_campaign_actions := existing_contact.actions.filter(Action.action_type_id.in_([2, 6, 11, 21])).order_by(Action.action_timestamp.desc()).all():
                            if continue_campaign_action := existing_contact.actions.filter(Action.action_type_id == 14).order_by(Action.action_timestamp.desc()).first():
                                if stop_campaign_actions[0].action_timestamp > continue_campaign_action.action_timestamp:
                                    new_action = Action(str(uuid4()), existing_contact.contact_id, 14, datetime.utcnow(), None)
                                    session.add(new_action)
                                else:
                                    continue
                            else:
                                new_action = Action(str(uuid4()), existing_contact.contact_id, 14, datetime.utcnow(), None)
                                session.add(new_action)
                        else:
                            continue
                    else:
                        new_action = Action(str(uuid4()), existing_contact.contact_id, 1, datetime.utcnow(), None)
                        session.add(new_action)
                else:
                    new_contact = create_new_contact(
                        item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, account.ulinc_config.ulinc_client_id
                    )
                    session.add(new_contact)
                    new_action = Action(str(uuid4()), new_contact.contact_id, 1, datetime.utcnow(), None)
                    session.add(new_action)
            elif item['Status'] == 'Replied':
                if existing_contact:
                    pass
                else:
                    new_contact = create_new_contact(
                        item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, account.ulinc_config.ulinc_client_id
                    )
                    session.add(new_contact)
                    new_action = Action(str(uuid4()), new_contact.contact_id, 1, datetime.utcnow(), None)
                    session.add(new_action)
            elif item['Status'] == 'Talking':
                if existing_contact:
                    pass
                else:
                    new_contact = create_new_contact(
                        item, account.account_id, janium_campaign.janium_campaign_id, ulinc_campaign.ulinc_campaign_id, contact_source_id, account.ulinc_config.ulinc_client_id
                    )
                    session.add(new_contact)
                    new_action = Action(str(uuid4()), new_contact.contact_id, 1, datetime.utcnow(), None)
                    session.add(new_action)
        session.commit()




def main(event, context):
    session = get_session()

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    account = session.query(Account).filter(Account.account_id == payload_json['account_id']).first()
    account_local_time = datetime.now(pytz.timezone('UTC')).astimezone(pytz.timezone(account.time_zone.time_zone_code)).replace(tzinfo=None)

    # janium_campaign = account.janium_campaigns[0]
    # ulinc_campaign = janium_campaign.ulinc_campaigns[0]
    # handle_csv_data(account, janium_campaign, ulinc_campaign, session)

    for janium_campaign in account.janium_campaigns:
        effective_dates_dict = janium_campaign.get_effective_dates(account.time_zone.time_zone_code)
        for ulinc_campaign in janium_campaign.ulinc_campaigns:
            if (effective_dates_dict['start'] <= account_local_time <= effective_dates_dict['end']) and ulinc_campaign.ulinc_is_active == 1:
                handle_csv_data(account, janium_campaign, ulinc_campaign, session)



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
    # contact_source_id = poll_and_save_csv('5676186', '13', {'usr': '48527', 'pwd': '93fd3060131f8f9e8410775809f0a231'}, '8acafb6b-3ce5-45b5-af81-d357509ba457', get_session())
    # print(contact_source_id)
