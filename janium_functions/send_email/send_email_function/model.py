import os
from datetime import datetime, timedelta

from sqlalchemy import (JSON, Boolean, Column, Computed, DateTime, ForeignKey,
                        Integer, String, Text, create_engine, engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy.sql import false, func, text, true

if not os.getenv('LOCAL_DEV'):
    db_url = engine.url.URL(
        drivername='mysql+pymysql',
        username= os.getenv('DB_USER'),
        password= os.getenv('DB_PASSWORD'),
        database= os.getenv('DB_DATABASE'),
        host= os.getenv('DB_PRIVATE_HOST')
    )
else:
    db_url = engine.url.URL(
        drivername='mysql+pymysql',
        username= os.getenv('LOCAL_DB_USER'),
        password= os.getenv('LOCAL_DB_PASSWORD'),
        database= os.getenv('LOCAL_DB_DATABASE'),
        host= os.getenv('LOCAL_DB_HOST'),
        port= os.getenv('LOCAL_DB_PORT')
    )

engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Client(Base):
    __tablename__ = 'client'

    def __init__(self, client_id, client_group_id, ulinc_config_id, email_config_id, is_active, is_sending_emails, is_sending_li_messages,
                       is_dte, is_assistant, first_name, last_name, title, company, location, primary_email, campaign_management_email,
                       alternate_dte_email, phone, assistant_first_name, assistant_last_name, assistant_email, voicemail_task_delay, is_email_forward):
        self.client_id = client_id
        self.client_group_id = client_group_id
        self.ulinc_config_id = ulinc_config_id
        self.email_config_id = email_config_id
        self.is_active = is_active
        self.is_sending_emails = is_sending_emails
        self.is_sending_li_messages = is_sending_li_messages
        self.is_dte = is_dte
        self.is_assistant = is_assistant
        self.first_name = first_name
        self.last_name = last_name
        self.title = title
        self.company = company
        self.location = location
        self.primary_email = primary_email
        self.campaign_management_email = campaign_management_email
        self.alternate_dte_email = alternate_dte_email
        self.phone = phone
        self.assistant_first_name = assistant_first_name
        self.assistant_last_name = assistant_last_name
        self.assistant_email = assistant_email
        self.voicemail_task_delay = voicemail_task_delay
        self.is_email_forward = is_email_forward

    # Primary Keys
    client_id = Column(String(36), primary_key=True)

    # Foreign Keys
    client_group_id = Column(String(36), ForeignKey('client_group.client_group_id'))
    ulinc_config_id = Column(String(36), ForeignKey('ulinc_config.ulinc_config_id'))
    email_config_id = Column(String(36), ForeignKey('email_config.email_config_id'))

    # Common Columns
    is_active = Column(Boolean, nullable=False, server_default=false())
    is_sending_emails = Column(Boolean, nullable=False, server_default=false())
    is_sending_li_messages = Column(Boolean, nullable=False, server_default=false())
    is_dte = Column(Boolean, nullable=False, server_default=false())
    is_assistant = Column(Boolean, nullable=False, server_default=false())
    is_email_forward = Column(Boolean, nullable=False, server_default=false())

    first_name = Column(String(126), nullable=False)
    last_name = Column(String(126), nullable=False)
    full_name = Column(String(256), Computed("CONCAT(first_name, ' ', last_name)"))
    title = Column(String(256), nullable=True)
    company = Column(String(256), nullable=True)
    location = Column(String(256), nullable=True)
    primary_email = Column(String(256), nullable=False)
    campaign_management_email = Column(String(256), nullable=True)
    alternate_dte_email = Column(String(256), nullable=True)
    phone = Column(String(256), nullable=True)
    voicemail_task_delay = Column(Integer, nullable=True)

    assistant_first_name = Column(String(128), nullable=True)
    assistant_last_name = Column(String(128), nullable=True)
    assistant_full_name = Column(String(256), Computed("CONCAT(assistant_first_name, ' ', assistant_last_name)"))
    assistant_email = Column(String(256), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    janium_campaigns = relationship('Janium_campaign', backref=backref('janium_campaign_client', uselist=False), uselist=True, lazy='dynamic')
    ulinc_campaigns = relationship('Ulinc_campaign', backref=backref('ulinc_campaign_client', uselist=False), uselist=True, lazy='dynamic')
    contacts = relationship('Contact', backref=backref('contact_client', uselist=False), uselist=True, lazy='dynamic')
    email_config = relationship('Email_config', backref=backref('email_config_client', uselist=False), uselist=False, lazy=True)
    ulinc_config = relationship('Ulinc_config', uselist=False, lazy=True)

class Client_group(Base):
    __tablename__ = 'client_group'
    janium_client_group_id = '02131075-e537-40c6-bdac-5ccf56fa9705'

    def __init__(self, client_group_id, client_group_manager_id, dte_id, dte_sender_id, name, description, is_active):
        self.client_group_id = client_group_id
        self.client_group_manager_id = client_group_manager_id
        self.dte_id = dte_id
        self.dte_sender_id = dte_sender_id
        self.name = name
        self.description = description
        self.is_active = is_active

    # Primary Keys
    client_group_id = Column(String(36), primary_key=True, nullable=False)

    # Foreign Keys
    client_group_manager_id = Column(String(36), ForeignKey('client_group_manager.client_group_manager_id'))
    dte_id = Column(String(36), ForeignKey('dte.dte_id'))
    dte_sender_id = Column(String(36), ForeignKey('dte_sender.dte_sender_id'))

    # Common Columns
    name = Column(String(250), nullable=False)
    description = Column(String(1000), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=false())

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    clients = relationship('Client', backref=backref('client_group', uselist=False), lazy=False)
    client_group_manager = relationship('Client_group_manager', backref=backref('client_groups', uselist=True), uselist=False, lazy=True)
    dte = relationship('Dte', uselist=False, lazy=True)
    dte_sender = relationship('Dte_sender', uselist=False, lazy=True)


class Client_group_manager(Base):
    __tablename__ = 'client_group_manager'
    janium_client_group_manager_id = 'cf2c5ddc-eaba-4db1-adfd-03b133c2213b'

    def __init__(self, client_group_manager_id, first_name, last_name):
        self.client_group_manager_id = client_group_manager_id
        self.first_name = first_name
        self.last_name = last_name

    # Primary Keys
    client_group_manager_id = Column(String(36), primary_key=True, nullable=False)

    # Foreign Keys

    # Common Columns
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    full_name = Column(String(256), Computed("CONCAT(first_name, ' ', last_name)"))

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences


class Janium_campaign(Base):
    __tablename__ = 'janium_campaign'
    unassigned_janium_campaign_id = '65c96bb2-0c32-4858-a913-ca0cd902f1fe'

    def __init__(self, janium_campaign_id, client_id, email_config_id, janium_campaign_name, janium_campaign_description, is_active, is_messenger):
        self.janium_campaign_id = janium_campaign_id
        self.client_id = client_id
        self.email_config_id = email_config_id
        self.janium_campaign_name = janium_campaign_name
        self.janium_campaign_description = janium_campaign_description
        self.is_active = is_active
        self.is_messenger = is_messenger

    # Primary Keys
    janium_campaign_id = Column(String(36), primary_key=True)

    # Foreign Keys
    client_id = Column(String(36), ForeignKey('client.client_id'))
    email_config_id = Column(String(36), ForeignKey('email_config.email_config_id')) # Insert dummy value if using client email_config

    # Common Columns
    janium_campaign_name = Column(String(512), nullable=False)
    janium_campaign_description = Column(String(512), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=false())
    is_messenger = Column(Boolean, nullable=False, server_default=false())

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    contacts = relationship('Contact', backref=backref('contact_janium_campaign', uselist=False), uselist=True, lazy='dynamic')
    ulinc_campaigns = relationship('Ulinc_campaign', backref=backref('parent_janium_campaign', uselist=False), uselist=True, lazy=True)
    janium_campaign_steps = relationship('Janium_campaign_step', backref=backref('parent_janium_campaign', uselist=False), uselist=True, lazy='dynamic')

class Janium_campaign_step(Base):
    __tablename__ = 'janium_campaign_step'

    def __init__(self, janium_campaign_step_id, janium_campaign_id, janium_campaign_step_type_id,
                       is_active, janium_campaign_step_delay, janium_campaign_step_body,
                       janium_campaign_step_subject):
        self.janium_campaign_step_id = janium_campaign_step_id
        self.janium_campaign_id = janium_campaign_id
        self.janium_campaign_step_type_id = janium_campaign_step_type_id
        self.is_active = is_active
        self.janium_campaign_step_delay = janium_campaign_step_delay
        self.janium_campaign_step_body = janium_campaign_step_body
        self.janium_campaign_step_subject = janium_campaign_step_subject

    # Primary Keys
    janium_campaign_step_id = Column(String(36), primary_key=True, nullable=False)

    # Foreign Keys
    janium_campaign_id = Column(String(36), ForeignKey('janium_campaign.janium_campaign_id'), nullable=False)
    janium_campaign_step_type_id = Column(Integer, ForeignKey('janium_campaign_step_type.janium_campaign_step_type_id'), nullable=False)

    # Common Columns
    is_active = Column(Boolean, nullable=False, server_default=true())
    janium_campaign_step_delay = Column(Integer, nullable=False)
    janium_campaign_step_body = Column(Text, nullable=True)
    janium_campaign_step_subject = Column(String(1000), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    janium_campaign_step_type = relationship('Janium_campaign_step_type', uselist=False, lazy=True)


class Janium_campaign_step_type(Base):
    __tablename__ = 'janium_campaign_step_type'

    def __init__(self, janium_campaign_step_type_id, janium_campaign_step_type, janium_campaign_step_type_description):
        self.janium_campaign_step_type_id = janium_campaign_step_type_id
        self.janium_campaign_step_type = janium_campaign_step_type
        self.janium_campaign_step_type_description = janium_campaign_step_type_description

    # Primary Keys
    janium_campaign_step_type_id = Column(Integer, primary_key=True, nullable=False)

    # Foreign Keys

    # Common Columns
    janium_campaign_step_type = Column(String(64), nullable=False)
    janium_campaign_step_type_description = Column(String(512), nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences


class Ulinc_campaign(Base):
    __tablename__ = 'ulinc_campaign'
    unassigned_ulinc_campaign_id = '943c18f3-74c8-45cf-a396-1ddc89c6b9d2'

    def __init__(self, ulinc_campaign_id, client_id, janium_campaign_id, ulinc_campaign_name, ulinc_is_active, ulinc_ulinc_campaign_id, ulinc_is_messenger, ulinc_messenger_origin_message):
        self.ulinc_campaign_id = ulinc_campaign_id
        self.client_id = client_id
        self.janium_campaign_id = janium_campaign_id
        self.ulinc_campaign_name = ulinc_campaign_name
        self.ulinc_is_active = ulinc_is_active
        self.ulinc_ulinc_campaign_id = ulinc_ulinc_campaign_id
        self.ulinc_is_messenger = ulinc_is_messenger
        self.ulinc_messenger_origin_message = ulinc_messenger_origin_message

    # Primary Keys
    ulinc_campaign_id = Column(String(36), primary_key=True)
    
    # Foreign Keys
    client_id = Column(String(36), ForeignKey('client.client_id'), nullable=False)
    janium_campaign_id = Column(String(36), ForeignKey('janium_campaign.janium_campaign_id'), nullable=True)

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
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    contacts = relationship('Contact', backref=backref('contact_ulinc_campaign', uselist=False), lazy=False)

class Contact(Base):
    __tablename__ = 'contact'

    def __init__(self, contact_id, client_id, janium_campaign_id, ulinc_campaign_id, webhook_response_id, ulinc_id, ulinc_ulinc_campaign_id, first_name, last_name, title,
                 company, location, email1, email2, email3, phone, website, li_profile_url, tib_id):
        self.contact_id = contact_id

        self.client_id = client_id
        self.janium_campaign_id = janium_campaign_id
        self.ulinc_campaign_id = ulinc_campaign_id
        self.webhook_response_id = webhook_response_id

        self.ulinc_id = ulinc_id
        self.ulinc_ulinc_campaign_id = ulinc_ulinc_campaign_id
        self.first_name = first_name
        self.last_name = last_name
        self.title = title
        self.company = company
        self.location = location
        self.email1 = email1
        self.email2 = email2
        self.email3 = email3
        self.phone = phone
        self.website = website
        self.li_profile_url = li_profile_url
        self.tib_id = tib_id

    # Primary Keys
    contact_id = Column(String(36), primary_key=True, nullable=False)

    # Foreign Keys
    client_id = Column(String(36), ForeignKey('client.client_id'), nullable=False)
    janium_campaign_id = Column(String(36), ForeignKey('janium_campaign.janium_campaign_id'), nullable=False)
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
    email1 = Column(String(250), nullable=True)
    email2 = Column(String(250), nullable=True)
    email3 = Column(String(250), nullable=True)
    phone = Column(String(250), nullable=True)
    website = Column(String(250), nullable=True)
    li_profile_url = Column(String(500), nullable=True)
    tib_id = Column(String(36), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    actions = relationship('Action', backref=backref('contact', uselist=False), uselist=True, lazy='dynamic')

    def get_emails(self):
        return [self.email1, self.email2, self.email3]


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
    action_type_id = Column(Integer, ForeignKey('action_type.action_type_id'), nullable=False)

    # Common Columns
    action_timestamp = Column(DateTime, nullable=True)
    action_message = Column(Text, nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    action_type = relationship('Action_type', uselist=False, lazy=True)


class Action_type(Base): # (messenger_origin_message, new_connection_date{backdate contacts})
    __tablename__ = 'action_type'

    def __init__(self, action_type_id, action_type, action_type_description):
        self.action_type_id = action_type_id
        self.action_type = action_type
        self.action_type_description = action_type_description

    # Primary Keys
    action_type_id = Column(Integer, primary_key=True, nullable=False)

    # Foreign Keys

    # Common Columns
    action_type = Column(String(64), nullable=False)
    action_type_description = Column(String(512), nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences


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
    client_id = Column(String(36), ForeignKey('client.client_id'))
    webhook_response_type_id = Column(Integer, ForeignKey('webhook_response_type.webhook_response_type_id'))

    # Primary Keys
    webhook_response_value = Column(JSON, nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    contacts = relationship('Contact', backref=backref('webhook_response', uselist=False), lazy=False)

class Webhook_response_type(Base):
    __tablename__ = 'webhook_response_type'

    def __init__(self, webhook_response_type_id, webhook_response_type, webhook_response_type_description):
        self.webhook_response_type_id = webhook_response_type_id
        self.webhook_response_type = webhook_response_type
        self.webhook_response_type_description = webhook_response_type_description

    # Primary Keys
    webhook_response_type_id = Column(Integer, primary_key=True, nullable=False)

    # Foreign Keys

    # Common Columns
    webhook_response_type = Column(String(64), nullable=False)
    webhook_response_type_description = Column(String(512), nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences


class Dte_sender(Base):
    __tablename__ = 'dte_sender'
    janium_dte_sender_id = '5202aea8-ab36-4e6d-9cda-5994d2c0bbe1'

    def __init__(self, dte_sender_id, email_config_id, first_name, last_name):
        self.dte_sender_id = dte_sender_id
        self.email_config_id = email_config_id
        self.first_name = first_name
        self.last_name = last_name

    # Primary Keys
    dte_sender_id = Column(String(36), primary_key=True)

    # Foreign Keys
    email_config_id = Column(String(36), ForeignKey('email_config.email_config_id'))

    # Common Columns
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), Computed("CONCAT(first_name, ' ', last_name)"))

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    email_config = relationship('Email_config', uselist=False, lazy=True)


class Dte(Base):
    __tablename__ = 'dte'
    janium_dte_id = '38429485-59e1-4eeb-a4bb-05696ead8e49'

    def __init__(self, dte_id, name, description, subject, body):
        self.dte_id = dte_id
        self.name = name
        self.description = description
        self.subject = subject
        self.body = body

    # Primary Keys
    dte_id = Column(String(36), primary_key=True)

    # Foreign Keys

    # Common Columns
    name = Column(String(250), nullable=False)
    description = Column(String(1000), nullable=True)
    subject = Column(String(1000), nullable=False)
    body = Column(Text, nullable=False)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences


class Email_config(Base):
    __tablename__ = 'email_config'
    janium_email_config_id = '709f79b3-7a20-43ff-844a-4f014fa4e406'
    unassigned_email_config_id = '7c5c4aa2-2c6e-4e3d-947e-6efdae4366a1'

    def __init__(self, email_config_id, credentials_id, email_server_id, is_sendgrid, sendgrid_sender_id):
        self.email_config_id = email_config_id
        self.credentials_id = credentials_id
        self.email_server_id = email_server_id
        self.is_sendgrid = is_sendgrid
        self.sendgrid_sender_id = sendgrid_sender_id

    # Primary Keys
    email_config_id = Column(String(36), primary_key=True)

    # Foreign Keys
    credentials_id = Column(String(36), ForeignKey('credentials.credentials_id'))
    email_server_id = Column(String(36), ForeignKey('email_server.email_server_id'))

    # Common Columns
    is_sendgrid = Column(Boolean, nullable=False, server_default=false())
    sendgrid_sender_id = Column(String(36), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    credentials = relationship('Credentials', backref=backref('email_config', uselist=False), uselist=False, lazy=True)
    email_server = relationship('Email_server', uselist=False, lazy=True)

class Email_server(Base):
    __tablename__ = 'email_server'

    def __init__(self, email_server_id, email_server_name, smtp_address, smtp_tls_port, smtp_ssl_port, imap_address, imap_ssl_port):
        self.email_server_id = email_server_id
        self.email_server_name = email_server_name
        self.smtp_address = smtp_address
        self.smtp_tls_port = smtp_tls_port
        self.smtp_ssl_port = smtp_ssl_port
        self.imap_address = imap_address
        self.imap_ssl_port = imap_ssl_port

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
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences


class Ulinc_config(Base):
    __tablename__ = 'ulinc_config'
    unassigned_ulinc_config_id = 'dff0e400-b338-4bc5-bb99-617bade305bd'

    def __init__(self, ulinc_config_id, credentials_id, cookie_id, client_ulinc_id, new_connection_webhook, new_message_webhook, send_message_webhook):
        self.ulinc_config_id = ulinc_config_id
        self.credentials_id = credentials_id
        self.cookie_id = cookie_id
        self.client_ulinc_id = client_ulinc_id
        self.new_connection_webhook = new_connection_webhook
        self.new_message_webhook = new_message_webhook
        self.send_message_webhook = send_message_webhook

    # Primary Keys
    ulinc_config_id = Column(String(36), primary_key=True)

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
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    credentials = relationship('Credentials', backref=backref('ulinc_config', uselist=False), uselist=False)
    cookie = relationship('Cookie', uselist=False)


class Credentials(Base):
    __tablename__ = 'credentials'
    janium_email_app_credentials_id = 'a217fb95-0a28-49ba-a18a-a0298d0b68b3'

    def __init__(self, credentials_id, username, password):
        self.credentials_id = credentials_id
        self.username = username
        self.password = password

    # Primary Keys
    credentials_id = Column(String(36), primary_key=True)

    # Foreign Keys

    # Common Columns
    username = Column(String(128), nullable=True)
    password = Column(String(128), nullable=True)

    # Table Metadata
    asOfStartTime = Column(DateTime, server_default=func.now())
    asOfEndTime = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    effective_start_date = Column(DateTime, server_default=func.now())
    effective_end_date = Column(DateTime, server_default=text("'9999-12-31 10:10:10'"))
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences


class Cookie(Base):
    __tablename__ = 'cookie'
    unassigned_cookie_id = 'dd0dfdaa-3d58-4d96-85dc-cd68307f528d'

    def __init__(self, cookie_id, cookie_type_id, cookie_json_value):
        self.cookie_id = cookie_id
        self.cookie_type_id = cookie_type_id
        self.cookie_json_value = cookie_json_value

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
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
    cookie_type = relationship('Cookie_type', uselist=False, lazy=True)


class Cookie_type(Base):
    __tablename__ = 'cookie_type'

    def __init__(self, cookie_type_id, cookie_type, cookie_type_description):
        self.cookie_type_id = cookie_type_id
        self.cookie_type = cookie_type
        self.cookie_type_description = cookie_type_description

    # Primary Keys
    cookie_type_id = Column(Integer, primary_key=True)

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
    updatedBy = Column(String(36), server_default=text("'45279d74-b359-49cd-bb94-d75e06ae64bc'"))

    # SQLAlchemy Relationships and Backreferences
