from db_model import *
from uuid import uuid4
from datetime import datetime, timedelta
import requests

mtn_time = datetime.utcnow() - timedelta(hours=7)

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
                    print("Invalid contact_ulincid")
                elif len(res) < 500:
                    print("Contact {} marked to no interest in Ulinc".format(contact.full_name))
                    return r"""\
                    <h1 style="text-align: center;">Janium: Disqualify Contact</h1>
                    <h4 style="text-align: center;">Contact/Propsect: {contact}</h4>
                    <hr />
                    <p style="text-align: center;">This contact has been disqualified. They will not receive any other messaging, and they were marked to "No Interest" in Ulinc.</p>\
                    """.replace(r"{contact}", contact.full_name)
                elif len(res) > 500:
                    print("Invalid cookie")
            else:
                print(r.text)
            
            return r"""\
            <h1 style="text-align: center;">Janium: Disqualify Contact</h1>
            <h4 style="text-align: center;">Contact/Propsect: {contact}</h4>
            <hr />
            <p style="text-align: center;">This contact has been disqualified. They will not receive any other messaging.</p>\
            """.replace(r"{contact}", contact.full_name)
        else:
            print(f"No Ulinc Cookie for {client.full_name}")
    else:
        return 'Contact {} does not exist in the Janium database'.format(contact.full_name)
