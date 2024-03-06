"""Add OOA's to organisation table and flag to distinguish from LA

Revision ID: 9e25640a3592
Revises: 312844850b7a
Create Date: 2018-05-09 14:29:16.503041

"""

# revision identifiers, used by Alembic.
revision = '9e25640a3592'
down_revision = '312844850b7a'

from alembic import op
from flask import current_app
import sqlalchemy as sa


other_originating_authorities = [
    'Airport Operator',
    'Anglian Water',
    'British Pipeline Authority',
    'Broads',
    'Buckinghamshire County Council',
    'CAA',
    'Cambridgeshire County Council',
    'Cambridge Water',
    'Church Commissioners',
    'Coalboard',
    'Courts',
    'Crossrall',
    'Cumbria County Council',
    'Dartmoor',
    'Defra',
    'Department for Constitutional Affairs',
    'Department for Environment',
    'Department of Transport',
    'Dept of Culture Media & Sport',
    'Derbyshire County Council',
    'Devon County Council',
    'Dorset County Council',
    'East Kent Housing',
    'East Sussex County Council',
    'Ebbsfleet Development Corporation',
    'English Partnership',
    'Environment Agency',
    'Environmental Services',
    'Environment Services',
    'Essex County Council',
    'Exmoor',
    'External Solicitors',
    'Fisher German',
    'Forestry Commission',
    'Futures Housing Association',
    'Gloucestershire County Council',
    'Government Pipelines & Storage Systems',
    'GPSS',
    'Greenfields Housing Association',
    'Group Heart of England',
    'Hampshire & IOW Wildlife Trust',
    'Hampshire County Council',
    'Hereford Housing',
    'Hertfordshire County Council',
    'Highways',
    'HS2',
    'Internal Drainage',
    'John German',
    'Kent County Council',
    'Knowsley Housing Trust',
    'Lake District',
    'Lancashire County Council',
    'Land Compensation',
    'Lands Tribunal',
    'Leicestershire County Council',
    'Lincolnshire County Council',
    'Magna Housing',
    'Mayoral & Development Corporation',
    'Meres & Moses Housing Association',
    'Mersey Travel',
    'Ministry of Defence',
    'Ministry of Housing',
    'Ministry of Power',
    'MOD',
    'National Grid',
    'National Radiological Protection Board',
    'National Rivers',
    'Nature Conservancy Council',
    'New Forest',
    'Norfolk County Council',
    'Northamptonshire County Council',
    'Northumbrerland',
    'Northumbrian Water',
    'North York Moors',
    'North Yorkshire County Council',
    'Nottinghamshire County Council',
    'Officer of the Clerk to Commissioners',
    'Old Oak & Park Royal Development Corporation',
    'One Vision Housing',
    'Oribital Housing',
    'Oxfordshire County Council',
    'Peak District',
    'Red Kite',
    'Rochdale Boroughwide Housing Ltd',
    'Sanctuary Housing',
    'Secretary of State',
    'Sector Housing Solution',
    'Severn Trent',
    'Somerset County Council',
    'South Downs',
    'South Eastern Economic Development Area',
    'Southern Water',
    'South West Water',
    'Staffordshire County Council',
    'STG',
    'Suffolk County Council',
    'Surrey County Council',
    'Swale Planning Policy',
    'Tees Valley Combined Authority',
    'Test Valley',
    'Thames Tunnel',
    'Thames Water',
    'The Solicitor of Basildon Development Commission',
    'Transco',
    'Trent & Dove Housing',
    'United Utilities',
    'Warwickshire County Council',
    'Wessex Water',
    'West Sussex County Council',
    'Worcester Regulatory Authority',
    'Worcestershire County Council',
    'WRS',
    'Yorkshire Coast Homes',
    'Yorkshire Dales',
    'Yorkshire Water'
]


def upgrade():
    organisation_type_table = op.create_table('organisation_type',
                    sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
                    sa.Column('type', sa.String(60)))
    op.execute("GRANT SELECT, INSERT ON organisation_type TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.execute("GRANT SELECT, USAGE ON organisation_type_id_seq TO " + current_app.config.get("APP_SQL_USERNAME"))
    op.bulk_insert(organisation_type_table, [{'id': 1, 'type': 'Local Authority'},
                                             {'id': 2, 'type': 'Other Originating Authority'}])

    op.add_column('organisation', sa.Column('type_id', sa.Integer(), sa.ForeignKey('organisation_type.id')))

    # Update all LA's organisation_type
    op.execute("UPDATE organisation SET type_id = 1;")
    # Add OOA's
    for ooa in other_originating_authorities:
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = '{0}') THEN INSERT INTO organisation " \
                "(title, migrated, type_id) VALUES ('{0}', 'f', 2); END IF; END $$;".format(ooa.replace("\'", "\'\'"))
        op.execute(query)


def downgrade():
    query = 'DELETE FROM organisation WHERE title IN ({});'.format(', '.join('\'' + ooa.replace("\'", "\'\'") + '\'' for ooa in other_originating_authorities))
    op.execute(query)

    op.drop_column('organisation', 'type_id')
    op.drop_table('organisation_type')
