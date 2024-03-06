"""Update the organisation name of one of the authorities

Revision ID: 76dcfa8e78bd
Revises: 795bb4fddb8a
Create Date: 2018-08-15 13:05:29.656695

"""

# revision identifiers, used by Alembic.
revision = '76dcfa8e78bd'
down_revision = '795bb4fddb8a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("UPDATE organisation_name_mapping \
    set organisation_name = 'Folkstone & Hythe District Council', \
    boundaries_name = 'Folkstone and Hythe District' \
    where organisation_name = 'Shepway District Council'")

    op.execute("UPDATE organisation \
    set title = 'Folkstone & Hythe District Council' \
    where title = 'Shepway District Council'")

    op.execute("UPDATE boundaries \
    set name = 'Folkstone and Hythe District' \
    where name = 'Shepway District'")

def downgrade():
    op.execute("UPDATE organisation_name_mapping \
    set organisation_name = 'Shepway District Council', \
    boundaries_name = 'Shepway District' \
    where organisation_name = 'Folkstone & Hythe District Council'")

    op.execute("UPDATE organisation \
    set title = 'Shepway District Council' \
    where title = 'Folkstone & Hythe District Council'")

    op.execute("UPDATE boundaries \
    set name = 'Shepway District' \
    where name = 'Folkstone and Hythe District'")
