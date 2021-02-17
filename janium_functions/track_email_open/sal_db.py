import os

import google.auth
from google.cloud import secretmanager
from google.oauth2 import service_account
from sqlalchemy import (JSON, Boolean, Column, DateTime, Integer, String, Text,
                        engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import FetchedValue

Base = declarative_base()

class Client(Base):
    __tablename__ = 'client'

    id = Column(String(36), primary_key=True, nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    firstname = Column(String(250), nullable=False)
    lastname = Column(String(250), nullable=False)
    title = Column(String(250))
    company = Column(String(250))
    location = Column(String(250))
    email = Column(String(250))
    dte_email = Column(String(250))
    campaign_management_email = Column(String(250))
    phone = Column(String(250))
    ulincid = Column(String(36), nullable=False)
    ulinc_username = Column(String(100))
    ulinc_password = Column(String(100))
    email_app_username = Column(String(100))
    email_app_password = Column(String(100))
    lpass_email = Column(String(250))
    lpass_ulinc = Column(String(250))
    lpass_li = Column(String(250))
    email_server_id = Column(Integer, nullable=False)
    new_connection_wh = Column(String(250))
    new_message_wh = Column(String(250))
    send_message_wh = Column(String(250))
    isactive = Column(Boolean, nullable=False)
    is_sending_emails = Column(Boolean, nullable=False)
    is_sending_li_messages = Column(Boolean, nullable=False)
    is_sendgrid = Column(Boolean)
    sendgrid_sender_id = Column(Integer)
    clientmanager = Column(String(36), nullable=False)
    # janium_group_id = Column(String(36), nullable=False)
    is_dte = Column(Boolean, nullable=False)
    dte_sender_id = Column(String(36), nullable=False)
    daily_tasks_email_id = Column(String(36))
    client_sheet_id = Column(String(100))
    dateupdated = Column(DateTime, server_default=FetchedValue())
    assistant_firstname = Column(String(250), nullable=True)
    assistant_lastname = Column(String(250), nullable=True)
    assistant_email = Column(String(250), nullable=True)


class Campaign(Base):
    __tablename__ = 'campaign'

    id = Column(String(36), primary_key=True, nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    clientid = Column(String(36), nullable=False)
    janium_campaign_type_id = Column(String(36), nullable=False)
    name = Column(String(250))
    description = Column(String(1000))
    send_email_after_c = Column(Boolean)
    automate_email_after_c = Column(Boolean)
    email_after_c_sendgrid_template_id = Column(String(40))
    email_after_c_body = Column(Text)
    email_after_c_subject = Column(String(500))
    email_after_c_delay = Column(Integer)
    send_email_after_wm = Column(Boolean)
    automate_email_after_wm = Column(Boolean)
    email_after_wm_sendgrid_template_id = Column(String(40))
    email_after_wm_body = Column(Text)
    email_after_wm_subject = Column(String(500))
    email_after_wm_delay = Column(Integer)
    send_followup1_email = Column(Boolean)
    automate_followup1_email = Column(Boolean)
    followup1_email_sendgrid_template_id = Column(String(40))
    followup1_email_body = Column(Text)
    followup1_email_subject = Column(String(500))
    followup1_email_delay = Column(Integer)
    send_followup2_email = Column(Boolean)
    automate_followup2_email = Column(Boolean)
    followup2_email_sendgrid_template_id = Column(String(40))
    followup2_email_body = Column(Text)
    followup2_email_subject = Column(String(500))
    followup2_email_delay = Column(Integer)
    send_followup3_email = Column(Boolean)
    automate_followup3_email = Column(Boolean)
    followup3_email_sendgrid_template_id = Column(String(40))
    followup3_email_body = Column(Text)
    followup3_email_subject = Column(String(500))
    followup3_email_delay = Column(Integer)
    has_voicemail1 = Column(Boolean)
    voicemail1_delay = Column(Integer)
    has_voicemail2 = Column(Boolean)
    voicemail2_delay = Column(Integer)
    has_voicemail3 = Column(Boolean)
    voicemail3_delay = Column(Integer)
    is_welcome_message = Column(Boolean)
    welcome_message_text = Column(Text)
    welcome_message_delay = Column(Integer)
    is_li_message1 = Column(Boolean)
    li_message1_text = Column(Text)
    li_message1_delay = Column(Integer)
    is_li_message2 = Column(Boolean)
    li_message2_text = Column(Text)
    li_message2_delay = Column(Integer)
    is_li_message3 = Column(Boolean)
    li_message3_text = Column(Text)
    li_message3_delay = Column(Integer)
    dateupdated = Column(DateTime, server_default=FetchedValue())
    isactive = Column(Boolean, nullable=False)
    is_messenger = Column(Boolean, nullable=False)
    use_alternate_email = Column(Boolean)
    email_app_username = Column(String(100))
    email_app_password = Column(String(100))
    email_server_id = Column(Integer)
    sendgrid_sender_id = Column(Integer)



class Contact(Base):
    __tablename__ = 'contact'

    def __init__(self, contactid, campaign_id, clientid, ulincid, ulinc_campaignid, firstname, lastname, title,
                 company, location, email, phone, website, li_profile_url, from_wh_id, from_wh_type
                ):
        self.id = contactid
        self.campaignid = campaign_id
        self.clientid = clientid
        self.ulincid = ulincid
        self.ulinc_campaignid = ulinc_campaignid
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
        self.from_wh_type = from_wh_type

    id = Column(String(36), primary_key=True, nullable=False)
    campaignid = Column(String(36), nullable=False)
    clientid = Column(String(36), nullable=False)
    ulincid = Column(String(20), nullable=False)
    ulinc_campaignid = Column(String(20), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    firstname = Column(String(250), nullable=False)
    lastname = Column(String(250), nullable=False)
    title = Column(String(250))
    company = Column(String(250))
    location = Column(String(250))
    email = Column(String(250))
    phone = Column(String(250))
    website = Column(String(250))
    li_profile_url = Column(String(500))
    dateupdated = Column(DateTime, server_default=FetchedValue())
    from_wh_id = Column(String(36), nullable=False)
    from_wh_type = Column(String(36), nullable=False)


class Activity(Base):
    __tablename__ = 'activity'

    def __init__(self, contactid, action_timestamp, action_code, action_message, email_message_id, is_ulinc_messenger_origin, ulinc_messenger_campaign_id):
        self.contactid = contactid
        self.action_timestamp = action_timestamp
        self.action_code = action_code
        self.action_message = action_message
        self.email_message_id = email_message_id
        self.is_ulinc_messenger_origin = is_ulinc_messenger_origin
        self.ulinc_messenger_campaign_id = ulinc_messenger_campaign_id

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    contactid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    action_timestamp = Column(DateTime)
    action_code = Column(Integer, nullable=False)
    action_message = Column(Text)
    email_message_id = Column(String(100))
    is_ulinc_messenger_origin = Column(Boolean)
    ulinc_messenger_campaign_id = Column(String(20))

class Action(Base):
    __tablename__ = 'action'

    def __init__(self, action_code, action_name):
        self.action_code = action_code
        self.action_name = action_name

    action_code = Column(Integer, nullable=False, primary_key=True)
    action_name = Column(String(250), nullable=False)


class New_connection_wh_res(Base):
    __tablename__ = 'new_connection_wh_res'

    def __init__(self, id, clientid, jdata):
        self.id = id
        self.clientid = clientid
        self.jdata = jdata

    id = Column(String(36), primary_key=True)
    clientid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    jdata = Column(JSON, nullable=False)

class New_message_wh_res(Base):
    __tablename__ = 'new_message_wh_res'

    def __init__(self, id, clientid, jdata):
        self.id = id
        self.clientid = clientid
        self.jdata = jdata

    id = Column(String(36), primary_key=True)
    clientid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    jdata = Column(JSON, nullable=False)

class Send_message_wh_res(Base):
    __tablename__ = 'send_message_wh_res'

    def __init__(self, id, clientid, jdata):
        self.id = id
        self.clientid = clientid
        self.jdata = jdata

    id = Column(String(36), primary_key=True)
    clientid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    jdata = Column(JSON, nullable=False)

class Dte_sender(Base):
    __tablename__ = 'dte_sender'

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    lpass_email = Column(String(20), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())
    email_app_username = Column(String(100))
    email_app_password = Column(String(100))


# class Group_manager(Base):
#     __tablename__ = 'group_manager'

#     id = Column(String(36), nullable=False, primary_key=True)
#     fullname = Column(String(100), nullable=False)
#     email = Column(String(100))


class Client_manager(Base):
    __tablename__ = 'client_manager'

    id = Column(String(36), nullable=False, primary_key=True)
    name = Column(String(100), nullable=False)
    lpass_email = Column(String(20), nullable=False)
    email = Column(String(100))

class Client_daily_tasks_email(Base):
    __tablename__ = 'client_daily_tasks_email'

    id = Column(String(36), nullable=False, primary_key=True)
    name = Column(String(250), nullable=False)
    clientmanagerid = Column(String(36), nullable=False)
    subject = Column(String(1000), nullable= False)
    body = Column(Text, nullable= False)

class Email_server(Base):
    __tablename__ = 'email_server'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    smtp_address = Column(String(100), nullable=False)
    smtp_tls_port = Column(Integer, nullable=False)
    smtp_ssl_port = Column(Integer, nullable=False)
    imap_address = Column(String(100))
    imap_ssl_port = Column(Integer)

# class Dte_config(Base):
#     __tablename__ = 'dte_config'

#     id = Column(Integer, primary_key=True)
#     name = Column(Text, nullable=False)
#     janium_group_id = Column(String(36))
#     intro = Column(Text)
#     conclusion = Column(Text)
#     is_nc = Column(Boolean)
#     nc_text = Column(Text)
#     is_nm = Column(Boolean)
#     nm_text = Column(Text)
#     is_vm1 = Column(Boolean)
#     vm1_text = Column(Text)
#     is_vm2 = Column(Boolean)
#     vm2_text = Column(Text)
#     is_vm3 = Column(Boolean)
#     vm3_text = Column(Text)

# class Janium_group(Base):
#     __tablename__ = 'janium_group'

#     id = Column(String(36), primary_key=True)
#     name = Column(String(100), nullable=False)
#     group_manager_id = Column(String(36), nullable=False)
#     dte_sender_id = Column(String(36), nullable=False)

class Ulinc_cookie(Base):
    __tablename__ = 'ulinc_cookie'

    def __init__(self, clientid, usr, pwd, expires):
        self.clientid = clientid
        self.usr = usr
        self.pwd = pwd
        self.expires = expires

    id = Column(Integer, primary_key=True, autoincrement=True)
    dateadded = Column(DateTime, server_default=FetchedValue())
    clientid = Column(String(36), nullable=False)
    usr = Column(String(100), nullable=False)
    pwd = Column(Integer, nullable=False)
    expires = Column(DateTime, nullable=False)

class Client_daily_tasks_email_history(Base):
    __tablename__ = 'client_daily_tasks_email_history'

    def __init__(self, clientid):
        self.clientid = clientid

    id = Column(Integer, primary_key=True)
    clientid = Column(String(36), nullable=False)
    dateadded = Column(DateTime, server_default=FetchedValue())

class Ulinc_campaign(Base):
    __tablename__ = 'ulinc_campaign'

    def __init__(self, id, clientid, name, ulinc_isactive, ulinc_campaignid, ulinc_is_messenger, ulinc_messenger_origin_message):
        self.id = id
        self.clientid = clientid
        self.name = name
        self.ulinc_isactive = ulinc_isactive
        self.ulinc_campaignid = ulinc_campaignid
        self.ulinc_is_messenger = ulinc_is_messenger
        self.ulinc_messenger_origin_message = ulinc_messenger_origin_message

    id = Column(String(36), primary_key=True)
    dateadded = Column(DateTime, server_default=FetchedValue())
    clientid = Column(String(36), nullable=False)
    janium_campaignid = Column(String(36), nullable=True)
    name = Column(String(250), nullable=False)
    ulinc_isactive = Column(Boolean, nullable=False)
    ulinc_campaignid = Column(String(20), nullable=False)
    ulinc_is_messenger = Column(Boolean)
    ulinc_messenger_origin_message = Column(Text)

base_dict = dict({
        'campaign_id': 0,
        'id': None,
        'first_name': None,
        'last_name': None,
        'title': None,
        'company': None,
        'location': None,
        'email': None,
        'phone': None,
        'website': None,
        'profile': None
    })

def get_mysql_password():
    if os.getenv('IS_CLOUD') == 'True':
        creds, project = google.auth.default()
    else:
        creds = service_account.Credentials.from_service_account_file('/home/nicolas/gcp/key.json') 
    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    secret_name = "gcf-mysql-password"
    project_id = "janium0-0"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def get_mysql_host(is_master=True):
    if os.getenv('IS_CLOUD') == 'True':
        creds, project = google.auth.default()
        secret_name = "janium-mysql-master-private-ip"
    else:
        creds = service_account.Credentials.from_service_account_file('/home/nicolas/gcp/key.json')
        if is_master:
            secret_name = "janium-mysql-master-public-ip"
        else:
            secret_name = "janium-mysql-development-public-ip"

    client = secretmanager.SecretManagerServiceClient(credentials=creds)
    project_id = "janium0-0"
    request = {"name": f"projects/{project_id}/secrets/{secret_name}/versions/latest"}
    response = client.access_secret_version(request)
    return response.payload.data.decode('UTF-8')

def get_db_url(is_master=True):
    if os.getenv('IS_CLOUD') == 'True':
        host = get_mysql_host()
        port = os.getenv('DB_PORT')
        driver_name = os.getenv('DRIVER_NAME')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = get_mysql_password()
        return engine.url.URL(
            drivername=driver_name,
            username=db_user,
            password=db_password,
            database=db_name,
            host=host,
            port=int(port)
        )

    from dotenv import load_dotenv
    load_dotenv()
    host = get_mysql_host(is_master)
    driver_name = os.getenv('DRIVER_NAME')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = get_mysql_password()
    return engine.url.URL(
        drivername=driver_name,
        username=db_user,
        password=db_password,
        database=db_name,
        host=host
    )
# Hey
