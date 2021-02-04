import base64
import json
from datetime import datetime
from bs4 import BeautifulSoup as Soup

import requests
import urllib3
import holidays
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_model import Client, Campaign, Action, Ulinc_cookie, Session

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def send_li_message(details):
    req_session = requests.Session()
    url = 'https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=send_message'.format(details['client_ulinc_id'], int(details['ulinc_campaign_id']))

    jar = requests.cookies.RequestsCookieJar()
    jar.set('usr', details['usr'])
    jar.set('pwd', details['pwd'])

    headers = {
        "Accept": "application/json"
    }

    message = str(details['message_text'])
    if message.__contains__('<p>'):
        soup = Soup(message, 'html.parser')
        bs = ''
        for p in soup.find_all('p'):
            bs += str(str(p.text).rstrip() + '\n')
        message = bs.rstrip()


    payload = {
        "message[contact_id]": details['contact_ulinc_id'],
        "message[text]": message
    }

    res = req_session.post(url=url, cookies=jar, headers=headers, data=payload, verify=False)
    if res.ok:
        res_json = res.json()
        if res_json['status'] == 'ok':
            # print("Sent li message to contact {} for client {}".format(details['contactid'], details['client_fullname']))

            status_url = "https://ulinc.co/{}/campaigns/{}/?do=campaigns&act=continue_sending&id={}".format(details['client_ulinc_id'], int(details['ulinc_campaign_id']), details['contact_ulinc_id'])
            status_res = req_session.get(url=status_url, cookies=jar, headers=headers, verify=False)
            if status_res.ok:
                # print("Updated Ulinc status to connected for contact {} for client {}".format(details['contactid'], details['client_fullname']))
                return details['contact_firstname']
            else:
                print("Failed to update status to connected for contact {} at request level. Response: {}".format(details['contact_id'], res.text))
                return details['contact_firstname']
        else:
            print("Li message to contact {} failed. Response: {}".format(details['contact_id'], res.text))
            return None
    else:
        print("Li message to contact {} failed at request level. Response: {}".format(details['contact_id'], res.text))
        return None


def main(event, context):
    session = Session()

    now = datetime.now()
    now_date = now.date()
    us_holidays = holidays.US()
    us_holidays.append(datetime(now.year, 12, 24)) # Christmas Eve
    us_holidays.append(datetime(now.year, 12, 31)) # New Years Eve
    us_holidays.append(datetime(now.year, 1, 1)) # New Years Day

    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    payload_json = json.loads(pubsub_message)
    # print(payload_json)

    if now_date not in us_holidays:
        # print("Running inside first if")
        if payload_json['testing'] == 'true':
            # print("testing is true inside client if")
            active_clients = session.query(Client).filter(Client.id == '63bf6eca-1d2b-11eb-9daa-42010a8002ff').all() # Nicolas Arnold Client record
        else:
            active_clients = session.query(Client).filter(Client.is_active == 1)\
                                                  .filter(Client.is_sending_li_messages == 1)\
                                                  .all()
        for client in active_clients:
            if payload_json['testing'] == 'true':
                # print("testing is true inside ulinc cookie if")
                ulinc_cookie = session.query(Ulinc_cookie).filter(Ulinc_cookie.client_id == 'e98f3c45-2f62-11eb-865a-42010a3d0004').first() # Jason's ulinc cookie values
            else:
                ulinc_cookie = session.query(Ulinc_cookie).filter(Ulinc_cookie.client_id == client.id).first()
            if ulinc_cookie is None or datetime.now() > ulinc_cookie.expires:
                print("No Ulinc cookie or cookie is expired for client {}".format(client.firstname + ' ' + client.lastname))
                continue

            active_campaigns = session.query(Campaign).filter(Campaign.client_id == client.id)\
                                                      .filter(Campaign.is_active == 1)\
                                                      .all()

            for campaign in active_campaigns:
                # print(campaign.name)
                try:
                    li_wm_targets = []
                    li_m1_targets = []
                    li_m2_targets = []
                    li_m3_targets = []
                    with db_engine.connect() as conn:
                        if campaign.is_messenger:
                            if campaign.is_li_message1 == 1 and campaign.li_message1_text != None:
                                query = "call fetch_li_m1_targets('{}', 'true')".format(campaign.id)
                                li_m1_targets = list(conn.execute(query))
                            if campaign.is_li_message2 == 1 and campaign.li_message2_text != None:
                                query = "call fetch_li_m2_targets('{}', 'true')".format(campaign.id)
                                li_m2_targets = list(conn.execute(query))
                            if campaign.is_li_message3 == 1 and campaign.li_message3_text != None:
                                query = "call fetch_li_m3_targets('{}', 'true')".format(campaign.id)
                                li_m3_targets = list(conn.execute(query))
                        else:
                            if campaign.is_welcome_message == 1 and campaign.welcome_message_text != None:
                                query = "call fetch_li_wm_targets('{}')".format(campaign.id)
                                li_wm_targets = list(conn.execute(query))
                            if campaign.is_li_message1 == 1 and campaign.li_message1_text != None:
                                query = "call fetch_li_m1_targets('{}', 'false')".format(campaign.id)
                                li_m1_targets = list(conn.execute(query))
                            if campaign.is_li_message2 == 1 and campaign.li_message2_text != None:
                                query = "call fetch_li_m2_targets('{}', 'false')".format(campaign.id)
                                li_m2_targets = list(conn.execute(query))
                            if campaign.is_li_message3 == 1 and campaign.li_message3_text != None:
                                query = "call fetch_li_m3_targets('{}', 'false')".format(campaign.id)
                                li_m3_targets = list(conn.execute(query))

                    li_message_targets = li_wm_targets + li_m1_targets + li_m2_targets + li_m3_targets
                    li_message_targets_list = []
                    for target in li_message_targets:
                        li_message_targets_list.append(
                            {
                                "contact_id": target[0],
                                "contact_firstname": target[1],
                                "contact_ulinc_id": str(target[2]).replace(str(client.ulinc_id), ''),
                                "message_text": str(target[3]).replace(r"{FirstName}", str(target[1])),
                                "ulinc_campaign_id": target[4],
                                "client_ulinc_id": client.ulincid,
                                "usr": str(ulinc_cookie.usr),
                                "pwd": str(ulinc_cookie.pwd),
                                "client_fullname": client.firstname + ' ' + client.lastname
                            }
                        )
                    recipient_list = []
                    for item in li_message_targets_list:
                        # print(item)
                        recipient_list.append(send_li_message(item))
                        # if send_li_message(item):
                        #     new_activity = Activity(item['contactid'], datetime.now(), 3, item['message_text'], None)
                        #     session.add(new_activity)
                        #     session.commit()
                except Exception as err:
                    print(err)
                print("Sent li messages to {} for client {} in campaign {}".format(recipient_list, client.firstname + ' ' + client.lastname, campaign.name))

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