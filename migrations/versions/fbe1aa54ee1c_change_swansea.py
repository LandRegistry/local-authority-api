"""Change Swansea

Revision ID: fbe1aa54ee1c
Revises: 35cc07609395
Create Date: 2022-03-31 14:01:30.633937

"""

# revision identifiers, used by Alembic.
revision = 'fbe1aa54ee1c'
down_revision = '35cc07609395'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("UPDATE organisation "
               "SET title = 'Swansea Council', "
               "historic_names = jsonb_set(historic_names, array['valid_names'], "
               "(historic_names -> 'valid_names') || '[\"Swansea Council\"]') "
               "WHERE title = 'City and County of Swansea';")


def downgrade():
    op.execute("UPDATE organisation "
               "SET title = 'City and County of Swansea', "
               "historic_names = jsonb_set(historic_names, array['valid_names'], "
               "(historic_names -> 'valid_names') - 'Swansea Council') "
               "WHERE title = 'Swansea Council';")
