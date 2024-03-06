"""New boundaries with mergers

Revision ID: b332431b6e07
Revises: 72d61d460997
Create Date: 2019-10-16 13:21:08.111967

"""

# revision identifiers, used by Alembic.
revision = 'b332431b6e07'
down_revision = '72d61d460997'

from alembic import op
import sqlalchemy as sa
from subprocess import check_output, CalledProcessError, STDOUT, Popen, PIPE
import os
from local_authority_api import config
from local_authority_api.alembic_utils.shapefile_loader import load_shapefile


REMOVE = {
    'Christchurch Borough Council': 'Christchurch District (B)',
    'Bournemouth Borough Council': 'Bournemouth (B)',
    'Borough of Poole': 'Poole (B)',
    'East Dorset District Council': 'East Dorset District',
    'North Dorset District Council': 'North Dorset District',
    'West Dorset District Council': 'West Dorset District',
    'Purbeck District Council': 'Purbeck District',
    'Weymouth and Portland Borough Council': 'Weymouth and Portland District (B)',
    'Forest Heath District Council': 'Forest Heath District',
    'St Edmundsbury Borough Council': 'St. Edmundsbury District (B)',
    'Suffolk Coastal District Council': 'Suffolk Coastal District',
    'Waveney District Council': 'Waveney District',
    'West Somerset District Council': 'West Somerset District',
    'Taunton Deane Borough Council': 'Taunton Deane District (B)',
    'Folkestone and Hythe District Council': 'Shepway District'
}

ADD = {
    'Bournemouth, Christchurch and Poole Council': 'Bournemouth, Christchurch and Poole',
    'Dorset Council': 'Dorset',
    'West Suffolk Council': 'West Suffolk District',
    'East Suffolk Council': 'East Suffolk District',
    'Somerset West and Taunton Council': 'Somerset West and Taunton District',
    'Folkestone and Hythe District Council': 'Folkestone and Hythe District'
}


def upgrade():
    # Delete old boundary data
    query = "DELETE FROM boundaries;"
    op.execute(query)

    load_shapefile(op, "./fragments/data/2019_district_borough_unitary_region.shp", "public.boundaries")

    query = 'DELETE FROM organisation_name_mapping WHERE organisation_name IN ({});'.format(
        ', '.join('\'' + organisation_name + '\'' for organisation_name in REMOVE.keys()))
    op.execute(query)

    query = 'DELETE FROM organisation WHERE title IN ({});'.format(
        ', '.join('\'' + organisation_name + '\'' for organisation_name in REMOVE.keys()))
    op.execute(query)

    # Folkestone one was previously messed up so remove
    query = "DELETE FROM organisation_name_mapping WHERE organisation_name = 'Folkestone and Hythe District Council';"
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
    query = "DELETE FROM boundaries;"
    op.execute(query)

    load_shapefile(op, "./fragments/data/f4560bd06da5_district_borough_unitary_region.shp", "public.boundaries")

    query = 'DELETE FROM organisation_name_mapping WHERE organisation_name IN ({});'.format(
        ', '.join('\'' + organisation_name + '\'' for organisation_name in ADD.keys()))
    op.execute(query)

    query = 'DELETE FROM organisation WHERE title IN ({});'.format(
        ', '.join('\'' + organisation_name + '\'' for organisation_name in ADD.keys()))
    op.execute(query)

    # Folkestone one was previously messed up so remove if there
    query = "DELETE FROM organisation_name_mapping WHERE organisation_name = 'Folkestone and Hythe District Council';"
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
