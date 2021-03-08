"""add new action type (continue_campaign)

Revision ID: e1f69b3eed30
Revises: 8a46e3cf013c
Create Date: 2021-03-05 14:18:08.097588

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, null
from sqlalchemy import Integer, String

# revision identifiers, used by Alembic.
revision = 'e1f69b3eed30'
down_revision = '8a46e3cf013c'
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
            {'action_type_id': 20, 'action_type': 'continue_campaign', 'action_type_description': "The contact's campaign is resumed"}
        ]
    )


def downgrade():
    pass
