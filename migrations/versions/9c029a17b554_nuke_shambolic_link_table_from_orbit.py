"""Nuke shambolic link table from orbit

Revision ID: 9c029a17b554
Revises: fbe1aa54ee1c
Create Date: 2022-04-07 12:45:16.376226

"""

# revision identifiers, used by Alembic.
import sqlalchemy as sa
from flask import current_app
from alembic import op
revision = '9c029a17b554'
down_revision = 'fbe1aa54ee1c'


def upgrade():
    op.execute("UPDATE organisation_name_mapping SET organisation_name = 'Swansea Council' "
               "WHERE organisation_name = 'City and County of Swansea';")
    op.add_column('organisation',
                  sa.Column('boundaries_gid', sa.Integer())
                  )

    op.execute("UPDATE organisation o SET boundaries_gid = "
               "(SELECT b.gid FROM organisation_name_mapping onm JOIN boundaries b ON onm.boundaries_name = b.name "
               "WHERE onm.organisation_name = o.title);")

    op.create_foreign_key("organisation_boundary_gid_fkey", "organisation",
                          "boundaries", ["boundaries_gid"], ["gid"])
    op.create_index('ix_organisation_boundaries_gid', 'organisation', ['boundaries_gid'])
    op.drop_table('organisation_name_mapping')


def downgrade():
    op.create_table('organisation_name_mapping',
                    sa.Column('organisation_name', sa.String(), primary_key=True),
                    sa.Column('boundaries_name', sa.String(), unique=True))
    op.execute("GRANT SELECT, INSERT ON organisation_name_mapping TO " + current_app.config.get("APP_SQL_USERNAME"))

    conn = op.get_bind()
    result = conn.exec_driver_sql("SELECT o.title, b.name FROM organisation o "
                          "JOIN boundaries b ON o.boundaries_gid = b.gid;").fetchall()

    for row in result:

        op.execute("INSERT INTO organisation_name_mapping(organisation_name, boundaries_name) "
                   "VALUES ('{}', '{}');".format(row[0].replace("'", "''"), row[1].replace("'", "''")))

    op.drop_column('organisation', 'boundaries_gid')

    op.execute("UPDATE organisation_name_mapping SET organisation_name = 'City and County of Swansea' "
               "WHERE organisation_name = 'Swansea Council';")
