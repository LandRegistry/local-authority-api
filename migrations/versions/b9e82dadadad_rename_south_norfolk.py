"""Rename South Norfolk

Revision ID: b9e82dadadad
Revises: f3111040b82c
Create Date: 2022-06-06 13:13:30.284229

"""

# revision identifiers, used by Alembic.
revision = 'b9e82dadadad'
down_revision = 'f3111040b82c'

from alembic import op


def upgrade():
    op.execute("UPDATE organisation "
               "SET title = 'South Norfolk Council', "
               "historic_names = jsonb_set(historic_names, array['valid_names'], "
               "(historic_names -> 'valid_names') || '[\"South Norfolk Council\"]') "
               "WHERE title = 'South Norfolk District Council';")


def downgrade():
    op.execute("UPDATE organisation "
               "SET title = 'South Norfolk District Council', "
               "historic_names = jsonb_set(historic_names, array['valid_names'], "
               "(historic_names -> 'valid_names') - 'South Norfolk Council') "
               "WHERE title = 'South Norfolk Council';")
