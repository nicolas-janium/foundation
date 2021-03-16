"""add model unassigned records

Revision ID: a916fca926cf
Revises: b52f593e4e84
Create Date: 2021-03-15 09:57:57.273316

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Boolean, Integer, String, Text, DateTime
from sqlalchemy.sql import column, null, table, text
from sqlalchemy.types import JSON
from db import model
import uuid


# revision identifiers, used by Alembic.
revision = 'a916fca926cf'
down_revision = 'b52f593e4e84'
branch_labels = None
depends_on = None

credentials = table('credentials',
    column('credentials_id', String),
    column('username', String),
    column('password', String),
    column('updated_by', String)
)
cookie = table('cookie',
    column('cookie_id', String),
    column('cookie_type_id', Integer),
    column('cookie_json_value', String),
    column('updated_by', String)
)
ulinc_config = table('ulinc_config',
    column('ulinc_config_id', String),
    column('credentials_id', String),
    column('cookie_id', String),
    column('ulinc_client_id', String),
    column('new_connection_webhook', String),
    column('new_message_webhook', String),
    column('send_message_webhook', String),
    column('updated_by', String)
)
email_config = table('email_config',
    column('email_config_id', String),
    column('credentials_id', String),
    column('email_server_id', String),
    column('is_sendgrid', Boolean),
    column('sendgrid_sender_id', String),
    column('updated_by', String)
)
dte = table('dte',
    column('dte_id', String),
    column('dte_name', String),
    column('dte_description', String),
    column('dte_subject', String),
    column('dte_body', Text),
    column('updated_by', String)
)
dte_sender = table('dte_sender',
    column('dte_sender_id', String),
    column('user_id', String),
    column('email_config_id', String)
)
account_group = table('account_group',
    column('account_group_id', String),
    column('account_group_manager_id', String),
    column('dte_id', String),
    column('dte_sender_id', String),
    column('account_group_name', String),
    column('account_group_description', String),
    column('updated_by', String)
)
janium_campaign = table('janium_campaign',
    column('janium_campaign_id', String),
    column('account_id', String),
    column('email_config_id', String),
    column('janium_campaign_name', String),
    column('janium_campaign_description', String),
    column('is_messenger', Boolean),
    column('queue_start_time', DateTime),
    column('queue_end_time', DateTime),
    column('updated_by', String)
)
ulinc_campaign = table('ulinc_campaign',
    column('ulinc_campaign_id', String),
    column('account_id', String),
    column('janium_campaign_id', String),
    column('ulinc_campaign_name', String),
    column('ulinc_ulinc_campaign_id', String),
    column('ulinc_is_active', Boolean),
    column('ulinc_is_messenger', Boolean),
    column('updated_by', String)
)
contact_source = table('contact_source',
    column('contact_source_id', String),
    column('account_id', String),
    column('contact_source_type_id', Integer),
    column('contact_source_json', JSON)
)
time_zone = table('time_zone',
    column('time_zone_id', String),
    column('time_zone_name', String),
    column('time_zone_code', String)
)
account = table('account',
    column('account_id', String),
    column('account_type_id', Integer),
    column('account_group_id', String),
    column('ulinc_config_id', String),
    column('email_config_id', String),
    column('time_zone_id', String),
    column('is_sending_emails', Boolean),
    column('is_sending_li_messages', Boolean),
    column('is_receiving_dte', Boolean),
    column('updated_by', String)
)



def upgrade():
    op.execute(
        credentials.insert().values(
            credentials_id=model.Credentials.unassigned_credentials_id,
            username='username',
            password='password',
            updated_by=model.User.system_user_id
        )
    )
    op.execute(
        cookie.insert().values(
            cookie_id=model.Cookie.unassigned_cookie_id,
            cookie_type_id=1,
            # cookie_json_value=json.dumps({'usr': '123', 'pwd': '123'})
            cookie_json_value = '{"usr": "123", "pwd": "123"}',
            updated_by=model.User.system_user_id
        )
    )
    op.execute(
        ulinc_config.insert().values(
            ulinc_config_id=model.Ulinc_config.unassigned_ulinc_config_id,
            credentials_id=model.Credentials.unassigned_credentials_id,
            cookie_id=model.Cookie.unassigned_cookie_id,
            ulinc_client_id='999',
            new_connection_webhook='123',
            new_message_webhook='123',
            send_message_webhook='123',
            updated_by=model.User.system_user_id
        )
    )
    op.execute(
        email_config.insert().values(
            email_config_id=model.Email_config.unassigned_email_config_id,
            credentials_id=model.Credentials.unassigned_credentials_id,
            email_server_id=model.Email_server.gmail_id,
            is_sendgrid=False,
            sendgrid_sender_id=null(),
            updated_by=model.User.system_user_id
        )
    )
    op.execute(
        dte.insert().values(
            dte_id=model.Dte.unassigned_dte_id,
            dte_name='Unassigned Dte Name',
            dte_description='Unassigned Dte description',
            dte_subject='Unassigned Dte Subject',
            dte_body='Unassigned Dte Body',
            updated_by=model.User.system_user_id
        )
    )
    op.execute(
        dte_sender.insert().values(
            dte_sender_id=model.Dte_sender.unassigned_dte_sender_id,
            user_id=model.User.system_user_id,
            email_config_id=model.Email_config.unassigned_email_config_id
        )
    )
    op.execute(
        account_group.insert().values(
            account_group_id=model.Account_group.unassigned_account_group_id,
            account_group_manager_id=model.User.system_user_id,
            dte_id=model.Dte.unassigned_dte_id,
            dte_sender_id=model.Dte_sender.unassigned_dte_sender_id,
            account_group_name='Unassigned Account Group Name',
            account_group_description='Unassigned Account Group Description',
            updated_by=model.User.system_user_id 
        )
    )
    mt_time_zone_id = str(uuid.uuid4())
    op.bulk_insert(time_zone,
        [
            {'time_zone_id': mt_time_zone_id, 'time_zone_name': 'Mountain Time', 'time_zone_code': 'US/Mountain'},
            {'time_zone_id': str(uuid.uuid4()), 'time_zone_name': 'Eastern Time', 'time_zone_code': 'US/Eastern'},
            {'time_zone_id': str(uuid.uuid4()), 'time_zone_name': 'Central Time', 'time_zone_code': 'US/Central'},
            {'time_zone_id': str(uuid.uuid4()), 'time_zone_name': 'Pacific Time', 'time_zone_code': 'US/Pacific'}
        ]
    )
    op.execute(
        account.insert().values(
            account_id=model.Account.unassigned_account_id,
            account_type_id=1,
            account_group_id=model.Account_group.unassigned_account_group_id,
            ulinc_config_id=model.Ulinc_config.unassigned_ulinc_config_id,
            email_config_id=model.Email_config.unassigned_email_config_id,
            time_zone_id=mt_time_zone_id,
            is_sending_emails=False,
            is_sending_li_messages=False,
            is_receiving_dte=False,
            updated_by=model.User.system_user_id 
        )
    )
    op.execute(
        janium_campaign.insert().values(
            janium_campaign_id=model.Janium_campaign.unassigned_janium_campaign_id,
            account_id=model.Account.unassigned_account_id,
            email_config_id=model.Email_config.unassigned_email_config_id,
            janium_campaign_name='Unassigned Janium Campaign',
            janium_campaign_description='Unassigned Janium Campaign Description',
            is_messenger=False,
            queue_start_time=text("'9999-12-31 09:00:00'"),
            queue_end_time=text("'9999-12-31 12:00:00'"),
            updated_by=model.User.system_user_id
        )
    )
    op.execute(
        ulinc_campaign.insert().values(
            ulinc_campaign_id=model.Ulinc_campaign.unassigned_ulinc_campaign_id,
            janium_campaign_id=model.Janium_campaign.unassigned_janium_campaign_id,
            account_id=model.Account.unassigned_account_id,
            ulinc_campaign_name='Unassigned Janium Campaign',
            ulinc_ulinc_campaign_id='999',
            ulinc_is_active=False,
            ulinc_is_messenger=False,
            updated_by=model.User.system_user_id
        )
    )


def downgrade():
    pass
