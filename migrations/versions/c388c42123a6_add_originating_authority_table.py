"""Add originating authority table

Revision ID: c388c42123a6
Revises: 594f2398aa87
Create Date: 2017-11-29 12:28:38.084541

"""

# revision identifiers, used by Alembic.
revision = 'c388c42123a6'
down_revision = '594f2398aa87'

from alembic import op
import sqlalchemy as sa
from flask import current_app


def upgrade():
    op.create_table('originating_authorities',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=False),
                        sa.Column('name', sa.String(), nullable=False, unique=True))
    op.execute("GRANT SELECT, INSERT ON originating_authorities TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_table('originating_authorities')
