"""Add authority update column

Revision ID: 77feac0e71db
Revises: 55f7586bf5a4
Create Date: 2023-06-15 10:22:55.173372

"""

# revision identifiers, used by Alembic.
revision = '77feac0e71db'
down_revision = '55f7586bf5a4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('organisation', sa.Column('last_updated', sa.DateTime(), nullable=True))
    op.alter_column('organisation', 'last_updated', nullable=True, server_default=sa.func.current_timestamp())


def downgrade():
    op.drop_column('organisation', 'last_updated')
