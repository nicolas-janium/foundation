"""add connect error action type

Revision ID: 7410dc15c4d6
Revises: a916fca926cf
Create Date: 2021-03-16 12:09:41.589314

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
revision = '7410dc15c4d6'
down_revision = 'a916fca926cf'
branch_labels = None
depends_on = None

action_type = table('action_type',
    column('action_type_id', Integer),
    column('action_type_name', String),
    column('action_type_description', String)
)

def upgrade():
    op.bulk_insert(action_type,
        [
            {'action_type_id': 18, 'action_type_name': 'ulinc_in_queue', 'action_type_description': 'The contact is in ulincs queue. Pre connection request. Ulinc side'},
            {'action_type_id': 19, 'action_type_name': 'ulinc_connection_requested', 'action_type_description': 'The contact has been sent a connection request. Ulinc side'},
            {'action_type_id': 20, 'action_type_name': 'ulinc_connection_error', 'action_type_description': 'The contact''s connection request had an error. Ulinc side'}
        ]
    )


def downgrade():
    pass
