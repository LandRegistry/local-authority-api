"""Add migrated column to organisation table

Revision ID: 048174d0ba59
Revises: c388c42123a6
Create Date: 2018-01-09 12:55:55.180234

"""

# revision identifiers, used by Alembic.
revision = '048174d0ba59'
down_revision = 'c388c42123a6'

from alembic import op
import sqlalchemy as sa
from flask import current_app


def upgrade():
    op.add_column('organisation',
        sa.Column('migrated', sa.Boolean(), server_default=sa.false())
    )
    op.execute("GRANT UPDATE ON organisation TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_column('organisation', 'migrated')
    op.execute("REVOKE UPDATE ON organisation FROM " + current_app.config.get("APP_SQL_USERNAME"))
