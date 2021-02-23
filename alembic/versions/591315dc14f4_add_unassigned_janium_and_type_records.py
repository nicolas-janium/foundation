"""add unassigned, janium, and type records

Revision ID: 591315dc14f4
Revises: 484dfe1add1c
Create Date: 2021-02-22 14:18:58.661972

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, JSON, Boolean, Text
# from db import model, model_types
from db import model
import os


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
    column('cookie_type_id', String),
    column('cookie_json_value', JSON)
)
ulinc_config = table('ulinc_config',
    column('ulinc_config_id', String),
    column('credentials_id', String),
    column('cookie_id', String),
    column('client_ulinc_id', String),
    column('new_connection_webhook', String)
    column('new_message_webhook', String)
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
    column('name', String),
    column('name', String),
    column('name', String),
)

def upgrade():
    op.execute(
        credentials.insert().values(
            credentials_id=model.Credentials.janium_email_app_credentials_id,
            username=os.getenv('NIC_EMAIL_APP_USERNAME'),
            password=os.getenv('NIC_EMAIL_APP_PASSWORD')
        )
    )
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
            cookie_json_value={'usr': '123', 'pwd': '123'}
        )
    )



def downgrade():
    op.execute(
        credentials.delete().where(credentials.c.credentials_id == 'b5a13613-3a78-4a9d-a34c-79391fc52d23')
    )


upgrade()