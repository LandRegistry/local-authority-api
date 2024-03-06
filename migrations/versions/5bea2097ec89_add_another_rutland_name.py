"""Add another rutland name

Revision ID: 5bea2097ec89
Revises: b9e82dadadad
Create Date: 2022-12-08 13:40:49.989442

"""

# revision identifiers, used by Alembic.
revision = '5bea2097ec89'
down_revision = 'b9e82dadadad'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("UPDATE organisation "
               "SET historic_names = jsonb_set(historic_names, array['valid_names'], "
               "(historic_names -> 'valid_names') || '[\"Rutland District Council\"]') "
               "WHERE title = 'Rutland County Council District Council';")


def downgrade():
    op.execute("UPDATE organisation "
               "SET historic_names = jsonb_set(historic_names, array['valid_names'], "
               "(historic_names -> 'valid_names') - 'Rutland District Council') "
               "WHERE title = 'Rutland County Council District Council';")
