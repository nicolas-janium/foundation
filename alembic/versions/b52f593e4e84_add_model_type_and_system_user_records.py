"""add model type, unassigned, and system user records

Revision ID: 4385fb17935a
Revises: e372494c0c3f
Create Date: 2021-03-11 09:33:12.120208

"""
import json
import os
import uuid

import sqlalchemy as sa
from alembic import op
from db import model
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.sql import column, null, table
from sqlalchemy.types import JSON

# revision identifiers, used by Alembic.
revision = 'b52f593e4e84'
down_revision = '83dd985ca947'
branch_labels = None
depends_on = None

user = table('user',
    column('user_id', String),
    column('first_name', String),
    column('last_name', String),
    column('primary_email', String),
    column('updated_by', String)
)
user_permission_map = table('user_permission_map',
    column('user_id', String),
    column('permission_id', String),
    column('updated_by', String)
)
account_type = table('account_type',
    column('account_type_id', Integer),
    column('account_type_name', String),
    column('account_type_description', String)
)
user_account_map = table('user_account_map',
    column('user_id', String),
    column('account_id', String),
    column('updated_by', String)
)
user_proxy_map = table('user_proxy_map',
    column('user_id', String),
    column('account_id', String),
    column('updated_by', String)
)
contact_source_type = table('contact_source_type',
    column('contact_source_type_id', Integer),
    column('contact_source_type_name', String),
    column('contact_source_type_description', String)
)
janium_campaign_step_type = table('janium_campaign_step_type',
    column('janium_campaign_step_type_id', Integer),
    column('janium_campaign_step_type_name', String),
    column('janium_campaign_step_type_description', String)
)
action_type = table('action_type',
    column('action_type_id', Integer),
    column('action_type_name', String),
    column('action_type_description', String)
)
cookie_type = table('cookie_type',
    column('cookie_type_id', Integer),
    column('cookie_type_name', String),
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
    system_user_id = model.User.system_user_id
    op.bulk_insert(user,
        [
            {'user_id': system_user_id, 'first_name': 'Janium System', 'last_name': 'Master User', 'primary_email': 'jason@janium.io', 'updated_by': system_user_id},
            {'user_id': model.User.unassigned_user_id, 'first_name': 'Unassigned', 'last_name': 'User', 'primary_email': 'unassigned321@gmail.com', 'updated_by': system_user_id}
        ]
    )
    op.bulk_insert(account_type,
        [
            {'account_type_id': 1, 'account_type_name': 'janium_foundation', 'account_type_description': 'Janium Foundation'},
            {'account_type_id': 2, 'account_type_name': 'janium_action', 'account_type_description': 'Janium Action'},
            {'account_type_id': 3, 'account_type_name': 'janium_management', 'account_type_description': 'Janium Management'}
        ]
    )
    op.bulk_insert(contact_source_type,
        [
            {'contact_source_type_id': 1, 'contact_source_type_name': 'ulinc_webhook_nc', 'contact_source_type_description': 'Webhook Data from Ulinc New Connection Webhook'},
            {'contact_source_type_id': 2, 'contact_source_type_name': 'ulinc_webhook_nm', 'contact_source_type_description': 'Webhook Data from Ulinc New Message Webhook'},
            {'contact_source_type_id': 3, 'contact_source_type_name': 'ulinc_webhook_sm', 'contact_source_type_description': 'Webhook Data from Ulinc Send Message Webhook'},
            {'contact_source_type_id': 4, 'contact_source_type_name': 'ulinc_csv_export', 'contact_source_type_description': 'CSV export from Ulinc'}
        ]
    )
    op.bulk_insert(janium_campaign_step_type,
        [
            {'janium_campaign_step_type_id': 1, 'janium_campaign_step_type_name': 'li_message', 'janium_campaign_step_type_description': 'LinkedIn Message'},
            {'janium_campaign_step_type_id': 2, 'janium_campaign_step_type_name': 'email', 'janium_campaign_step_type_description': 'Email'},
            {'janium_campaign_step_type_id': 3, 'janium_campaign_step_type_name': 'text_message', 'janium_campaign_step_type_description': 'Text Message'}
        ]
    )
    op.bulk_insert(action_type,
        [
            {'action_type_id': 1, 'action_type_name': 'li_new_connection', 'action_type_description': 'The contact connection request accepted. Originates in Ulinc'},
            {'action_type_id': 2, 'action_type_name': 'li_new_message', 'action_type_description': 'The client received a new li message from this contact. Originates in Ulin'},
            {'action_type_id': 3, 'action_type_name': 'li_send_message', 'action_type_description': 'The client sent a li message to this contact. Originates in Janium through Ulinc'},
            {'action_type_id': 4, 'action_type_name': 'send_email', 'action_type_description': 'The client sent an email to this contact. Originates in Janium'},
            {'action_type_id': 5, 'action_type_name': 'contact_email_open', 'action_type_description': 'The contact opened a previously sent email'},
            {'action_type_id': 6, 'action_type_name': 'new_email', 'action_type_description': 'The contact sent an email to the client'},
            {'action_type_id': 7, 'action_type_name': 'email_blacklist', 'action_type_description': 'The contact unsubscribed from a sent email from the client'},
            {'action_type_id': 8, 'action_type_name': 'dte_profile_visit_nc', 'action_type_description': 'The client visited the LI profile of this contact. Originates in DTE New Connection section'},
            {'action_type_id': 9, 'action_type_name': 'dte_profile_visit_nm', 'action_type_description': 'The client visited the LI profile of this contact. Originates in DTE New Message section'},
            {'action_type_id': 10, 'action_type_name': 'dte_profile_visit_vm', 'action_type_description': 'The client visited the LI profile of this contact. Originates in DTE Voicemail section'},
            {'action_type_id': 11, 'action_type_name': 'marked_no_interest', 'action_type_description': 'The client disqualified this contact. Originates in DTE'},
            {'action_type_id': 12, 'action_type_name': 'arbitrary_response', 'action_type_description': 'The contact responded with an arbitrary response and further campaign steps should continue'},
            {'action_type_id': 13, 'action_type_name': 'ulinc_messenger_origin_message', 'action_type_description': 'This is the origin message for Ulinc Messenger Campaigns'},
            {'action_type_id': 14, 'action_type_name': 'continue_campaign', 'action_type_description': 'The contact connection request accepted if contact is backdated into a janium campaign'},
            {'action_type_id': 15, 'action_type_name': 'email_bounce', 'action_type_description': 'The contact was sent an email that bounced. Originates from Sendgrid'},
            {'action_type_id': 16, 'action_type_name': 'tib_new_vendor', 'action_type_description': 'When a new vendor registers on TIB'},
            {'action_type_id': 17, 'action_type_name': 'tib_new_vendor_retire', 'action_type_description': 'When a new vendor submits a meeting request'}
        ]
    )
    op.bulk_insert(cookie_type,
        [
            {'cookie_type_id': 1, 'cookie_type_name': 'Ulinc Cookie', 'cookie_type_description': 'Cookie for Ulinc accounts'}
        ]
    )
    op.bulk_insert(email_server,
        [
            {'email_server_id': model.Email_server.gmail_id, 'email_server_name': 'gmail', 'smtp_address': 'smtp.gmail.com', 'smtp_ssl_port': 465, 'smtp_tls_port': 587, 'imap_address': 'imap.gmail.com', 'imap_ssl_port': 993},
            {'email_server_id': str(uuid.uuid4()), 'email_server_name': 'office_365', 'smtp_address': 'smtp.office365.com', 'smtp_ssl_port': 465, 'smtp_tls_port': 587, 'imap_address': 'outlook.office365.com', 'imap_ssl_port': 993},
            {'email_server_id': str(uuid.uuid4()), 'email_server_name': 'yahoo_small_business', 'smtp_address': 'smtp.bizmail.yahoo.com', 'smtp_ssl_port': 465, 'smtp_tls_port': 587, 'imap_address': 'imap.mail.yahoo.com', 'imap_ssl_port': 993}
        ]
    )


def downgrade():
    pass
