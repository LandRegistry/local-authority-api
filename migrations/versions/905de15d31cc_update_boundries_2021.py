"""update_boundries_2021

Revision ID: 905de15d31cc
Revises: 32b25806eb6f
Create Date: 2021-09-14 12:38:57.645447

"""

# revision identifiers, used by Alembic.
revision = '905de15d31cc'
down_revision = '32b25806eb6f'

from alembic import op
import sqlalchemy as sa
from subprocess import check_output, CalledProcessError, STDOUT, Popen, PIPE
import os
from local_authority_api import config
from local_authority_api.alembic_utils.shapefile_loader import load_shapefile

REMOVE = {
    "Corby Borough Council": "Corby District (B)",
    "South Northamptonshire Council": "South Northamptonshire District",
    "Chiltern District Council": "Chiltern District",
    "Wellingborough Borough Council": "Wellingborough District (B)",
    "East Northamptonshire Council": "East Northamptonshire District",
    "Kettering Borough Council": "Kettering District (B)",
    "Northampton Borough Council": "Northampton District (B)",
    "Aylesbury Vale District Council": "Aylesbury Vale District",
    "Daventry District Council": "Daventry District",
    "Torfaen County Borough Council": "Tor-faen - Torfaen",
    "South Bucks District Council": "South Bucks District",
    "Wycombe District Council": "Wycombe District"
}

ADD = {
    "North Northamptonshire Council": "North Northamptonshire",
    "Buckinghamshire Council": "Buckinghamshire",
    "West Northamptonshire Council": "West Northamptonshire",
    "Torfaen County Borough Council": "Torfaen - Torfaen",
}


def upgrade():
    # Delete old boundary data
    query = "DELETE FROM boundaries WHERE name <> 'Isle Of Man';"
    op.execute(query)

    load_shapefile(op, "./fragments/data/2021_district_borough_unitary_region.shp", "public.boundaries")

    query = 'DELETE FROM organisation_name_mapping WHERE organisation_name IN ({});'.format(
        ', '.join('\'' + organisation_name + '\'' for organisation_name in REMOVE.keys()))
    op.execute(query)

    query = 'DELETE FROM organisation WHERE title IN ({});'.format(
        ', '.join('\'' + organisation_name + '\'' for organisation_name in REMOVE.keys()))
    op.execute(query)

    for organisation_name, boundaries_name in ADD.items():
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation_name_mapping WHERE organisation_name = '{0}') THEN INSERT INTO organisation_name_mapping " \
            "(organisation_name, boundaries_name) VALUES ('{0}', '{1}'); END IF; END $$;".format(
                organisation_name, boundaries_name)
        op.execute(query)
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = '{0}') THEN INSERT INTO organisation " \
            "(title, migrated, type_id, notice, scottish) VALUES ('{0}', 'f', 1, 'f', 'f'); END IF; END $$;".format(
                organisation_name)
        op.execute(query)

    # Reapply boundary update
    boundary_update()


def downgrade():
    # Delete new boundary data
    query = "DELETE FROM boundaries WHERE name <> 'Isle Of Man';"
    op.execute(query)

    load_shapefile(op, "./fragments/data/2019_district_borough_unitary_region.shp", "public.boundaries")

    query = 'DELETE FROM organisation_name_mapping WHERE organisation_name IN ({});'.format(
        ', '.join('\'' + organisation_name + '\'' for organisation_name in ADD.keys()))
    op.execute(query)

    query = 'DELETE FROM organisation WHERE title IN ({});'.format(
        ', '.join('\'' + organisation_name + '\'' for organisation_name in ADD.keys()))
    op.execute(query)

    for organisation_name, boundaries_name in REMOVE.items():
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation_name_mapping WHERE organisation_name = '{0}') THEN INSERT INTO organisation_name_mapping " \
            "(organisation_name, boundaries_name) VALUES ('{0}', '{1}'); END IF; END $$;".format(
                organisation_name, boundaries_name)
        op.execute(query)
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = '{0}') THEN INSERT INTO organisation " \
            "(title, migrated, type_id, notice, scottish) VALUES ('{0}', 'f', 1, 'f', 'f'); END IF; END $$;".format(
                organisation_name)
        op.execute(query)

    # Reapply boundary update
    boundary_update()


def boundary_update():
    with open(os.path.join(os.getcwd(), 'local_authority_api', 'static', 'boundary_update.sql'), 'r', encoding='utf8') as f:
        sql_file = f.read()
        # split all of the SQL commands and execute them
        sql_commands = sql_file.split(';')
        for command in sql_commands[:-1]:
            op.execute(command)
