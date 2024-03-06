"""Remove erroneous OOAs from list (Part 1 & 2)

Revision ID: fd4c46c0387a
Revises: 17f4ca8c827b
Create Date: 2019-04-30 12:52:18.007389

"""

# revision identifiers, used by Alembic.
revision = 'fd4c46c0387a'
down_revision = '17f4ca8c827b'

from alembic import op
from flask import current_app
import sqlalchemy as sa


other_originating_authorities = [
    "Airport Operator",
    "Courts",
    "External Solicitors",
    "GPSS",
    "HS2",
    "Internal Drainage",
    "John German",
    "Land Compensation",
    "Lands Tribunal",
    "MOD",
    "Environment Services",
    "Mayoral & Development Corporation",
    "Officer of the Clerk to Commissioners",
    "STG",
    "Test Valley",
    "WRS",
    "Broads",
    "CAA",
    "Dartmoor",
    "Defra",
    "Exmoor",
    "Highways",
    "Lake District",
    "Nature Conservancy Council",
    "New Forest",
    "Northumbrerland",
    "North York Moors",
    "Peak District",
    "South Downs",
    "Yorkshire Dales",
    "Coalboard",
    "Department of Transport",
    "Dept of Culture Media & Sport",
    "Oribital Housing",
    "Crossrall"
]


def upgrade():
    query = 'DELETE FROM organisation WHERE title IN ({});'.format(', '.join('\'' + ooa.replace("\'", "\'\'") + '\'' for ooa in other_originating_authorities))
    op.execute(query)


def downgrade():
    for ooa in other_originating_authorities:
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = '{0}') THEN INSERT INTO organisation " \
                "(title, migrated, type_id) VALUES ('{0}', 'f', 2); END IF; END $$;".format(ooa.replace("\'", "\'\'"))
        op.execute(query)
