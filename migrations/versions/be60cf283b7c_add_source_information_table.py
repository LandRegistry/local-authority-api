from alembic import op
import sqlalchemy as sa
from flask import current_app

"""Add source information table

Revision ID: be60cf283b7c
Revises: f4560bd06da5
Create Date: 2018-04-11 13:37:37.790001

"""

# revision identifiers, used by Alembic.
revision = 'be60cf283b7c'
down_revision = 'f4560bd06da5'


def upgrade():
    op.create_table('source_information',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('source_information', sa.String(), nullable=False),
                    sa.Column('organisation_id', sa.Integer(), sa.ForeignKey('organisation.id'), nullable=False))
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON source_information TO " +
               current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT SELECT, USAGE ON source_information_id_seq TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_table('source_information')
