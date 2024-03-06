"""Change Hull

Revision ID: 55f7586bf5a4
Revises: e2002fbbbbf4
Create Date: 2023-04-14 10:29:27.510849

"""

# revision identifiers, used by Alembic.
revision = '55f7586bf5a4'
down_revision = 'e2002fbbbbf4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("UPDATE organisation "
               "SET title = 'Kingston Upon Hull City Council', "
               "historic_names = '{\"valid_names\": [\"Kingston Upon Hull City Council\"]}' "
               "WHERE title = 'Hull City Council';")


def downgrade():
    op.execute("UPDATE organisation "
               "SET title = 'Hull City Council', "
               "historic_names = '{\"valid_names\": [\"Hull City Council\"]}' "
               "WHERE title = 'Kingston Upon Hull City Council';")
