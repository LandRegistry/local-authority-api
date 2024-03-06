"""Westmorland and Furness Council mergers

Revision ID: 7a4c927ddb84
Revises: ed687a064d67
Create Date: 2023-03-09 17:51:27.946807

"""

# revision identifiers, used by Alembic.
revision = '7a4c927ddb84'
down_revision = 'ed687a064d67'

from alembic import op
import sqlalchemy as sa


# Westmorland and Furness Council (replaces Barrow-in-Furness, Eden, South Lakeland, plus Cumbria County Council (OOA))
# These are not yet migrated so any charges for Cumbria County Council that exist currently will not be for this
# authority
ORGS = {
    'Barrow-in-Furness Borough Council': 'Barrow-in-Furness District (B)',
    'Eden District Council': 'Eden District',
    'South Lakeland District Council': 'South Lakeland District'
}


def upgrade():
    boundary_names = "', '".join([boundary for boundary in ORGS.values() if boundary])
    sub_query = f"SELECT ST_Multi(ST_UnaryUnion(ST_Collect(geom))) FROM boundaries WHERE name IN ('{boundary_names}')"
    query = f"INSERT INTO boundaries(gid, name, geom) VALUES (749, 'Westmorland and Furness Council', ({sub_query}));"
    op.execute(query)
    current_titles = "', '".join([str(key) for key in ORGS.keys()])
    sub_query = "SELECT json_build_object('valid_names', jsonb_agg(valid_names.valid_name) || " \
        + "'[\"Westmorland and Furness Council\"]'::jsonb) FROM organisation o " \
        + "JOIN LATERAL jsonb_array_elements(o.historic_names-> 'valid_names') AS valid_names(valid_name) " \
        + f"on true WHERE o.title in ('{current_titles}')"

    op.execute("INSERT INTO organisation(title, migrated, type_id, notice, scottish, "
               "maintenance, historic_names, boundaries_gid) "
               "VALUES('Westmorland and Furness Council', false, 1, false, false, false, "
               f"({sub_query}), 749);")

    current_titles_las = "', '".join([str(key) for key, value in ORGS.items() if value])
    current_titles_ooas = "', '".join([str(key) for key, value in ORGS.items() if not value])
    op.execute(f"UPDATE organisation SET type_id = 4 WHERE title in ('{current_titles_las}');")
    op.execute(f"UPDATE organisation SET type_id = 5 WHERE title in ('{current_titles_ooas}');")


def downgrade():
    op.execute("DELETE FROM organisation WHERE title = 'Westmorland and Furness Council';")
    op.execute("DELETE FROM boundaries WHERE gid = 749;")
    old_titles_las = "', '".join([str(key) for key, value in ORGS.items() if value])
    old_titles_ooas = "', '".join([str(key) for key, value in ORGS.items() if not value])
    op.execute(f"UPDATE organisation SET type_id = 1 WHERE title in ('{old_titles_las}');")
    op.execute(f"UPDATE organisation SET type_id = 2 WHERE title in ('{old_titles_ooas}');")
