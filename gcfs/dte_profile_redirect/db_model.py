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
        host= os.getenv('DB_HOST')
    )


engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)


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
