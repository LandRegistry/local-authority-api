"""add multiple alternate OOA names

Revision ID: 35cc07609395
Revises: 23c8f2667961
Create Date: 2021-11-22 11:38:01.252823

"""

# revision identifiers, used by Alembic.
revision = '35cc07609395'
down_revision = '23c8f2667961'

from alembic import op
import json

AUTH_NAMES = {
    "Anglian Water": ["Anglian Water", "Anglian Water Authority", "Anglian Water Services Ltd"],
    "Bromsgrove District Council": ["Bromsgrove District Council", "Bromsgrove District Council, Parkside, Market Street, Bromsgrove, B61 8DA"],
    "City of London Corporation": ["City f London", "City of London Corporation", "Corporation of London"],
    "City of Westminster": ["City of Westminster", "City of Westminster Council"],
    "Exolum Pipeline System Limited": ["Exolum Pipeline System", "Exolum Pipeline System Limited", "Fisher German"],
    "Council of the Isles of Scilly": ["Council of the Isles of Scilly", "Isles of Scilly Council"],
    "Secretary of State": ["Department for the Environment",
                           "Department for Transport",
                           "Department of Environment",
                           "Department of Environment & Transport",
                           "Department of Environment & Transport.",
                           "Department of Environment and Transport",
                           "Department of Environment, The Planning Inspectorate",
                           "Department of Environmental",
                           "Department of the Environment",
                           "Department of The Environment",
                           "Department of the Environment & Transport",
                           "Department of the Environment and Department of Transport",
                           "Department of the Environment and Transport",
                           "Department of the Environment and Transport.",
                           "Department of Transport",
                           "Departments of the Environment and Transport",
                           "Dept of Env & Trans",
                           "Dept of Environment & Transport",
                           "Dept of Evironment & Transport",
                           "Dept of the Environment",
                           "Dept of The Environment",
                           "Dept, of the Env.",
                           "Dept. of Env & Trans.",
                           "Dept. of Env. & Trans.",
                           "Dept. of the Env & Tran.",
                           "Dept. of the Env & Trans.",
                           "Dept. of The Env.",
                           "Dept. of the Env.",
                           "Dept. of the Env. & Transport.",
                           "Dept. of the Env. And Transport",
                           "Dept. of The Enviroment",
                           "Dept. of The Environment",
                           "Dept. of the Environment",
                           "Dept. of The Environment, Room 1404.",
                           "Dpeartment of the Environment",
                           "Dpet. Of Env. & Trans.",
                           "The Department of Environment",
                           "The Department of Transport Eastern Construction Programme",
                           "The Department of Transport Eastern Construction Programme Division",
                           "The Dept. of The Environment Room 1405",
                           "The Dept. of the Environment.",
                           "Government Office for London",
                           "Government Office for the West Midlands",
                           "Government Office for The West Midlands",
                           "Government Office for West Midlands",
                           "Home Office",
                           "Ministry of Civil Aviation, 19-29 Woburn Place, London, WC1",
                           "Ministry of Works",
                           "The Minister of Housing and Local Government"],
    "Environment Agency": ["The Environment Agency"],
    "Forestry Commission": ["Forest Enterprise", "Forestry Commission"],
    "Heart of England Housing Association Limited": ["Heart of England Housing Association"],
    "Historic England": ["English Heritage"],
    "High Speed Two (HS2) Limited": ["High Speed Tow (HS2) Limited", "High Speed Two (HS2)", "High Speed Two (HS2) Limited"],
    "London Borough of Enfield": ["Enfield London Borough Council"],
    "Natural England": ["English Nature",
                        "English Nature West Midlands Region",
                        "Nature Conservancy",
                        "Nature Conservancy Council",
                        "Nature Conservancy Council Foxhold House Thornfold Road Crookham Common Newbury Berks RG15 8EL"],
    "Northumbrian Water": ["Northumbrian Water Limited   https://www.nwl.co.uk/your-home.aspx"],
    "Nuneaton and Bedworth Borough Council": ["Nuneaton and Bedworth Borough  Council",
                                              "Nuneaton and Bedworth Borough Council",
                                              "Nuneaton and Bedworth District Council"],
    "Redditch Borough Council": ["Redditch Borough", "Redditch Borough Council"],
    "Runnymede Borough Council": ["Runnymede Borough Council."],
    "Severn Trent": ["Severn Trent Water", "Severn Trent Water Limited", "Severn Trent Water Ltd"],
    "South Hams District Council": ["Southam R.D.C",
                                    "Southam R.D.C. now part of Stratford-on-Avon District Council",
                                    "Southam R.D.C. Now part of Stratford-on-Avon District Council",
                                    "Southam Rural District Council"],
    "Southern Water": ["Southern Water Authority"],
    "Spelthorne Borough Council": ["Spelthorne Borough Council",
                                   "Staines Urban District Council",
                                   "Sunbury On Thames Urban District Council"],
    "Stratford-on-Avon District Council": ["Stratford on Avon Borough Council now forming part of Stratford-on-Avon District Council",
                                           "Stratford on Avon R.D.C. (now forming part of Stratford-on-Avon District Council)",
                                           "Stratford-on-Avon District Council",
                                           "Stratford-on-Avon District Council  Department of the Environment",
                                           "Stratford-on-Avon District Council and Department of Environment",
                                           "Stratford-on-Avon District Council and Department of Environment and Transport",
                                           "Stratford-on-Avon District Council and Department of the Environment",
                                           "Stratford-on-Avon District Council and Department of the Environment and Transport",
                                           "Stratford-on-Avon District Council and the Department of the Environment",
                                           "Stratford-on-Avon District Council Department of Environment and Transport",
                                           "Stratford-on-Avon District Council, Elizabeth House, Church Street, Stratford-upon-Avon, CV37 6HX",
                                           "Stratford-on-Avon District Council00",
                                           "Planning Department Stratford-on-Avon D.C Elizabeth House Church Street Stratford Upon Avon CV37 6HX",
                                           "Planning Department Stratford-on-Avon D.C."],
    "Warwickshire County Council": ["The Warwickshire County Council",
                                    "Warwickshire County",
                                    "Warwickshire County Council",
                                    "Warwickshire County Council & Stratford On Avon District Council",
                                    "Warwickshire County Council and Stratford-on-Avon District Council",
                                    "Warwickshire County Council Resources Group Law & Governance PO Box 9 Shire Hall Warwick",
                                    "Warwickshire County Council."],
    "Worcestershire County Council": ["Worcestershire County Council",
                                      "Worcestershire County Council, County Hall, Spetchley Road, Worcester WR5 2NP",
                                      "Worcestershire County Council, County Hall, Spetchley Road, Worcester, WR5 2NP"]
}


def upgrade():
    conn = op.get_bind()
    query = "SELECT title, historic_names FROM organisation;"
    res = conn.exec_driver_sql(query)
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Missing Organisations")

    for result in results:
        organisation_name = result[0]
        valid_names = result[1].get("valid_names")
        new_names = AUTH_NAMES.get(organisation_name)

        if new_names:
            for new_name in new_names:
                if new_name not in valid_names:
                    valid_names.append(new_name)

            historic_names = {"valid_names": valid_names}

            query = ("UPDATE organisation SET historic_names = '{0}' WHERE title = '{1}';".
                     format(json.dumps(historic_names), organisation_name))
            op.execute(query)


def downgrade():
    conn = op.get_bind()
    query = "SELECT title, historic_names FROM organisation;"
    res = conn.exec_driver_sql(query)
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Missing Organisations")

    for result in results:
        organisation_name = result[0]
        valid_names = result[1].get("valid_names")

        remove_names = AUTH_NAMES.get(organisation_name)

        if remove_names:
            for remove_name in remove_names:
                if remove_name in valid_names and remove_name != organisation_name:
                    # Do not remove the matching title name as this is still valid
                    valid_names.remove(remove_name)

            historic_names = {"valid_names": valid_names}

            query = ("UPDATE organisation SET historic_names = '{0}' WHERE title = '{1}';".
                     format(json.dumps(historic_names), organisation_name))
            op.execute(query)
