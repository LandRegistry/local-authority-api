"""North Yorkshire mergers

Revision ID: 90d8e9bcb2ed
Revises: c43bf1b81cb2
Create Date: 2023-03-08 11:59:14.711224

"""

# revision identifiers, used by Alembic.
revision = '90d8e9bcb2ed'
down_revision = 'c43bf1b81cb2'

from alembic import op
import sqlalchemy as sa


# North Yorkshire Council (replaces Craven, Hambleton, Harrogate, Richmondshire, Rydale, Scarborough and Selby
#  - plus North Yorkshire County Council (OOA))
ORGS = {
    'Craven District Council': 'Craven District',
    'Hambleton District Council': 'Hambleton District',
    'Harrogate Borough Council': 'Harrogate District (B)',
    'Richmondshire District Council': 'Richmondshire District',
    'Ryedale District Council': 'Ryedale District',
    'Scarborough Borough Council': 'Scarborough District (B)',
    'Selby District Council': 'Selby District',
    'North Yorkshire County Council': None,
}


def upgrade():
    boundary_names = "', '".join([boundary for boundary in ORGS.values() if boundary])
    sub_query = f"SELECT ST_Multi(ST_UnaryUnion(ST_Collect(geom))) FROM boundaries WHERE name IN ('{boundary_names}')"
    query = f"INSERT INTO boundaries(gid, name, geom) VALUES (751, 'The North Yorkshire Council', ({sub_query}));"
    op.execute(query)
    current_titles = "', '".join([str(key) for key in ORGS.keys()])
    sub_query = "SELECT json_build_object('valid_names', jsonb_agg(valid_names.valid_name) || " \
        + "'[\"The North Yorkshire Council\"]'::jsonb) FROM organisation o " \
        + "JOIN LATERAL jsonb_array_elements(o.historic_names-> 'valid_names') AS valid_names(valid_name) " \
        + f"on true WHERE o.title in ('{current_titles}')"

    op.execute("INSERT INTO organisation(title, migrated, type_id, notice, scottish, "
               "maintenance, historic_names, boundaries_gid) "
               "VALUES('The North Yorkshire Council', true, 1, false, false, false, "
               f"({sub_query}), 751);")

    current_titles_las = "', '".join([str(key) for key, value in ORGS.items() if value])
    current_titles_ooas = "', '".join([str(key) for key, value in ORGS.items() if not value])
    op.execute(f"UPDATE organisation SET type_id = 4 WHERE title in ('{current_titles_las}');")
    op.execute(f"UPDATE organisation SET type_id = 5 WHERE title in ('{current_titles_ooas}');")


def downgrade():
    op.execute("DELETE FROM organisation WHERE title = 'The North Yorkshire Council';")
    op.execute("DELETE FROM boundaries WHERE gid = 751;")
    old_titles_las = "', '".join([str(key) for key, value in ORGS.items() if value])
    old_titles_ooas = "', '".join([str(key) for key, value in ORGS.items() if not value])
    op.execute(f"UPDATE organisation SET type_id = 1 WHERE title in ('{old_titles_las}');")
    op.execute(f"UPDATE organisation SET type_id = 2 WHERE title in ('{old_titles_ooas}');")
