import os
from datetime import datetime, timedelta

import google.auth
from google.cloud import secretmanager
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text, create_engine, engine, Computed, JSON)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func, false, text

def get_mysql_info():
    creds, project = google.auth.default()
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    project_id = "janium0-0"

    pass_secret_name = "gcf-mysql-password"
    pass_request = {"name": f"projects/{project_id}/secrets/{pass_secret_name}/versions/latest"}
    pass_response = client.access_secret_version(pass_request)

    host_secret_name = "janium-mysql-master-private-ip"
    host_request = {"name": f"projects/{project_id}/secrets/{host_secret_name}/versions/latest"}
    host_response = client.access_secret_version(host_request)

    return (pass_response.payload.data.decode('UTF-8'), host_response.payload.data.decode('UTF-8'))

if os.getenv('IS_CLOUD'):
    pwd, host = get_mysql_info()
    db_url = engine.url.URL(
        drivername=os.getenv('DRIVER_NAME'),
        username= os.getenv('DB_USER'),
        password= get_mysql_password(),
        database= os.getenv('DB_NAME'),
        host= get_mysql_host()
    )
else:
    db_url = engine.url.URL(
        drivername=os.getenv('DRIVER_NAME'),
        username= os.getenv('DB_USER'),
        password= os.getenv('DB_PASSWORD'),
        database= os.getenv('DB_NAME'),
        host= os.getenv('DB_HOST'),
        port= os.getenv('DB_PORT')
    )

engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Client(Base):
    __tablename__ = 'client'

    id = Column(String(36), primary_key=True, nullable=False)
    dateadded = Column(DateTime, server_default=func.now())
    dateupdated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    fullname = Column(String(200), Computed("CONCAT(firstname, ' ', lastname)"))
    title = Column(String(250), nullable=True)
    company = Column(String(250), nullable=True)
    location = Column(String(250), nullable=True)
    email = Column(String(250), nullable=False)
    campaign_management_email = Column(String(250), nullable=True)
    phone = Column(String(250), nullable=True)
    ulinc_id = Column(String(36), nullable=False)
    ulinc_username = Column(String(100), nullable=False)
    ulinc_password = Column(String(100), nullable=False)
    email_app_username = Column(String(100), nullable=True)
    email_app_password = Column(String(100), nullable=True)
    email_server_id = Column(String(36), ForeignKey('email_server.id'), nullable=True)
    new_connection_wh = Column(String(250), nullable=False)
    new_message_wh = Column(String(250), nullable=False)
    send_message_wh = Column(String(250), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=false())
    is_sending_emails = Column(Boolean, nullable=False, server_default=false())
    is_sending_li_messages = Column(Boolean, nullable=False, server_default=false())
    is_sendgrid = Column(Boolean, nullable=False, server_default=false())
    sendgrid_sender_id = Column(String(36), nullable=True)
    client_manager = Column(String(36), ForeignKey('client_manager.id'), nullable=True)
    is_dte = Column(Boolean, nullable=False, server_default=false())
    dte_email = Column(String(250), nullable=True)
    dte_sender_id = Column(String(36), ForeignKey('dte_sender.id'), nullable=True)
    dte_id = Column(String(36), ForeignKey('dte.id'), nullable=True)
    assistant_firstname = Column(String(250), nullable=True)
    assistant_lastname = Column(String(250), nullable=True)
    assistant_email = Column(String(250), nullable=True)

    campaigns = relationship('Campaign', backref='client_campaigns', lazy=True)
    ulinc_campaigns = relationship('Ulinc_campaign', backref='client_ulinc_campaigns', lazy=False)
    contacts = relationship('Contact', backref='client_contacts', lazy=False)
    ulinc_cookie = relationship('Ulinc_cookie', backref='client_ulinc_cookie', lazy=True, uselist=False)
    # dte_sender = relationship('Dte_sender', backref='dte_sender_clients', lazy=False, uselist=False)


class Campaign(Base):
    __tablename__ = 'campaign'

    id = Column(String(36), primary_key=True, nullable=False)
    dateadded = Column(DateTime, server_default=func.now())
    client_id = Column(String(36), ForeignKey('client.id'), nullable=False) # Foreign key to client
    name = Column(String(250), nullable=False)
    description = Column(String(1000), nullable=True)

    dateupdated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))
    is_active = Column(Boolean, nullable=False, server_default=false())
    is_messenger = Column(Boolean, nullable=False, server_default=false())
    use_alternate_email = Column(Boolean, nullable=False, server_default=false())
    is_sendgrid = Column(Boolean, nullable=False, server_default=false())
    email_app_username = Column(String(100), nullable=True)
    email_app_password = Column(String(100), nullable=True)
    email_server_id = Column(String(36), nullable=True)
    sendgrid_sender_id = Column(String(36), nullable=True)

    send_email_after_wm = Column(Boolean, nullable=False, server_default=false())
    email_after_wm_body = Column(Text, nullable=True)
    email_after_wm_subject = Column(String(500), nullable=True)
    email_after_wm_delay = Column(Integer, nullable=True)

    send_followup1_email = Column(Boolean, nullable=False, server_default=false())
    followup1_email_body = Column(Text, nullable=True)
    followup1_email_subject = Column(String(500), nullable=True)
    followup1_email_delay = Column(Integer, nullable=True)

    send_followup2_email = Column(Boolean, nullable=False, server_default=false())
    followup2_email_body = Column(Text, nullable=True)
    followup2_email_subject = Column(String(500), nullable=True)
    followup2_email_delay = Column(Integer, nullable=True)

    send_followup3_email = Column(Boolean, nullable=False, server_default=false())
    followup3_email_body = Column(Text, nullable=True)
    followup3_email_subject = Column(String(500), nullable=True)
    followup3_email_delay = Column(Integer, nullable=True)

    is_welcome_message = Column(Boolean, nullable=False, server_default=false())
    welcome_message_text = Column(Text, nullable=True)
    welcome_message_delay = Column(Integer, nullable=True)
    is_li_message1 = Column(Boolean, nullable=False, server_default=false())
    li_message1_text = Column(Text, nullable=True)
    li_message1_delay = Column(Integer, nullable=True)
    is_li_message2 = Column(Boolean, nullable=False, server_default=false())
    li_message2_text = Column(Text, nullable=True)
    li_message2_delay = Column(Integer, nullable=True)
    is_li_message3 = Column(Boolean, nullable=False, server_default=false())
    li_message3_text = Column(Text, nullable=True)
    li_message3_delay = Column(Integer, nullable=True)

    has_voicemail1 = Column(Boolean, nullable=False, server_default=false())
    voicemail1_delay = Column(Integer, nullable=True)
    has_voicemail2 = Column(Boolean, nullable=False, server_default=false())
    voicemail2_delay = Column(Integer, nullable=True)
    has_voicemail3 = Column(Boolean, nullable=False, server_default=false())
    voicemail3_delay = Column(Integer, nullable=True)

    contacts = relationship('Contact', backref='campaign_contacts', lazy=False)
    ulinc_campaigns = relationship('Ulinc_campaign', backref='campaign_ulinc_campaigns', lazy=False)

class Ulinc_campaign(Base):
    __tablename__ = 'ulinc_campaign'

    def __init__(self, id, client_id, name, ulinc_is_active, ulinc_campaign_id, ulinc_is_messenger, ulinc_messenger_origin_message):
        self.id = id
        self.client_id = client_id
        self.name = name
        self.ulinc_is_active = ulinc_is_active
        self.ulinc_campaign_id = ulinc_campaign_id
        self.ulinc_is_messenger = ulinc_is_messenger
        self.ulinc_messenger_origin_message = ulinc_messenger_origin_message

    id = Column(String(36), primary_key=True)
    dateadded = Column(DateTime, server_default=func.now())
    dateupdated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))
    client_id = Column(String(36), ForeignKey('client.id'), nullable=False)
    janium_campaign_id = Column(String(36), ForeignKey('campaign.id'), nullable=True)
    name = Column(String(250), nullable=False)
    ulinc_is_active = Column(Boolean, nullable=False, server_default=false())
    ulinc_campaign_id = Column(String(20), nullable=False)
    ulinc_is_messenger = Column(Boolean, nullable=False, server_default=false())

    contacts = relationship('Contact', backref='ulinc_campaign_contacts', lazy=False)


class Contact(Base):
    __tablename__ = 'contact'

    def __init__(self, contact_id, campaign_id, client_id, ulinc_id, ulinc_campaign_id, internal_ulinc_campaign_id, firstname, lastname, title,
                 company, location, email, phone, website, li_profile_url, from_wh_id):
        self.id = contact_id
        self.campaign_id = campaign_id
        self.client_id = client_id
        self.ulinc_id = ulinc_id
        self.ulinc_campaign_id = ulinc_campaign_id
        self.internal_ulinc_campaign_id = internal_ulinc_campaign_id
        self.firstname = firstname
        self.lastname = lastname
        self.title = title
        self.company = company
        self.location = location
        self.email = email
        self.phone = phone
        self.website = website
        self.li_profile_url = li_profile_url
        self.from_wh_id = from_wh_id

    id = Column(String(36), primary_key=True, nullable=False)
    dateadded = Column(DateTime, server_default=func.now())
    dateupdated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))
    campaign_id = Column(String(36), ForeignKey('campaign.id'), nullable=False)
    client_id = Column(String(36), ForeignKey('client.id'), nullable=False)
    ulinc_id = Column(String(20), nullable=False)
    ulinc_campaign_id = Column(String(20), nullable=False)
    internal_ulinc_campaign_id = Column(String(36), ForeignKey('ulinc_campaign.id'), nullable=False)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    fullname = Column(String(200), Computed("CONCAT(firstname, ' ', lastname)"))
    title = Column(String(250), nullable=True)
    company = Column(String(250), nullable=True)
    location = Column(String(250), nullable=True)
    email = Column(String(250), nullable=True)
    phone = Column(String(250), nullable=True)
    website = Column(String(250), nullable=True)
    li_profile_url = Column(String(500), nullable=True)
    from_wh_id = Column(String(36), ForeignKey('webhook_res.id'), nullable=False)

    actions = relationship('Action', backref='contact_actions', lazy=True, order_by='Action.action_timestamp.desc()')


class Action(Base):
    __tablename__ = 'action'

    def __init__(self, id, contact_id, action_timestamp, action_code, action_message, is_ulinc_messenger_origin, ulinc_messenger_campaign_id):
        self.id = id
        self.contact_id = contact_id
        self.action_timestamp = action_timestamp
        self.action_code = action_code
        self.action_message = action_message
        self.is_ulinc_messenger_origin = is_ulinc_messenger_origin
        self.ulinc_messenger_campaign_id = ulinc_messenger_campaign_id

    id = Column(String(36), primary_key=True, nullable=False)
    contact_id = Column(String(36), ForeignKey('contact.id'), nullable=False)
    dateadded = Column(DateTime, server_default=func.now())
    action_timestamp = Column(DateTime, nullable=True)
    action_code = Column(Integer, ForeignKey('action_name.code'), nullable=False)
    action_message = Column(Text, nullable=True)
    is_ulinc_messenger_origin = Column(Boolean, nullable=False, server_default=false())
    ulinc_messenger_campaign_id = Column(String(10), nullable=True)

class Action_name(Base):
    __tablename__ = 'action_name'

    def __init__(self, code, name):
        self.code = code
        self.name = name

    code = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(100), nullable=False)

class Webhook_res(Base):
    __tablename__ = 'webhook_res'

    def __init__(self, id, client_id, json_value, wh_type):
        self.id = id
        self.client_id = client_id
        self.json_value = json_value
        self.wh_type = wh_type
    
    id = Column(String(36), primary_key=True, nullable=False)
    client_id = Column(String(36), ForeignKey('client.id'), nullable=False)
    dateadded = Column(DateTime, server_default=func.now())
    json_value = Column(JSON, nullable=False)
    wh_type = Column(String(50), nullable=False)

    contacts = relationship('Contact', backref='webhook_res', lazy=False)

class Dte_sender(Base):
    __tablename__ = 'dte_sender'

    id = Column(String(36), primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    fullname = Column(String(200), Computed("CONCAT(firstname, ' ', lastname)"))
    dateadded = Column(DateTime, server_default=func.now())
    dateupdated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))
    is_sendgrid = Column(Boolean, nullable=False, server_default=false())
    email_app_username = Column(String(100), nullable=True)
    email_app_password = Column(String(100), nullable=True)
    sendgrid_sender_id = Column(String(36), nullable=True)

    clients = relationship('Client', backref='client_dte_sender', lazy=False)

class Client_manager(Base):
    __tablename__ = 'client_manager'

    id = Column(String(36), nullable=False, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    fullname = Column(String(200), Computed("CONCAT(firstname, ' ', lastname)"))
    email = Column(String(100), nullable=False)

    clients = relationship('Client', backref='client_manager_clients', lazy=False)
    dtes = relationship('Dte', backref='client_manager_dtes', lazy=False)

class Dte(Base):
    __tablename__ = 'dte'

    id = Column(String(36), nullable=False, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(1000), nullable=True)
    client_manager_id = Column(String(36), ForeignKey('client_manager.id'), nullable=False)
    subject = Column(String(1000), nullable=False)
    body = Column(Text, nullable=False)

    clients = relationship('Client', backref='client_dte', lazy=False)


class Email_server(Base):
    __tablename__ = 'email_server'

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    smtp_address = Column(String(100), nullable=False)
    smtp_tls_port = Column(Integer, nullable=False)
    smtp_ssl_port = Column(Integer, nullable=False)
    imap_address = Column(String(100), nullable=True)
    imap_ssl_port = Column(Integer, nullable=True)

class Ulinc_cookie(Base):
    __tablename__ = 'ulinc_cookie'

    def __init__(self, id, client_id, usr, pwd, expires):
        self.id = id
        self.client_id = client_id
        self.usr = usr
        self.pwd = pwd
        self.expires = expires

    id = Column(String(36), primary_key=True)
    dateadded = Column(DateTime, server_default=func.now())
    client_id = Column(String(36), ForeignKey('client.id'), nullable=False)
    usr = Column(String(100), nullable=False)
    pwd = Column(String(100), nullable=False)
    expires = Column(DateTime, nullable=False)