"""Update name of Trafford

Revision ID: 3bde0ebd11f3
Revises: 5bea2097ec89
Create Date: 2022-12-14 14:04:38.751195

"""

# revision identifiers, used by Alembic.
revision = '3bde0ebd11f3'
down_revision = '5bea2097ec89'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("UPDATE organisation "
               "SET title = 'Trafford Borough Council', "
               "historic_names = jsonb_set(historic_names, array['valid_names'], "
               "(historic_names -> 'valid_names') || '[\"Trafford Borough Council\"]') "
               "WHERE title = 'Trafford Metropolitan Borough Council';")


def downgrade():
    op.execute("UPDATE organisation "
               "SET title = 'Trafford Metropolitan Borough Council', "
               "historic_names = jsonb_set(historic_names, array['valid_names'], "
               "(historic_names -> 'valid_names') - 'Trafford Borough Council') "
               "WHERE title = 'Trafford Borough Council';")
