"""add unassigned, janium, and type records

Revision ID: 591315dc14f4
Revises: 484dfe1add1c
Create Date: 2021-02-22 14:18:58.661972

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean, Text, Integer
from sqlalchemy.types import JSON
# from db import model, model_types
from db import model
import os
import json


# revision identifiers, used by Alembic.
revision = '591315dc14f4'
down_revision = '484dfe1add1c'
branch_labels = None
depends_on = None

credentials = table('credentials',
    column('credentials_id', String),
    column('username', String),
    column('password', String)
)
cookie = table('cookie',
    column('cookie_id', String),
    column('cookie_type_id', Integer),
    column('cookie_json_value', JSON)
)
ulinc_config = table('ulinc_config',
    column('ulinc_config_id', String),
    column('credentials_id', String),
    column('cookie_id', String),
    column('client_ulinc_id', String),
    column('new_connection_webhook', String),
    column('new_message_webhook', String),
    column('send_message_webhook', String)
)
email_config = table('email_config',
    column('email_config_id', String),
    column('credentials_id', String),
    column('email_server_id', String),
    column('is_sendgrid', Boolean),
    column('sendgrid_sender_id', String)
)
dte = table('dte',
    column('dte_id', String),
    column('name', String),
    column('description', String),
    column('subject', String),
    column('body', Text)
)
dte_sender = table('dte_sender',
    column('dte_sender_id', String),
    column('email_config_id', String),
    column('first_name', String),
    column('last_name', String)
)
client_group_manager = table('client_group_manager',
    column('client_group_manager_id', String),
    column('first_name', String),
    column('last_name', String)
)
client_group = table('client_group',
    column('client_group_id', String),
    column('client_group_manager_id', String),
    column('dte_id', String),
    column('dte_sender_id', String),
    column('name', String),
    column('description', String),
    column('is_active', Boolean)
)
client = table('client',
    column('client_id', String),
    column('client_group_id', String),
    column('ulinc_config_id', String),
    column('email_config_id', String),

    column('is_active', Boolean),
    column('is_sending_emails', Boolean),
    column('is_sending_li_messages', Boolean),
    column('is_dte', Boolean),
    column('is_assistant', Boolean),
    column('is_email_forward', Boolean),

    column('first_name', String),
    column('last_name', String),
    column('primary_email', String)
)
janium_campaign = table('janium_campaign',
    column('janium_campaign_id', String),
    column('client_id', String),
    column('email_config_id', String),
    column('janium_campaign_name', String),
    column('janium_campaign_description', String),
    column('is_active', Boolean),
    column('is_messenger', Boolean)
)
ulinc_campaign = table('ulinc_campaign',
    column('ulinc_campaign_id', String),
    column('janium_campaign_id', String),
    column('client_id', String),
    column('ulinc_campaign_name', String),
    column('ulinc_ulinc_campaign_id', String),
    column('ulinc_is_active', Boolean),
    column('ulinc_is_messenger', Boolean)
)
janium_campaign_step_type = table('janium_campaign_step_type',
    column('janium_campaign_step_type_id', Integer),
    column('janium_campaign_step_type', String),
    column('janium_campaign_step_type_description', String)
)
action_type = table('action_type',
    column('action_type_id', Integer),
    column('action_type', String),
    column('action_type_description', String)
)
webhook_response_type = table('webhook_response_type',
    column('webhook_response_type_id', Integer),
    column('webhook_response_type', String),
    column('webhook_response_type_description', String)
)
cookie_type = table('cookie_type',
    column('cookie_type_id', Integer),
    column('cookie_type', String),
    column('cookie_type_description', String)
)
email_server = table('email_server',
    column('email_server_id', String),
    column('email_server_name', String),
    column('smtp_address', String),
    column('smtp_ssl_port', Integer),
    column('smtp_tls_port', Integer),
    column('imap_address', String),
    column('imap_ssl_port', Integer)
)


def upgrade():
    ### Insert Janium Record Types ###
    op.bulk_insert(action_type,
        [
            {'action_type_id': 1, 'action_type': 'li_new_connection', 'action_type_description': 'The contact connection request accepted. Originates in Ulinc'},
            {'action_type_id': 2, 'action_type': 'li_new_message', 'action_type_description': 'The client received a new li message from this contact. Originates in Ulin'},
            {'action_type_id': 3, 'action_type': 'li_send_message', 'action_type_description': 'The client sent a li message to this contact. Originates in Janium through Ulinc'},
            {'action_type_id': 4, 'action_type': 'send_email', 'action_type_description': 'The client sent an email to this contact. Originates in Janium'},
            {'action_type_id': 5, 'action_type': 'contact_email_open', 'action_type_description': 'The contact opened a previously sent email'},
            {'action_type_id': 6, 'action_type': 'new_email', 'action_type_description': 'The contact sent an email to the client'},
            {'action_type_id': 7, 'action_type': 'email_blacklist', 'action_type_description': 'The contact unsubscribed from a sent email from the client'},
            {'action_type_id': 8, 'action_type': 'dte_profile_visit_nc', 'action_type_description': 'The client visited the LI profile of this contact. Originates in DTE New Connection section'},
            {'action_type_id': 9, 'action_type': 'dte_profile_visit_nm', 'action_type_description': 'The client visited the LI profile of this contact. Originates in DTE New Message section'},
            {'action_type_id': 10, 'action_type': 'dte_profile_visit_vm', 'action_type_description': 'The client visited the LI profile of this contact. Originates in DTE Voicemail section'},
            {'action_type_id': 11, 'action_type': 'marked_to_no_interest', 'action_type_description': 'The client disqualified this contact. Originates in DTE'},
            {'action_type_id': 12, 'action_type': 'arbitrary_response', 'action_type_description': 'The contact responded with an arbitrary response and further campaign steps should continue'},
            {'action_type_id': 13, 'action_type': 'ulinc_origin_messenger_message', 'action_type_description': 'This is the origin message for Ulinc Messenger Campaigns'},
            {'action_type_id': 14, 'action_type': 'li_new_connection_backdated', 'action_type_description': 'The contact connection request accepted if contact is backdated into a janium campaign'},
            {'action_type_id': 15, 'action_type': 'email_bounce', 'action_type_description': 'The contact was sent an email that bounced. Originates from Sendgrid'},
            {'action_type_id': 16, 'action_type': 'tib_new_vendor', 'action_type_description': 'When a new vendor registers on TIB'},
            {'action_type_id': 17, 'action_type': 'tib_new_vendor_retire', 'action_type_description': 'When a new vendor submits a meeting request'}
        ]
    )
    op.bulk_insert(janium_campaign_step_type,
        [
            {'janium_campaign_step_type_id': 1, 'janium_campaign_step_type': 'li_message', 'janium_campaign_step_type_description': 'LinkedIn Message'},
            {'janium_campaign_step_type_id': 2, 'janium_campaign_step_type': 'email', 'janium_campaign_step_type_description': 'Email'},
            {'janium_campaign_step_type_id': 3, 'janium_campaign_step_type': 'text_message', 'janium_campaign_step_type_description': 'Text Message'}
        ]
    )
    op.bulk_insert(webhook_response_type,
        [
            {'webhook_response_type_id': 1, 'webhook_response_type': 'ulinc_new_connection', 'webhook_response_type_description': 'New connection webhook from ulinc'},
            {'webhook_response_type_id': 2, 'webhook_response_type': 'ulinc_new_message', 'webhook_response_type_description': 'New Message webhook from ulinc'},
            {'webhook_response_type_id': 3, 'webhook_response_type': 'ulinc_send_message', 'webhook_response_type_description': 'Send Message webhook from ulinc'}
        ]
    )
    op.bulk_insert(cookie_type,
        [
            {'cookie_type_id': 1, 'cookie_type': 'Ulinc Cookie', 'cookie_type_description': 'Cookie for Ulinc accounts'}
        ]
    )
    op.bulk_insert(email_server,
        [
            {'email_server_id': 'f9cf23f6-231c-4210-90f3-7749873909ad', 'email_server_name': 'gmail', 'smtp_address': 'smtp.gmail.com', 'smtp_ssl_port': 465, 'smtp_tls_port': 587, 'imap_address': 'imap.gmail.com', 'imap_ssl_port': 993},
            {'email_server_id': '9e29868d-65dc-4d12-9bfb-9ee38f639773', 'email_server_name': 'office_365', 'smtp_address': 'smtp.office365.com', 'smtp_ssl_port': 465, 'smtp_tls_port': 587, 'imap_address': 'outlook.office365.com', 'imap_ssl_port': 993},
            {'email_server_id': '5fbb236e-16e6-4a98-94fe-ff11f2b222b3', 'email_server_name': 'yahoo_small_business', 'smtp_address': 'smtp.bizmail.yahoo.com', 'smtp_ssl_port': 465, 'smtp_tls_port': 587, 'imap_address': 'imap.mail.yahoo.com', 'imap_ssl_port': 993}
        ]
    )

    # ### Add Unassigned Records ###
    op.execute(
        credentials.insert().values(
            credentials_id=model.Credentials.unassigned_credentials_id,
            username='username',
            password='password'
        )
    )
    op.execute(
        cookie.insert().values(
            cookie_id=model.Cookie.unassigned_cookie_id,
            cookie_type_id=1,
            # cookie_json_value=json.dumps({'usr': '123', 'pwd': '123'})
            cookie_json_value = {"usr": "123", "pwd": "123"}
        )
    )
    op.execute(
        ulinc_config.insert().values(
            ulinc_config_id=model.Ulinc_config.unassigned_ulinc_config_id,
            credentials_id=model.Credentials.unassigned_credentials_id,
            cookie_id=model.Cookie.unassigned_cookie_id,
            client_ulinc_id='999',
            new_connection_webhook='123',
            new_message_webhook='123',
            send_message_webhook='123'
        )
    )
    op.execute(
        email_config.insert().values(
            email_config_id=model.Email_config.unassigned_email_config_id,
            credentials_id=model.Credentials.unassigned_credentials_id,
            email_server_id='f9cf23f6-231c-4210-90f3-7749873909ad',
            is_sendgrid=False,
            sendgrid_sender_id=None
        )
    )
    op.execute(
        dte.insert().values(
            dte_id=model.Dte.unassigned_dte_id,
            name='Unassigned Dte Name',
            description='Unassigned Dte description',
            subject='Unassigned Dte Subject',
            body='Unassigned Dte Body'
        )
    )
    op.execute(
        dte_sender.insert().values(
            dte_sender_id=model.Dte_sender.unassigned_dte_sender_id,
            email_config_id=model.Email_config.unassigned_email_config_id,
            first_name='Unassigned',
            last_name='Dte Sender'
        )
    )
    op.execute(
        client_group_manager.insert().values(
            client_group_manager_id= model.Client_group_manager.unassigned_client_group_manager_id,
            first_name='Unassigned',
            last_name='Client Group Manager'
        )
    )
    op.execute(
        client_group.insert().values(
            client_group_id=model.Client_group.unassigned_client_group_id,
            client_group_manager_id= model.Client_group_manager.unassigned_client_group_manager_id,
            dte_id=model.Dte.unassigned_dte_id,
            dte_sender_id=model.Dte_sender.unassigned_dte_sender_id,
            name='Unassigned Client Group Name',
            description='Unassigned Client Group Description',
            is_active=False
        )
    )
    op.execute(
        client.insert().values(
            client_id=model.Client.unassigned_client_id,
            client_group_id=model.Client_group.unassigned_client_group_id,
            ulinc_config_id=model.Ulinc_config.unassigned_ulinc_config_id,
            email_config_id=model.Email_config.unassigned_email_config_id,

            is_active=False,
            is_sending_emails=False,
            is_sending_li_messages=False,
            is_dte=False,
            is_assistant=False,
            is_email_forward=False,

            first_name='Unassigned',
            last_name='Client',
            primary_email='unassigned@unassigned.com'
        )
    )
    op.execute(
        janium_campaign.insert().values(
            janium_campaign_id=model.Janium_campaign.unassigned_janium_campaign_id,
            client_id=model.Client.unassigned_client_id,
            email_config_id=model.Email_config.unassigned_email_config_id,
            janium_campaign_name='Unassigned Janium Campaign',
            janium_campaign_description='Unassigned Janium Campaign Description',
            is_active=False,
            is_messenger=False
        )
    )
    op.execute(
        ulinc_campaign.insert().values(
            ulinc_campaign_id=model.Ulinc_campaign.unassigned_ulinc_campaign_id,
            janium_campaign_id=model.Janium_campaign.unassigned_janium_campaign_id,
            client_id=model.Client.unassigned_client_id,
            ulinc_campaign_name='Unassigned Janium Campaign',
            ulinc_ulinc_campaign_id='999',
            ulinc_is_active=False,
            ulinc_is_messenger=False
        )
    )


def downgrade():
    pass