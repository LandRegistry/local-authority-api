"""remove Fisher German

Revision ID: 8b170388b1b0
Revises: b332431b6e07
Create Date: 2020-02-19 15:09:47.506570

"""

# revision identifiers, used by Alembic.
revision = '8b170388b1b0'
down_revision = 'b332431b6e07'

from alembic import op


def upgrade():
    query = "DELETE FROM organisation WHERE title = 'Fisher German';"
    op.execute(query)


def downgrade():
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = 'Fisher German') THEN " \
            "INSERT INTO organisation " \
            "(title, migrated, type_id) VALUES ('Fisher German', 'f', 2); END IF; END $$;"
    op.execute(query)
