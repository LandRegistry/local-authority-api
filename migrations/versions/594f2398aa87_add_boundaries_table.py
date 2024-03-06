"""Add boundaries table

Revision ID: 594f2398aa87
Revises: dd2e44336bda
Create Date: 2017-08-24 11:34:11.683642

"""

# revision identifiers, used by Alembic.
revision = '594f2398aa87'
down_revision = 'dd2e44336bda'

from alembic import op
from flask import current_app
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    op.create_table('boundaries',
                    sa.Column('gid', sa.Integer(), primary_key=True, nullable=False),
                    sa.Column('name', sa.String(60)),
                    sa.Column('area_code', sa.String(3)),
                    sa.Column('descriptio', sa.String(50)),
                    sa.Column('file_name', sa.String(50)),
                    sa.Column('number', sa.Float(53)),
                    sa.Column('number0', sa.Float(53)),
                    sa.Column('polygon_id', sa.Float(53)),
                    sa.Column('unit_id', sa.Float(53)),
                    sa.Column('code', sa.String(9)),
                    sa.Column('hectares', sa.Float(53)),
                    sa.Column('area', sa.Float(53)),
                    sa.Column('type_code', sa.String(2)),
                    sa.Column('descript0', sa.String(25)),
                    sa.Column('type_cod0', sa.String(3)),
                    sa.Column('descript1', sa.String(36)),
                    sa.Column('geom', geoalchemy2.types.Geometry(geometry_type="MULTIPOLYGON", srid=27700), nullable=False))
    op.execute("GRANT SELECT ON boundaries TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.drop_table('boundaries')
