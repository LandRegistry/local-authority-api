"""Somerset Council mergers

Revision ID: e2002fbbbbf4
Revises: 7a4c927ddb84
Create Date: 2023-03-10 12:21:53.436504

"""

# revision identifiers, used by Alembic.
revision = 'e2002fbbbbf4'
down_revision = '7a4c927ddb84'

from alembic import op
import sqlalchemy as sa


# Somerset Council (replaces Mendip, Sedgemoor, Somerset West & Taunton and South Somerset,
# plus Somerset County Council (OOA))
ORGS = {
    'Mendip District Council': 'Mendip District',
    'Sedgemoor District Council': 'Sedgemoor District',
    'Somerset West and Taunton Council': 'Somerset West and Taunton District',
    'South Somerset District Council': 'South Somerset District',
    'Somerset County Council': None
}


def upgrade():
    boundary_names = "', '".join([boundary for boundary in ORGS.values() if boundary])
    sub_query = f"SELECT ST_Multi(ST_UnaryUnion(ST_Collect(geom))) FROM boundaries WHERE name IN ('{boundary_names}')"
    query = f"INSERT INTO boundaries(gid, name, geom) VALUES (748, 'Somerset Council', ({sub_query}));"
    op.execute(query)
    current_titles = "', '".join([str(key) for key in ORGS.keys()])
    sub_query = "SELECT json_build_object('valid_names', jsonb_agg(valid_names.valid_name) || " \
        + "'[\"Somerset Council\"]'::jsonb) FROM organisation o " \
        + "JOIN LATERAL jsonb_array_elements(o.historic_names-> 'valid_names') AS valid_names(valid_name) " \
        + f"on true WHERE o.title in ('{current_titles}')"

    op.execute("INSERT INTO organisation(title, migrated, type_id, notice, scottish, "
               "maintenance, historic_names, boundaries_gid) "
               "VALUES('Somerset Council', false, 1, false, false, false, "
               f"({sub_query}), 748);")

    current_titles_las = "', '".join([str(key) for key, value in ORGS.items() if value])
    current_titles_ooas = "', '".join([str(key) for key, value in ORGS.items() if not value])
    op.execute(f"UPDATE organisation SET type_id = 4 WHERE title in ('{current_titles_las}');")
    op.execute(f"UPDATE organisation SET type_id = 5 WHERE title in ('{current_titles_ooas}');")


def downgrade():
    op.execute("DELETE FROM organisation WHERE title = 'Somerset Council';")
    op.execute("DELETE FROM boundaries WHERE gid = 748;")
    old_titles_las = "', '".join([str(key) for key, value in ORGS.items() if value])
    old_titles_ooas = "', '".join([str(key) for key, value in ORGS.items() if not value])
    op.execute(f"UPDATE organisation SET type_id = 1 WHERE title in ('{old_titles_las}');")
    op.execute(f"UPDATE organisation SET type_id = 2 WHERE title in ('{old_titles_ooas}');")
