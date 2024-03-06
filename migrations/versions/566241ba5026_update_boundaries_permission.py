"""Update boundaries permission

Revision ID: 566241ba5026
Revises: fd4c46c0387a
Create Date: 2018-10-17 20:19:36.222122

"""

# revision identifiers, used by Alembic.
revision = '566241ba5026'
down_revision = 'fd4c46c0387a'

from alembic import op
import sqlalchemy as sa
from flask import current_app

def upgrade():
    op.execute("GRANT UPDATE ON boundaries TO " + current_app.config.get("APP_SQL_USERNAME"))


def downgrade():
    op.execute("REVOKE UPDATE ON boundaries FROM " + current_app.config.get("APP_SQL_USERNAME"))
