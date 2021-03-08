"""add two new action types (In Queue, Conn Req)

Revision ID: 1fa114ff98a9
Revises: b6f613d8be61
Create Date: 2021-03-05 09:00:03.006576

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, null
from sqlalchemy import Integer, String


# revision identifiers, used by Alembic.
revision = '1fa114ff98a9'
down_revision = 'b6f613d8be61'
branch_labels = None
depends_on = None

action_type = table('action_type',
    column('action_type_id', Integer),
    column('action_type', String),
    column('action_type_description', String)
)

def upgrade():
    ### Insert Janium Record Types ###
    op.bulk_insert(action_type,
        [
            {'action_type_id': 18, 'action_type': 'ulinc_in_queue', 'action_type_description': 'The contact is in queue in Ulinc'},
            {'action_type_id': 19, 'action_type': 'ulinc_conn_req', 'action_type_description': 'The client has received a connection request'}
        ]
    )


def downgrade():
    pass
