"""Replace ampersands with and, fix typo for organisation names

Revision ID: 72d61d460997
Revises: 566241ba5026
Create Date: 2019-09-17 11:41:29.742600

"""

# revision identifiers, used by Alembic.
revision = '72d61d460997'
down_revision = '566241ba5026'

from alembic import op
import sqlalchemy as sa

NAME_MAPPING = {
    "London Borough of Hammersmith & Fulham": "London Borough of Hammersmith and Fulham",
    "Telford & Wrekin Council": "Telford and Wrekin Council",
    "Government Pipelines & Storage Systems": "Government Pipelines and Storage Systems",
    "Hampshire & IOW Wildlife Trust": "Hampshire and IOW Wildlife Trust",
    "Meres & Moses Housing Association": "Meres and Moses Housing Association",
    "Old Oak & Park Royal Development Corporation": "Old Oak and Park Royal Development Corporation",
    "Trent & Dove Housing": "Trent and Dove Housing",
    "Folkstone & Hythe District Council": "Folkestone and Hythe District Council"
}

def upgrade():
    for old, new in NAME_MAPPING.items():
        op.execute("UPDATE organisation \
            set title = '{}' \
            where title = '{}'".format(new, old))
        op.execute("UPDATE organisation_name_mapping \
            set organisation_name = '{}' \
            where organisation_name = '{}'".format(new, old))

def downgrade():
    for old, new in NAME_MAPPING.items():
        op.execute("UPDATE organisation \
            set title = '{}' \
            where title = '{}'".format(old, new))
        op.execute("UPDATE organisation_name_mapping \
            set organisation_name = '{}' \
            where organisation_name = '{}'".format(old, new))
