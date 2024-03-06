"""Rename Rutland

Revision ID: f3111040b82c
Revises: 9c029a17b554
Create Date: 2022-05-18 14:13:22.374973

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from alembic import op
revision = 'f3111040b82c'
down_revision = '9c029a17b554'


def upgrade():
    op.execute('UPDATE organisation SET title = \'Rutland County Council District Council\','
               '   historic_names = \'{"valid_names": ["Rutland County Council", "Rutland County Council District Council"]}\''
               '   WHERE title = \'Rutland County Council\';')


def downgrade():
    op.execute('UPDATE organisation SET title = \'Rutland County Council\','
               '   historic_names = \'{"valid_names": ["Rutland County Council"]}\''
               '   WHERE title = \'Rutland County Council District Council\';')
