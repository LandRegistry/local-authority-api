"""Add maintenance column

Revision ID: 4ba7da4fe369
Revises: 8b170388b1b0
Create Date: 2020-05-06 12:38:18.642856

"""

# revision identifiers, used by Alembic.
revision = '4ba7da4fe369'
down_revision = '8b170388b1b0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('organisation',
                  sa.Column('maintenance', sa.Boolean(), server_default=sa.false())
                  )


def downgrade():
    op.drop_column('organisation', 'maintenance')
