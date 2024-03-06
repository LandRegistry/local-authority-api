"""Add Organisation table

Revision ID: dd2e44336bda
Revises: None
Create Date: 2017-07-06 10:47:03.387160

"""

# revision identifiers, used by Alembic.
revision = 'dd2e44336bda'
down_revision = None

from alembic import op
import sqlalchemy as sa
from flask import current_app


def upgrade():
    op.create_table('organisation',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('title', sa.String(), nullable=False, unique=True))
    op.execute("GRANT SELECT, INSERT ON organisation TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT SELECT, USAGE ON organisation_id_seq TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_table('organisation')
