import os
from datetime import datetime, timedelta

import google.auth
from google.cloud import secretmanager
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text, create_engine, engine, Computed, JSON)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
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
        password= pwd,
        database= os.getenv('DB_NAME'),
        host= host
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

    # Primary Keys
    client_id = Column(String(36), primary_key=True, nullable=False)

    # Foreign Keys
    client_group_id = Column(String(36), ForeignKey('client_group.id'), nullable=False)

    # Common Columns
    is_active = Column(Boolean, nullable=False, server_default=false())
    is_sending_emails = Column(Boolean, nullable=False, server_default=false())
    is_sending_li_messages = Column(Boolean, nullable=False, server_default=false())
    is_dte = Column(Boolean, nullable=False, server_default=false())

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), Computed("CONCAT(first_name, ' ', last_name)"))
    title = Column(String(250), nullable=True)
    company = Column(String(250), nullable=True)
    location = Column(String(250), nullable=True)
    primary_email = Column(String(250), nullable=False)
    campaign_management_email = Column(String(250), nullable=True)
    phone = Column(String(250), nullable=True)

    # ulinc_id = Column(String(36), nullable=False)
    # ulinc_username = Column(String(100), nullable=False)
    # ulinc_password = Column(String(100), nullable=False)

    # new_connection_wh = Column(String(250), nullable=False)
    # new_message_wh = Column(String(250), nullable=False)
    # send_message_wh = Column(String(250), nullable=False)
    

    
    dte_email = Column(String(250), nullable=True)
    dte_sender_id = Column(String(36), ForeignKey('dte_sender.id'), nullable=True)
    dte_id = Column(String(36), ForeignKey('dte.id'), nullable=True)
    assistant_first_name = Column(String(250), nullable=True)
    assistant_last_name = Column(String(250), nullable=True)
    assistant_email = Column(String(250), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    campaigns = relationship('Campaign', backref=backref('campaign_client', uselist=False), lazy=True)
    ulinc_campaigns = relationship('Ulinc_campaign', backref=backref('ulinc_campaign_client', uselist=False), lazy=False)
    contacts = relationship('Contact', backref=backref('contact_client', uselist=False), lazy=False)
    ulinc_cookie = relationship('Ulinc_cookie', backref=backref('ulinc_cookie_client', uselist=False), lazy=True)

class Client_group_manager(Base):
    __tablename__ = 'client_group_manager'

    client_group_manager_id = Column(String(36), primary_key=True, nullable=False)
    date_added = Column(DateTime, server_default=func.now())
    date_updated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), Computed("CONCAT(first_name, ' ', last_name)"))

    client_groups = relationship('Client_group', backref=backref('client_group_manager', uselist=False), lazy=False)

class Client_group(Base):
    __tablename__ = 'client_group'

    client_group_id = Column(String(36), primary_key=True, nullable=False)
    date_added = Column(DateTime, server_default=func.now())
    date_updated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))

    name = Column(String(250), nullable=False)
    description = Column(String(1000), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=false())

    client_group_manager_id = Column(String(36), ForeignKey('client_group_manager.id'), nullable=False)

    clients = relationship('Client', backref=backref('client_client_group', uselist=False), lazy=False)

class Campaign(Base):
    __tablename__ = 'campaign'

    # Primary Keys
    campaign_id = Column(String(36), primary_key=True)

    # Foreign Keys
    client_id = Column(String(36), ForeignKey('client.id'))
    credentials_id = Column(String(36), ForeignKey('credentials.credentials_id'))

    # Common Columns
    campaign_name = Column(String(512), nullable=False)
    campaign_description = Column(String(512), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=false())
    is_messenger = Column(Boolean, nullable=False, server_default=false())

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences
    contacts = relationship('Contact', backref='contact_campaign', lazy=False)
    ulinc_campaigns = relationship('Ulinc_campaign', backref='parent_janium_campaign', lazy=False)
    campaign_steps = relationship('Campaign_step', backref=backref('parent_campaign', uselist=False), lazy=True)

class Campaign_step(Base):
    __tablename__ = 'campaign_step'

    # Primary Keys
    campaign_step_id = Column(String(36), primary_key=True, nullable=False)

    # Foreign Keys
    campaign_id = Column(String(36), ForeignKey('campaign.campaign_id'), nullable=False)
    campaign_step_type_id = Column(Integer, ForeignKey('campaign_step_type.campaign_step_type_id'), nullable=False)

    # Common Columns
    campaign_step_delay = Column(Integer, nullable=False)
    campaign_step_body = Column(Text, nullable=True)
    campaign_step_subject = Column(String(1000), nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences


class Campaign_step_type(Base):
    __tablename__ = 'campaign_step_type'

    # Primary Keys
    campaign_step_type_id = Column(Integer, primary_key=True, auto_increment=True, nullable=False)

    # Foreign Keys

    # Common Columns
    campaign_step_type = Column(String(64), nullable=False)
    campaign_step_type_description = Column(String(512), nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences
    campaign_steps = relationship('Campaign_step', backref=backref('campaign_step_type', uselist=False), lazy=False)

class Ulinc_campaign(Base):
    __tablename__ = 'ulinc_campaign'

    def __init__(self, ulinc_campaign_id, client_id, name, ulinc_is_active, ulinc_campaign_id, ulinc_is_messenger, ulinc_messenger_origin_message):
        self.ulinc_campaign_id = ulinc_campaign_id
        self.client_id = client_id
        self.name = name
        self.ulinc_is_active = ulinc_is_active
        self.ulinc_campaign_id = ulinc_campaign_id
        self.ulinc_is_messenger = ulinc_is_messenger
        self.ulinc_messenger_origin_message = ulinc_messenger_origin_message

    # Primary Keys
    ulinc_campaign_id = Column(String(36), primary_key=True)
    
    # Foreign Keys
    client_id = Column(String(36), ForeignKey('client.client_id'), nullable=False)
    janium_campaign_id = Column(String(36), ForeignKey('campaign.campaign_id'), nullable=True)

    # Common Columns
    ulinc_campaign_name = Column(String(512), nullable=False)
    ulinc_is_active = Column(Boolean, nullable=False, server_default=false())
    ulinc_ulinc_campaign_id = Column(String(20), nullable=False)
    ulinc_is_messenger = Column(Boolean, nullable=False, server_default=false())

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences
    contacts = relationship('Contact', backref=backref('contact_ulinc_campaign', uselist=False), lazy=False)

class Contact(Base):
    __tablename__ = 'contact'

    def __init__(self, contact_id, client_id, campaign_id, ulinc_campaign_id, webhook_response_id, ulinc_id, ulinc_ulinc_campaign_id, first_name, last_name, title,
                 company, location, email, phone, website, li_profile_url):
        self.contact_id = contact_id

        self.client_id = client_id
        self.campaign_id = campaign_id
        self.ulinc_campaign_id = ulinc_campaign_id
        self.webhook_response_id = webhook_response_id

        self.ulinc_id = ulinc_id
        self.ulinc_ulinc_campaign_id = ulinc_ulinc_campaign_id
        self.first_name = first_name
        self.last_name = last_name
        self.title = title
        self.company = company
        self.location = location
        self.email = email
        self.phone = phone
        self.website = website
        self.li_profile_url = li_profile_url

    # Primary Keys
    contact_id = Column(String(36), primary_key=True, nullable=False)

    # Foreign Keys
    client_id = Column(String(36), ForeignKey('client.client_id'), nullable=False)
    campaign_id = Column(String(36), ForeignKey('campaign.campaign_id'), nullable=False)
    ulinc_campaign_id = Column(String(36), ForeignKey('ulinc_campaign.ulinc_campaign_id'), nullable=False)
    webhook_response_id = Column(String(36), ForeignKey('webhook_response.webhook_response_id'), nullable=False)

    # Common Columns
    ulinc_id = Column(String(20), nullable=False)
    ulinc_ulinc_campaign_id = Column(String(20), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), Computed("CONCAT(first_name, ' ', last_name)"))
    title = Column(String(250), nullable=True)
    company = Column(String(250), nullable=True)
    location = Column(String(250), nullable=True)
    email = Column(String(250), nullable=True)
    phone = Column(String(250), nullable=True)
    website = Column(String(250), nullable=True)
    li_profile_url = Column(String(500), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences
    actions = relationship('Action', backref='action_contact', lazy=True)


class Action(Base):
    __tablename__ = 'action'

    def __init__(self, action_id, contact_id, action_type_id, action_timestamp, action_message):
        self.action_id = action_id
        self.contact_id = contact_id
        self.action_type_id = action_type_id
        self.action_timestamp = action_timestamp
        self.action_message = action_message

    # Primary Keys
    action_id = Column(String(36), primary_key=True, nullable=False)

    # Foreign Keys
    contact_id = Column(String(36), ForeignKey('contact.contact_id'), nullable=False)
    action_type_id = Column(Integer, ForeignKey('action_name.action_type_id'), nullable=False)

    # Common Columns
    action_timestamp = Column(DateTime, nullable=True)
    action_message = Column(Text, nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences


class Action_type(Base): # (messenger_origin_message, new_connection_date{backdate contacts})
    __tablename__ = 'action_type'

    def __init__(self, action_type, action_type_description):
        self.action_type = action_type
        self.action_type_description = action_type_description

    # Primary Keys
    action_type_id = Column(Integer, primary_key=True, auto_increment=True, nullable=False)

    # Foreign Keys


    # Common Columns
    action_type = Column(String(64), nullable=False)
    action_type_description = Column(String(512), nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences
    actions = relationship('Action', backref=backref('action_action_name', uselist=False), lazy=False)

class Webhook_response(Base):
    __tablename__ = 'webhook_response'

    def __init__(self, webhook_response_id, client_id, webhook_response_value, webhook_response_type_id):
        self.webhook_response_id = webhook_response_id
        self.client_id = client_id
        self.webhook_response_value = webhook_response_value
        self.webhook_response_type_id = webhook_response_type_id
    
    # Primary Keys
    webhook_response_id = Column(String(36), primary_key=True, nullable=False)

    # Primary Keys
    client_id = Column(String(36), ForeignKey('client.client_id'), nullable=False)
    webhook_response_type_id = Column(Integer, ForeignKey('webhook_response_type.webhook_response_type_id'), nullable=False)

    # Primary Keys
    webhook_response_value = Column(JSON, nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences
    contacts = relationship('Contact', backref=backref('webhook_response', uselist=False), lazy=False)

class Webhook_response_type(Base):
    __tablename__ = 'webhook_response_type'

    def __init__(self, webhook_response_type, webhook_response_type_description):
        self.webhook_response_type = webhook_response_type
        self.webhook_res_type_description = webhook_response_type_description

    # Primary Keys
    webhook_response_type_id = Column(Integer, primary_key=True, auto_increment=True, nullable=False)

    # Foreign Keys

    # Common Columns
    webhook_response_type = Column(String(64), nullable=False)
    webhook_response_type_description = Column(String(512), nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences


class Dte_sender(Base):
    __tablename__ = 'dte_sender'

    id = Column(String(36), primary_key=True)
    date_added = Column(DateTime, server_default=func.now())
    date_updated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), Computed("CONCAT(first_name, ' ', last_name)"))

    email_credentials_id = Column(String(36), ForeignKey('email_credentials.id'))

class Dte(Base):
    __tablename__ = 'dte'

    id = Column(String(36), nullable=False, primary_key=True)
    date_added = Column(DateTime, server_default=func.now())
    date_updated = Column(DateTime, server_default=text('NOW() ON UPDATE NOW()'))

    name = Column(String(250), nullable=False)
    description = Column(String(1000), nullable=True)
    subject = Column(String(1000), nullable=False)
    body = Column(Text, nullable=False)

    clients = relationship('Client', backref='dte', lazy=False)

class Credentials(Base):
    __tablename__ = 'credentials'

    # Primary Keys
    credentials_id = Column(String(36), primary_key=True)

    # Foreign Keys
    client_id = Column(String(36), ForeignKey('client.client_id'))
    credentials_type_id = Column(Integer, ForeignKey('credentials_type.credentials_type_id'))
    email_server_id = Column(Integer, ForeignKey('email_server.email_server_id'))

    # Common Columns
    username = Column(String(128), nullable=True)
    password = Column(String(128), nullable=True)
    email_sender_id = Column(String(128), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences
    clients = relationship('Client', backref=backref('client_credentials', uselist=True))
    campaigns = relationship('Campaign', backref=backref('campaign_credentials', uselist=False))
    dte_senders = relationship('Dte_sender', backref=backref('dte_sender_email_credentials', uselist=False))

class Credentials_type(Base):
    __tablename__ = 'credentials_type'

    # Primary Keys
    credentials_type_id = Column(Integer, primary_key=True, auto_increment=True)

    # Foreign Keys


    # Common Columns
    credentials_type = Column(String(64), nullable=False)
    credentials_type_description = Column(String(512), nullable=True)
    credentials_type_login_url = Column(String(1024), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences


class Ulinc_client_info(Base):
    __tablename__ = 'ulinc_client_info'

    # Primary Keys
    ulinc_client_info_id = Column(String(36), primary_key=True)

    # Foreign Keys
    credentials_id = Column(String(36), ForeignKey('credentials.credentials_id'))
    cookie_id = Column(String(36), ForeignKey('cookie.cookie_id'))

    # Common Columns
    client_ulinc_id = Column(String(16), nullable=False)
    new_connection_webhook = Column(String(256), nullable=False)
    new_message_webhook = Column(String(256), nullable=False)
    send_message_webhook = Column(String(256), nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences


class Cookie(Base):
    __tablename__ = 'cookie'

    # Primary Keys
    cookie_id = Column(String(36), primary_key=True)

    # Foreign Keys
    cookie_type_id = Column(Integer, ForeignKey('cookie_type.cookie_type_id'))

    # Common Columns
    cookie_json_value = Column(JSON, nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences


class Cookie_type(Base):
    __tablename__ = 'cookie_type'

    # Primary Keys
    cookie_type_id = Column(Integer, primary_key=True, auto_increment=True)

    # Foreign Keys


    # Common Columns
    cookie_type = Column(String(64), nullable=False)
    cookie_type_description = Column(String(512), nullable=True)
    cookie_type_website_url = Column(String(1024), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences


class Email_server(Base):
    __tablename__ = 'email_server'

    # Primary Keys
    email_server_id = Column(String(36), primary_key=True)

    # Foreign Keys


    # Common Columns
    email_server_name = Column(String(64), nullable=False)
    smtp_address = Column(String(64), nullable=False)
    smtp_tls_port = Column(Integer, nullable=False)
    smtp_ssl_port = Column(Integer, nullable=False)
    imap_address = Column(String(64), nullable=False)
    imap_ssl_port = Column(Integer, nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), nullable=False)

    # SQLAlchemy Relationships and Backreferences
    credentials = relationship('Credentials', backref=backref('credentials_email_server', uselist=False))
