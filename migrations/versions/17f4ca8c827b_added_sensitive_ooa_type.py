"""added sensitive OOA type

Revision ID: 17f4ca8c827b
Revises: b95e1b9139a8
Create Date: 2019-04-11 13:17:11.418528

"""

# revision identifiers, used by Alembic.
revision = '17f4ca8c827b'
down_revision = 'b95e1b9139a8'

from alembic import op

CLH_OOA = "CLH Pipeline System (CLH-PS) Ltd"


def upgrade():
    # Add new Authority type
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation_type WHERE id = 3) THEN INSERT INTO " \
            "organisation_type (id, type) VALUES (3, 'Sensitive Other Originating Authority'); END IF; END $$;"
    op.execute(query)

    # Add new sensitive authority
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = '{0}') THEN INSERT INTO organisation " \
            "(title, migrated, type_id) VALUES ('{0}', 'f', 3); END IF; END $$;".format(CLH_OOA)
    op.execute(query)


def downgrade():
    # delete ALL SOOAs in case someone added more through the frontend
    query = "DELETE FROM organisation WHERE type_id = 3;"
    op.execute(query)

    query = "DELETE FROM organisation_type WHERE id = 3;"
    op.execute(query)
