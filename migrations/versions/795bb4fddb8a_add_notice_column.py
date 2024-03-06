"""Create notice period column

Revision ID: 795bb4fddb8a
Revises: 9e25640a3592
Create Date: 2018-06-07 12:25:33.841459

"""

# revision identifiers, used by Alembic.
revision = '795bb4fddb8a'
down_revision = '9e25640a3592'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('organisation',
                  sa.Column('notice', sa.Boolean(), server_default=sa.false())
                  )


def downgrade():
    op.drop_column('organisation', 'notice')
