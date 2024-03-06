"""Cumberland mergers

Revision ID: ed687a064d67
Revises: 90d8e9bcb2ed
Create Date: 2023-03-09 17:14:21.475429

"""

# revision identifiers, used by Alembic.
revision = 'ed687a064d67'
down_revision = '90d8e9bcb2ed'

from alembic import op
import sqlalchemy as sa


# Cumberland Council (replaces Copeland, Allerdale and Carlisle, plus Cumbria County Council (OOA))
# Carlisle need to become a historic name for Cumberland - but Cumberland boundary still needs to be the
# ‘Carlisle’ boundary, ie for Cumberland Council boundaries are not merged.
# “Is your authority migrated” must be updated to reflect the new names.
# For Cumberland there will be 3 entries:
# Cumberland Council;
# Cumberland Council (formerly Allerdale Borough Council);
# and Cumberland Council (formerly Copeland Borough Council)
ORGS = {
    'Carlisle City Council': 'Carlisle District (B)',
    'Cumbria County Council': None,
}

NAME_CHANGES = {
    'Allerdale Borough Council': 'Cumberland Council (formerly Allerdale Borough Council)',
    'Copeland Borough Council': 'Cumberland Council (formerly Copeland Borough Council)'
}


def upgrade():
    boundary_names = "', '".join([boundary for boundary in ORGS.values() if boundary])
    sub_query = f"SELECT ST_Multi(ST_UnaryUnion(ST_Collect(geom))) FROM boundaries WHERE name IN ('{boundary_names}')"
    query = f"INSERT INTO boundaries(gid, name, geom) VALUES (750, 'Cumberland Council', ({sub_query}));"
    op.execute(query)
    current_titles = "', '".join([str(key) for key in ORGS.keys()])
    sub_query = "SELECT json_build_object('valid_names', jsonb_agg(valid_names.valid_name) || " \
        + "'[\"Cumberland Council\"]'::jsonb) FROM organisation o " \
        + "JOIN LATERAL jsonb_array_elements(o.historic_names-> 'valid_names') AS valid_names(valid_name) " \
        + f"on true WHERE o.title in ('{current_titles}')"

    op.execute("INSERT INTO organisation(title, migrated, type_id, notice, scottish, "
               "maintenance, historic_names, boundaries_gid) "
               "VALUES('Cumberland Council', true, 1, false, false, false, "
               f"({sub_query}), 750);")

    current_titles_las = "', '".join([str(key) for key, value in ORGS.items() if value])
    current_titles_ooas = "', '".join([str(key) for key, value in ORGS.items() if not value])
    op.execute(f"UPDATE organisation SET type_id = 4 WHERE title in ('{current_titles_las}');")
    op.execute(f"UPDATE organisation SET type_id = 5 WHERE title in ('{current_titles_ooas}');")

    for old, new in NAME_CHANGES.items():
        op.execute(f"UPDATE organisation SET title = '{new}' WHERE title = '{old}';")
        op.execute("UPDATE organisation SET historic_names = "
                   "jsonb_set(historic_names, array['valid_names'], historic_names->'valid_names' || "
                   f"'[\"{new}\"]'::jsonb) "
                   f"WHERE title = '{new}';")


def downgrade():
    op.execute("DELETE FROM organisation WHERE title = 'Cumberland Council';")
    op.execute("DELETE FROM boundaries WHERE gid = 750;")
    old_titles_las = "', '".join([str(key) for key, value in ORGS.items() if value])
    old_titles_ooas = "', '".join([str(key) for key, value in ORGS.items() if not value])
    op.execute(f"UPDATE organisation SET type_id = 1 WHERE title in ('{old_titles_las}');")
    op.execute(f"UPDATE organisation SET type_id = 2 WHERE title in ('{old_titles_ooas}');")

    for old, new in NAME_CHANGES.items():
        op.execute(f"UPDATE organisation SET title = '{old}' WHERE title = '{new}';")
        op.execute("UPDATE organisation SET historic_names = "
                   "jsonb_set(historic_names, array['valid_names'], (historic_names->'valid_names')::jsonb - "
                   f"'{new}') WHERE title = '{old}';")
