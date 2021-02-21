import email
from datetime import datetime, timedelta
from uuid import uuid4

from model import *

mtn_time = datetime.utcnow() - timedelta(hours=7)

def main(request):
    session = Session()

    req_dict = request.form.to_dict()
    from_addr = email.utils.parseaddr(req_dict['from'])[1] # Contact email addr
    to_addr = email.utils.parseaddr(req_dict['to'])[1] # Contact email addr

    email_message = email.message_from_string(req_dict['email'])
    body = ''

    if email_message.is_multipart():
        for part in email_message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    else:
        body = email_message.get_payload(decode=True)

    if from_addr == 'forwarding-noreply@google.com':
        print(body)

    for credentials in session.query(Credentials).filter(Credentials.username == to_addr).all():
        if client := credentials.email_config.email_config_client:
            for contact in client.contacts:
                if from_addr in contact.emails:
                    new_action = Action(str(uuid4()), contact.contact_id, 6, mtn_time, body)
                    session.add(new_action)
                    session.commit()

    return '1'

if __name__ == '__main__':
    pass
    # session = Session()

    # if email_config := session.query(Credentials).filter(Credentials.username == 'jason@thecxo100.com').first().email_config:
    #     client = email_config.email_config_client
    #     print(client.full_name)
