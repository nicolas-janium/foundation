import email
from datetime import datetime
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_model import Client, Action, Contact, Session


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
    
    client = session.query(Client).filter(Contact.email == to_addr).first()
    if client:
        contacts = client.contacts
        for contact in contacts:
            if contact.email == from_addr:
                new_action = Action(str(uuid4()), contact.id, datetime.now(), 6, None, None, False, None)
                session.add(new_action)
                session.commit()

    return '1'

if __name__ == '__main__':
    pass
    # session = Session()

    # client = session.query(Client).first()

    # contacts = client.contacts.filter(Contact.firstname == 'Sarah').all()
    # for contact in contacts:
    #     print(contact.lastname)