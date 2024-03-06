"""Add Isle of Man

Revision ID: 32b25806eb6f
Revises: 4ba7da4fe369
Create Date: 2020-09-16 17:04:28.945463

"""

# revision identifiers, used by Alembic.
revision = '32b25806eb6f'
down_revision = '4ba7da4fe369'

from alembic import op
import sqlalchemy as sa
import os
from local_authority_api import config
from local_authority_api.alembic_utils.shapefile_loader import load_shapefile


def upgrade():

    load_shapefile(op, "./fragments/data/isleofman_bng.shp", "public.boundaries")


def downgrade():
    op.execute("DELETE FROM boundaries WHERE name = 'Isle Of Man';")
