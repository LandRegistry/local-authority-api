"""Update OOA list, removing 9 and adding 2 to the database.

Revision ID: 23c8f2667961
Revises: 05be07b7fb0b
Create Date: 2021-11-18 09:27:06.358981

"""

# revision identifiers, used by Alembic.
revision = '23c8f2667961'
down_revision = '05be07b7fb0b'

from alembic import op
import sqlalchemy as sa
import json

# List of OOAs that need to be removed from the database.
OOAS_TO_REMOVE = [
    "Department for Digital, Culture, Media and Sport",
    "Department for Environment",
    "Department for Environment, Food and Rural Affairs",
    "Department for Transport",
    "Ministry of Defence",
    "Ministry of Housing",
    "Ministry of Power",
    "Dorset County Council",
    "Department for Constitutional Affairs",
]

# List of OOAs that need to be added to the database.
OOAS_TO_ADD = [
    "Heart of England Housing Association Limited",
    "Southern Eastern Electricity Board"
]

# Alembic upgrade script.
def upgrade():

    # # Remove OOAs from the database
    for ooa in OOAS_TO_REMOVE:
        removal_query = "DELETE FROM organisation WHERE title = '{}'".format(ooa)
        op.execute(removal_query)

    # Add OOAS to the database
    for ooa in OOAS_TO_ADD:
        historical = {"valid_names": [ooa]}
        adding_query = "INSERT INTO organisation (title, type_id, historic_names) VALUES ('{title}', 2, '{historic}')".format(title=ooa, historic=json.dumps(historical))
        op.execute(adding_query)

# Alembic downgrade script.
def downgrade():

    # Undo new OOAs added to the database
    for ooa in OOAS_TO_ADD:
        removal_query = "DELETE FROM organisation WHERE title = '{}'".format(ooa)
        op.execute(removal_query)

    # Undo OOAs deleted from the database
    for ooa in OOAS_TO_REMOVE:
        historical = {"valid_names": [ooa]}
        adding_query = "INSERT INTO organisation (title, type_id, historic_names) VALUES ('{title}', 2, '{historic}')".format(title=ooa, historic=json.dumps(historical))
        op.execute(adding_query)
