"""add kendo_data_enrichment action type

Revision ID: 7bd11d7dc238
Revises: 4fd45561bf99
Create Date: 2021-03-23 08:02:43.283896

"""
import json
import os
import uuid

import sqlalchemy as sa
from alembic import op
from db import model
from sqlalchemy import (JSON, Boolean, Column, Computed, DateTime, ForeignKey,
                        Integer, PrimaryKeyConstraint, String, Table, Text,
                        create_engine, engine)
from sqlalchemy.sql import false, func, text, true, table, column, null


# revision identifiers, used by Alembic.
revision = '7bd11d7dc238'
down_revision = '4fd45561bf99'
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
            {'action_type_id': 22, 'action_type_name': 'kendo_data_enrichment', 'action_type_description': 'Data enrichment from Kendo Email'}
        ]
    )


def downgrade():
    pass
