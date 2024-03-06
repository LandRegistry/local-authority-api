"""Add scottishness

Revision ID: b95e1b9139a8
Revises: 76dcfa8e78bd
Create Date: 2019-03-27 18:04:05.159611

"""

# revision identifiers, used by Alembic.
revision = 'b95e1b9139a8'
down_revision = '76dcfa8e78bd'

from alembic import op
import sqlalchemy as sa

SCOTTISH_AUTHORITIES = ["Na h-Eileanan an Iar",
                        "Highland",
                        "Moray",
                        "Aberdeenshire",
                        "Aberdeen City",
                        "Argyll and Bute",
                        "Stirling",
                        "Perth and Kinross",
                        "Angus",
                        "Dundee City",
                        "Clackmannanshire",
                        "Fife",
                        "Inverclyde",
                        "West Dunbartonshire",
                        "East Dunbartonshire",
                        "North Lanarkshire",
                        "Renfrewshire",
                        "East Renfrewshire",
                        "Glasgow City",
                        "North Ayrshire",
                        "Falkirk",
                        "West Lothian",
                        "East Lothian",
                        "City of Edinburgh",
                        "Midlothian",
                        "South Ayrshire",
                        "East Ayrshire",
                        "South Lanarkshire",
                        "Dumfries and Galloway",
                        "Scottish Borders",
                        "Dumfries and Galloway",
                        "Orkney Islands",
                        "Shetland Islands"]

WELSH_AUTHORITIES = [["Abertawe - Swansea", "City and County of Swansea"],
                     ["Blaenau Gwent - Blaenau Gwent", "Blaenau Gwent County Borough Council"],
                     ["Bro Morgannwg - the Vale of Glamorgan", "Vale of Glamorgan Council"],
                     ["Caerffili - Caerphilly", "Caerphilly County Borough Council"],
                     ["Casnewydd - Newport", "Newport City Council"],
                     ["Castell-nedd Port Talbot - Neath Port Talbot", "Neath Port Talbot County Borough Council"],
                     ["Conwy - Conwy", "Conwy County Borough Council"],
                     ["Merthyr Tudful - Merthyr Tydfil", "Merthyr Tydfil County Borough Council"],
                     ["Pen-y-bont ar Ogwr - Bridgend", "Bridgend County Borough Council"],
                     ["Powys - Powys", "Powys County Council"],
                     ["Rhondda Cynon Taf - Rhondda Cynon Taf", "Rhondda Cynon Taf County Borough Council"],
                     ["Sir Ddinbych - Denbighshire", "Denbighshire County Council"],
                     ["Sir Gaerfyrddin - Carmarthenshire", "Carmarthenshire County Council"],
                     ["Sir y Fflint - Flintshire", "Flintshire County Council"],
                     ["Tor-faen - Torfaen", "Torfaen County Borough Council"],
                     ["Wrecsam - Wrexham", "Wrexham County Borough Council"],
                     ["Sir Ynys Mon - Isle of Anglesey", "Isle of Anglesey County Council"],
                     ["Gwynedd - Gwynedd", "Gwynedd Council"],
                     ["Caerdydd - Cardiff", "Cardiff Council"],
                     ["Sir Ceredigion - Ceredigion", "Ceredigion County Council"],
                     ["Sir Fynwy - Monmouthshire", "Monmouthshire County Council"],
                     ["Sir Benfro - Pembrokeshire", "Pembrokeshire County Council"]]


def upgrade():
    op.add_column('organisation', sa.Column('scottish', sa.Boolean(), server_default=sa.false()))

    for authority in SCOTTISH_AUTHORITIES:
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = '{0}') THEN INSERT INTO organisation " \
                "(title, migrated, scottish, type_id) VALUES ('{0}', 'f', 't', 1); END IF; END $$;".format(
                    authority.replace("\'", "\'\'"))
        op.execute(query)
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation_name_mapping WHERE boundaries_name = '{0}') " \
                "THEN INSERT INTO organisation_name_mapping " \
                "(organisation_name, boundaries_name) VALUES ('{0}', '{0}'); END IF; END $$;".format(
                    authority.replace("\'", "\'\'"))
        op.execute(query)

    for authority in WELSH_AUTHORITIES:
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation WHERE title = '{0}') THEN INSERT INTO organisation " \
                "(title, migrated, scottish, type_id) VALUES ('{0}', 'f', 'f', 1); END IF; END $$;".format(
                    authority[1].replace("\'", "\'\'"))
        op.execute(query)
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM organisation_name_mapping WHERE boundaries_name = '{0}') " \
                "THEN INSERT INTO organisation_name_mapping " \
                "(organisation_name, boundaries_name) VALUES ('{0}', '{1}'); END IF; END $$;".format(
                    authority[1].replace("\'", "\'\'"), authority[0].replace("\'", "\'\'"))
        op.execute(query)


def downgrade():
    op.drop_column('organisation', 'scottish')

    for authority in SCOTTISH_AUTHORITIES:
        op.execute("DELETE FROM organisation_name_mapping WHERE organisation_name = '{0}';".format(
            authority.replace("\'", "\'\'")))
        op.execute("DELETE FROM organisation WHERE title = '{0}';".format(authority.replace("\'", "\'\'")))

    for authority in WELSH_AUTHORITIES:
        op.execute("DELETE FROM organisation_name_mapping WHERE organisation_name = '{0}';".format(
            authority[1].replace("\'", "\'\'")))
        op.execute("DELETE FROM organisation WHERE title = '{0}';".format(authority[1].replace("\'", "\'\'")))
