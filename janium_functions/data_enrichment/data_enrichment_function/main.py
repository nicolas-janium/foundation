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
from workdays import networkdays

if not os.getenv('LOCAL_DEV'):
    from model import *

    logger = logging.getLogger('send_email_function')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
else:
    from db.model import *

    logger = logging.getLogger('send_email_function')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    logHandler = logging.StreamHandler()
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

PROJECT_ID = os.getenv('PROJECT_ID')


def get_li_profile_id(li_profile_url):
    for part in str(li_profile_url).rsplit('/')[::-1]:
        if part:
            return part

def validate_kendo_email(email_addr):
    url = "https://kendoemailapp.com/verifyemail?apikey={}&email={}".format(os.getenv('KENDO_API_KEY'), email_addr)
    res = requests.get(url=url)
    if res.ok:
        return res.json()

def get_kendo_person(li_profile_id):
    url = "https://kendoemailapp.com/profilebylinkedin?apikey={}&linkedin={}".format(os.getenv('KENDO_API_KEY'), li_profile_id)
    res = requests.get(url=url)
    if res.ok:
        return res.json()

def main(event, context):
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)

    session = get_session()

    if account := session.query(Account).filter(Account.account_id == payload_json['account_id']).first():
        account_local_time = datetime.now(pytz.timezone('UTC')).astimezone(pytz.timezone(account.time_zone.time_zone_code)).replace(tzinfo=None)
        for janium_campaign in account.janium_campaigns:
            for contact in janium_campaign.contacts:
                contact_info = contact.contact_info
                if cnxn_action := contact.actions.filter(Action.action_type_id == 1).first():
                    continue
                elif cnxn_req_action := contact.actions.filter(Action.action_type_id == 19).first():
                    if kendo_de_action := contact.actions.filter(Action.action_type_id == 22).first():
                        continue
                    else:
                        if campaign_steps := janium_campaign.janium_campaign_steps.filter(Janium_campaign_step.janium_campaign_step_type_id == 4).order_by(Janium_campaign_step.janium_campaign_step_delay).all():
                            if (networkdays(cnxn_req_action.action_timestamp, datetime.utcnow()) - 1) == (campaign_steps[0].janium_campaign_step_delay - 1):
                                if li_profile_url := contact_info['ulinc']['li_profile_url']:
                                    li_profile_id = get_li_profile_id(li_profile_url)
                                    kendo_person = get_kendo_person(li_profile_id)
                                    action_id = str(uuid4())
                                    if work_email := kendo_person['work_email']:
                                        if validate_kendo_email(work_email):
                                            work_email_dict = {
                                                "value": work_email,
                                                "is_valid": True
                                            }
                                        else:
                                            work_email_dict = {
                                                "value": work_email,
                                                "is_valid": False
                                            }
                                        kendo_person['work_email'] = work_email_dict
                                        contact_info['kendo'] = kendo_person
                                        contact.contact_info = contact_info
                                        if new_action := session.query(Action).filter(Action.action_id == action_id).first():
                                            pass
                                        else:
                                            new_action = Action(action_id, contact.contact_id, 22, datetime.utcnow(), None)
                                            session.add(new_action)
                                        session.commit()
                                    if private_email := kendo_person['private_email']:
                                        if validate_kendo_email(private_email):
                                            private_email_dict = {
                                                "value": private_email,
                                                "is_valid": True
                                            }
                                        else:
                                            private_email_dict = {
                                                "value": private_email,
                                                "is_valid": False
                                            }
                                        kendo_person['private_email'] = private_email_dict
                                        contact_info['kendo'] = kendo_person
                                        contact.contact_info = contact_info
                                        if new_action := session.query(Action).filter(Action.action_id == action_id).first():
                                            pass
                                        else:
                                            new_action = Action(action_id, contact.contact_id, 22, datetime.utcnow(), None)
                                            session.add(new_action)
                                        session.commit()
                                    

                else:
                    pass



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
    # get_kendo_person("brandongrant")
    # print(get_li_profile_id('https://www.linkedin.com/in/ruchikapanesar/'))
