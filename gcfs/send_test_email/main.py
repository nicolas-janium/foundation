import os
import random
import smtplib
import string
from email.header import Header
from email.message import EmailMessage
from email.utils import make_msgid

import google.auth
import lastpass
from bs4 import BeautifulSoup as Soup
from google.cloud import secretmanager


def message_id_generator():
    rstring = ''.join(random.choice(string.ascii_letters) for x in range(13))
    return make_msgid(domain='mail.gmail.com', idstring=rstring)

def get_lpass_master():
    creds, project = google.auth.default()
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    secret_name = "janium-lastpass-master-master-password"
    project_id = "janium0-0"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def get_credentials(lpass_id):
    vault = lastpass.Vault.open_remote('lastpass@janium.io', get_lpass_master())
    return [(i.username.decode('UTF-8'), i.password.decode('UTF-8')) for i in vault.accounts if i.id == bytes(lpass_id, 'utf-8')][0]

def add_tracker(email_html, contactid, messageid):
    tracker_url = str(os.getenv('TRACKER_URL'))
    tracker_url += "?contactid={}&messageid={}".format(contactid, messageid)
    soup = Soup(email_html, 'html.parser')
    div = soup.new_tag('div')
    img = soup.new_tag('img', attrs={'height': '0', 'width': '0', 'src': tracker_url})
    div.append(img)
    soup.append(div)
    return str(soup)

def add_email_opt_out(email_html, contactid, contact_email):
    opt_out_url = str(os.getenv('EMAIL_OPT_OUT_URL'))
    opt_out_url += "?contactid={}&landing=1&contact_email={}".format(contactid, contact_email)
    soup = Soup(email_html, 'html.parser')
    div = soup.new_tag('div')
    email_preferences = r"""
        <p style="text-align: center;font-size: 10px;"><a href="{opt_out_url}">Email Preferences/Unsubscribe</a>.</p>
        """
    p_soup = Soup(email_preferences, 'html.parser')
    div.append(p_soup)
    soup.append(div)
    return str(soup).replace(r'{opt_out_url}', opt_out_url)

def send_email(details):
    username, password = get_credentials('2575208259370624104')
    recipient = details['contact_email']

    contactid = '00f0be86-5a98-4323-8a68-9da074bb49a1'
    messageid = message_id_generator()
    main_email = EmailMessage()

    main_email['Subject'] = details['email_subject']
    main_email['From'] = str(Header('{} <{}>')).format('Janium Test', username)
    main_email['To'] = recipient
    main_email['Message-ID'] = messageid

    email_html = add_tracker(details['email_body'], contactid, messageid)
    email_html = add_email_opt_out(email_html, contactid, details['contact_email'])
    email_html = email_html.replace(r"{FirstName}", details['contact_firstname'])
    main_email.set_content(email_html, 'html')

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.send_message(main_email)
            print("sent email to {}".format(recipient))
    except Exception as err:
        print(err)

def main(request):
    request_json = request.get_json()
    if request_json:
        item = request_json['data']
        send_email(item)
    # if request:
    #     item = request['data']
    #     send_email(item)
    return "Hello, World"


# if __name__ == '__main__':
#     sef_payload = {
#     "trigger-type": "function",
#     "from": "director-function",
#     "data":{
#         "contact_firstname": "Bryce",
#         "contact_email": "nic@janium.io",
#         "email_subject": "This is a wm subject line",
#         "email_body": r'<div dir="ltr">Hello {firstname},<div><br></div><div>This is a test email.</div><div><br></div><div>Goodbye,</div><div>Nicolas</div></div>'
#         }
#     }

#     main(sef_payload)
