"""add historic oa names

Revision ID: 05be07b7fb0b
Revises: 905de15d31cc
Create Date: 2021-09-22 14:55:55.551573

"""

# revision identifiers, used by Alembic.
revision = '05be07b7fb0b'
down_revision = '905de15d31cc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import json

new_organisations = [
    "Livv Housing Trust",
    "Archbishop of York",
    "Crossrail 1",
    "Crossrail 2",
    "Historic England",
    "High Speed Two (HS2) Limited",
    "London Legacy Development Corporation",
    "Broads Authority",
    "Civil Aviation Authority",
    "Dartmoor National Park Authority",
    "Department for Environment, Food and Rural Affairs",
    "Exmoor National Park Authority",
    "Highways England",
    "Lake District National Park Authority",
    "Natural England",
    "New Forest National Park Authority",
    "Northumberland National Park Authority",
    "North York Moors National Park Authority",
    "Peak District National Park Authority",
    "South Downs National Park Authority",
    "Yorkshire Dales National Park Authority",
    "Coal Authority",
    "Department for Transport",
    "Department for Digital, Culture, Media and Sport",
    "Orbit Housing"
]
rename_organisations = {"CLH Pipeline System (CLH-PS) Ltd": "Exolum Pipeline System Limited"}


def upgrade():
    # insert new organisations
    for org in new_organisations:
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = '{0}') THEN " \
                "INSERT INTO organisation " \
                "(title, migrated, type_id) VALUES ('{0}', 'f', 2); END IF; END $$;".format(org)
        op.execute(query)

    # add historic column and populate
    op.add_column('organisation', sa.Column('historic_names', postgresql.JSONB(), nullable=True))
    update_historic_names()
    op.alter_column('organisation', 'historic_names', nullable=False)
    update_organisation_names(True)


def downgrade():
    # remove new organisations
    for org in new_organisations:
        query = "DELETE FROM organisation " \
                "where historic_names -> 'valid_names' @> '\"{}\"';".format(org)
        op.execute(query)

    # remove historic column
    op.drop_column('organisation', 'historic_names')
    update_organisation_names(False)


# Loop through current organisation table and add the existing names to the JSON field in the Database
def update_historic_names():
    conn = op.get_bind()
    query = "SELECT title FROM organisation;"
    res = conn.exec_driver_sql(query)
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Missing Organisations")

    for result in results:
        # escape out single quotes in certain organisation names
        organisation_name = result[0].replace("'", "''")
        new_organisation_name = rename_organisations.get(result[0])

        display_name_current = {"valid_names": [organisation_name]}

        if new_organisation_name is not None:
            display_name_current["valid_names"].append(new_organisation_name.replace("'", "''"))

        query = ("UPDATE organisation SET historic_names = '{0}' WHERE title = '{1}';".
                 format(json.dumps(display_name_current), organisation_name))
        op.execute(query)


def update_organisation_names(upgrading):
    for key in rename_organisations:
        if upgrading:
            old_name = key
            new_name = rename_organisations[key]
        else:
            old_name = rename_organisations[key]
            new_name = key

    query = ("UPDATE organisation SET title = '{}' WHERE title = '{}';"
             .format(new_name, old_name))
    op.execute(query)
