"""Add organisation mapping table

Revision ID: 6a327410efb3
Revises: 048174d0ba59
Create Date: 2018-01-10 12:00:37.217823

"""

# revision identifiers, used by Alembic.
revision = '6a327410efb3'
down_revision = '048174d0ba59'

from alembic import op
import sqlalchemy as sa
from flask import current_app


def upgrade():
    op.create_table('organisation_name_mapping',
                    sa.Column('organisation_name', sa.String(), primary_key=True),
                    sa.Column('boundaries_name', sa.String(), unique=True))
    op.execute("GRANT SELECT, INSERT ON organisation_name_mapping TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_table('organisation_name_mapping')
