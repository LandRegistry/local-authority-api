"""Add migrated authority type

Revision ID: c43bf1b81cb2
Revises: 3bde0ebd11f3
Create Date: 2023-03-08 11:20:53.903957

"""

# revision identifiers, used by Alembic.
revision = 'c43bf1b81cb2'
down_revision = '3bde0ebd11f3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add new Authority type
    query = "INSERT INTO organisation_type (id, type) VALUES (4, 'Migrated Local Authority');"
    op.execute(query)
    query = "INSERT INTO organisation_type (id, type) VALUES (5, 'Migrated Other Originating Authority');"
    op.execute(query)


def downgrade():
    query = "DELETE FROM organisation_type WHERE id = 4;"
    op.execute(query)
    query = "DELETE FROM organisation_type WHERE id = 5;"
    op.execute(query)
