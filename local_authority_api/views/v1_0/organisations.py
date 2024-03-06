from datetime import datetime
from flask import request, Blueprint, current_app, Response
from flask_negotiate import consumes
from jsonschema import validate, ValidationError
from sqlalchemy import false
from sqlalchemy.orm.attributes import flag_modified

from local_authority_api.exceptions import ApplicationError
from local_authority_api.extensions import db
from local_authority_api.models import UPDATE_ORGANISATION_SCHEMA, ORGANISATION_SOURCE_INFORMATION_SCHEMA, \
    Organisation, SourceInformation, UPDATE_ORGANISATION_NOTICE_SCHEMA, UPDATE_ORGANISATION_MAINTENANCE_SCHEMA
import json

organisations = Blueprint('organisations', __name__)


@organisations.route('', methods=['GET'])
def get_organisations():
    current_app.logger.info("Endpoint called - Retrieving organisations")
    try:
        current_app.logger.info("Retrieving organisation list from database")
        organisation_type = request.args.get('organisation_type')
        orgs_query = Organisation.query.distinct(Organisation.title).filter(Organisation.scottish == false())
        if organisation_type is None:
            # Exclude merged organisations by default
            orgs = orgs_query.filter(Organisation.type_id != 4).filter(Organisation.type_id != 5).all()
        elif organisation_type == 'la':
            orgs = orgs_query.filter(Organisation.type_id == 1).all()
        elif organisation_type == 'ooa':
            orgs = orgs_query.filter(Organisation.type_id == 2).all()
        elif organisation_type == 'sooa':
            orgs = orgs_query.filter(Organisation.type_id == 3).all()
        elif organisation_type == 'merged_la':
            orgs = orgs_query.filter(Organisation.type_id == 4).all()
        elif organisation_type == 'merged_ooa':
            orgs = orgs_query.filter(Organisation.type_id == 5).all()
        elif organisation_type == 'all':
            orgs = orgs_query.all()
        else:
            raise ApplicationError("Not a valid type, raising application error", "get-orgs-2", 400)
    except Exception as ex:
        error_message = 'Failed to retrieve the organisation list from database' \
            'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_ORGANISATIONS_FROM_DB')

    if not orgs:
        raise ApplicationError("No organisations found", "get-orgs-1", 404)

    current_app.logger.info("Organisations returned - Building response")

    organisation_details = list(map(lambda org: {
        'title': org.title.strip(),
        'migrated': org.migrated,
        'maintenance': org.maintenance,
        'historic_names': org.historic_names,
        'notice': org.notice,
        'type': org.type_id,
        'last_updated': org.last_updated.isoformat() if org.last_updated else None},
        orgs))

    return json.dumps(organisation_details), 200, {'Content-Type': 'application/json'}


@organisations.route('/<organisation>', methods=['GET'])
def get_latest_organisation_name(organisation):
    current_app.logger.info("Endpoint called - Retrieving latest organisation name for {}".format(organisation))
    try:
        org_query = Organisation.query.\
            filter(Organisation.historic_names.contains({'valid_names': [organisation]}))
        # We return the first found, so order by type ID so we normally get LA or OOA, unless we prefer merged
        if request.args.get("prefer_merged") == "true":
            org = org_query.order_by(Organisation.type_id.desc()).first()
        else:
            org = org_query.order_by(Organisation.type_id.asc()).first()
    except Exception as ex:
        error_message = 'Failed to retrieve the organisation from the database. ' \
            'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_ORGANISATION_FAILED')

    if not org:
        current_app.logger.info("Latest organisation name not found for - {}".format(organisation))
        raise ApplicationError("Organisation not found", "get-orgs-3", 404)
    else:
        org_name = org.title.strip()
        current_app.logger.info("Latest organisation name found - {}".format(org_name))

    organisation_details = {'title': org_name,
                            'migrated': org.migrated,
                            'maintenance': org.maintenance,
                            'historic_names': org.historic_names,
                            'notice': org.notice,
                            'last_updated': org.last_updated.isoformat() if org.last_updated else None,
                            'organisation_type': ['la', 'ooa', 'sooa', 'merged_la', 'merged_ooa'][org.type_id - 1]}

    return json.dumps(organisation_details), 200, {'Content-Type': 'application/json'}


@organisations.route('/add', methods=['POST'])
@consumes('application/json')
def add_organisation():
    payload = request.get_json()
    organisation = payload.get("title")
    org_type = payload.get("type")
    if not organisation:
        raise ApplicationError("Authority name not provided", "E101", 400)
    if not org_type:
        raise ApplicationError("Authority type not provided", "E102", 400)

    current_app.logger.info("Add organisation endpoint called with organisation: '{}' "
                            "and payload: {}".format(organisation, payload))

    try:
        existing_org = Organisation.query.\
            filter(Organisation.historic_names.contains({'valid_names': [organisation]}))\
            .filter(Organisation.type_id != 4).filter(Organisation.type_id != 5).first()
    except Exception as ex:
        error_message = 'Failed to retrieve the organisation from the database. ' \
            'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_ORGANISATION_FAILED', 500)

    if existing_org:
        current_app.logger.info("Organisation {} already exists".format(organisation))
        raise ApplicationError("Organisation already exists", "get-orgs-4", 400)
    else:
        if org_type == "sooa":
            type_code = 3
        else:
            type_code = 2
        org = Organisation(title=organisation,
                           migrated=False,
                           type_id=type_code,
                           notice=False,
                           scottish=False,
                           maintenance=False,
                           historic_names={"valid_names": [organisation]},
                           last_updated=datetime.now())
        db.session.add(org)
        db.session.commit()
        current_app.logger.info("Organisation added - {}".format(organisation))

    return Response()


@organisations.route('/edit', methods=['POST'])
@consumes('application/json')
def edit_organisation():
    payload = request.get_json()
    organisation = payload.get("title")
    new_title = payload.get("new_title")
    if not organisation:
        raise ApplicationError("Authority name not provided", "E103", 400)
    if not new_title:
        raise ApplicationError("New authority name not provided", "E104", 400)
    if organisation == new_title:
        raise ApplicationError("New and old name must not be the same", "E105", 400)

    current_app.logger.info("Edit organisation endpoint called with organisation: '{}' "
                            "and payload: {}".format(organisation, payload))

    try:
        historic_org = Organisation.query.\
            filter(Organisation.historic_names.contains({'valid_names': [new_title]})) \
            .filter(Organisation.type_id != 4).filter(Organisation.type_id != 5).first()
    except Exception as ex:
        error_message = 'Failed to retrieve the organisation from the database. ' \
            'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_ORGANISATION_FAILED', 500)

    if historic_org:
        # if org exists with this chosen name in the historic names, then the current title must be the old org name
        # i.e. you can only re-use a historic name of the same organisation
        historic_org_name = historic_org.title.strip()
        if historic_org_name != organisation:
            current_app.logger.info("Name {} already exists for organisation {}".format(new_title, historic_org_name))
            raise ApplicationError("New name already exists", "get-orgs-5", 400)
        else:
            historic_org.title = new_title
            historic_org.last_updated = datetime.now()
            db.session.commit()
    else:
        try:
            existing_org = Organisation.query. \
                filter(Organisation.title == organisation) \
                .first()
        except Exception as ex:
            error_message = 'Failed to retrieve the organisation from the database. ' \
                            'Exception - {}'.format(ex)
            current_app.logger.exception(error_message)
            raise ApplicationError(error_message, 'GET_ORGANISATION_FAILED', 500)

        if existing_org:
            existing_org.title = new_title
            # Add new display name to list of valid display names
            if new_title not in existing_org.historic_names["valid_names"]:
                existing_org.historic_names["valid_names"].append(new_title)
                # need to flag modified otherwise it won't update the jsonb column for some reason
                flag_modified(existing_org, "historic_names")
            existing_org.last_updated = datetime.now()
            db.session.commit()
        else:
            current_app.logger.info("Organisation not found for - {}".format(organisation))
            raise ApplicationError("Organisation not found", "get-orgs-3", 404)

    current_app.logger.info("Organisation {} renamed to {}".format(organisation, new_title))
    return Response()


@organisations.route('/<organisation>/migrated', methods=['PUT'])
@consumes('application/json')
def update_organisation_migrated(organisation):
    try:
        payload = request.get_json()
    except Exception as ex:
        error_message = 'Failed to get JSON payload. ' \
            'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_JSON_PAYLOAD_FAILED', 400)

    current_app.logger.info("Update organisation endpoint called with organisation: '{}' "
                            "and payload: {}".format(organisation, payload))

    try:
        validate(payload, UPDATE_ORGANISATION_SCHEMA)
    except ValidationError as e:
        error_message = "Payload failed validation. Exception: {}".format(e)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'UPDATE_ORGANISATION_MIGRATED_VALIDATION_ERROR', 400)

    try:
        organisation_db_object = db.session.query(Organisation).filter_by(title=organisation).first()
    except Exception as ex:
        error_message = 'Failed to retrieve the organisation from the database. ' \
            'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_ORGANISATION_FAILED')

    if not organisation_db_object:
        current_app.logger.info("Organisation '{}' not found".format(organisation))
        raise ApplicationError("Organisation '{}' not found".format(organisation), "S404", 404)
    else:
        current_app.logger.info("Organisation '{}' found, updating migrated status to '{}'"
                                .format(organisation, payload['migrated']))

        try:
            organisation_db_object.migrated = payload['migrated']
            db.session.commit()
        except Exception as ex:
            error_message = 'Failed to update the migrated field in the database. ' \
                'Exception - {}'.format(ex)
            current_app.logger.exception(error_message)
            raise ApplicationError(error_message, 'UPDATE_ORGANISATION_FAILED')

    return Response()


@organisations.route('/<organisation>/notice', methods=['PUT'])
@consumes('application/json')
def update_organisation_notice(organisation):
    try:
        payload = request.get_json()
    except Exception as ex:
        error_message = 'Failed to get JSON payload. ' \
                        'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_JSON_PAYLOAD_FAILED', 400)

    current_app.logger.info("Update organisation notice endpoint called with organisation: '{}' "
                            "and payload: {}".format(organisation, payload))

    try:
        validate(payload, UPDATE_ORGANISATION_NOTICE_SCHEMA)
    except ValidationError as e:
        error_message = "Payload failed validation. Exception: {}".format(e)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'UPDATE_ORGANISATION_NOTICE_SCHEMA_VALIDATION_ERROR', 400)

    try:
        organisation_db_object = db.session.query(Organisation).filter_by(title=organisation).first()
    except Exception as ex:
        error_message = 'Failed to retrieve the organisation from the database. ' \
                        'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_ORGANISATION_NOTICE_FAILED')

    if not organisation_db_object:
        current_app.logger.info("Organisation '{}' not found".format(organisation))
        raise ApplicationError("Organisation '{}' not found".format(organisation), "S404", 404)
    else:
        current_app.logger.info("Organisation '{}' found, updating notice status to '{}'"
                                .format(organisation, payload['notice']))

        try:
            organisation_db_object.notice = payload['notice']
            db.session.commit()
        except Exception as ex:
            error_message = 'Failed to update the notice field in the database. ' \
                            'Exception - {}'.format(ex)
            current_app.logger.exception(error_message)
            raise ApplicationError(error_message, 'UPDATE_ORGANISATION_NOTICE_FAILED')

    return Response()


@organisations.route('/<organisation>/maintenance', methods=['PUT'])
@consumes('application/json')
def update_organisation_maintenance(organisation):
    try:
        payload = request.get_json()
    except Exception as ex:
        error_message = 'Failed to get JSON payload. ' \
            'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_JSON_PAYLOAD_FAILED', 400)

    current_app.logger.info("Update organisation maintenance endpoint called with organisation: '{}' "
                            "and payload: {}".format(organisation, payload))

    try:
        validate(payload, UPDATE_ORGANISATION_MAINTENANCE_SCHEMA)
    except ValidationError as e:
        error_message = "Payload failed validation. Exception: {}".format(e)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'UPDATE_ORGANISATION_MAINTENANCE_VALIDATION_ERROR', 400)

    try:
        organisation_db_object = db.session.query(Organisation).filter_by(title=organisation).first()
    except Exception as ex:
        error_message = 'Failed to retrieve the organisation from the database. ' \
            'Exception - {}'.format(ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_ORGANISATION_FAILED')

    if not organisation_db_object:
        current_app.logger.info("Organisation '{}' not found".format(organisation))
        raise ApplicationError("Organisation '{}' not found".format(organisation), "S404", 404)
    else:
        current_app.logger.info("Organisation '{}' found, updating maintenance status to '{}'"
                                .format(organisation, payload['maintenance']))

        try:
            organisation_db_object.migrated = payload['maintenance']
            db.session.commit()
        except Exception as ex:
            error_message = 'Failed to update the maintenance field in the database. ' \
                'Exception - {}'.format(ex)
            current_app.logger.exception(error_message)
            raise ApplicationError(error_message, 'UPDATE_MAINTENANCE_FAILED')

    return Response()


@organisations.route('/<organisation>/source-information', methods=['GET'])
def get_organisation_source_information(organisation):
    current_app.logger.info("Endpoint called - Retrieving organisations source information")

    organisation_result = db.session.query(Organisation).filter_by(title=organisation).first()

    if not organisation_result:
        raise ApplicationError("Organisation '{}' not found".format(organisation), "S404", 404)

    source_information = []

    for source in organisation_result.source_information:
        source_information.append({'id': source.id, 'source-information': source.source_information})

    return json.dumps(source_information), 200, {'Content-Type': 'application/json'}


@organisations.route('/<organisation>/source-information', methods=['POST'])
@consumes('application/json')
def post_organisation_source_information(organisation):
    payload = request.get_json()

    try:
        validate(payload, ORGANISATION_SOURCE_INFORMATION_SCHEMA)
    except ValidationError as e:
        raise ApplicationError("Payload failed validation Exception: {}".format(e),
                               "ORGANISATION_SOURCE_INFORMATION_VALIDATION_ERROR", 422)

    organisation_result = db.session.query(Organisation).filter_by(title=organisation).first()

    if not organisation_result:
        raise ApplicationError("Organisation '{}' not found".format(organisation), "S404", 404)

    if len(organisation_result.source_information) >= int(current_app.config['SOURCE_INFORMATION_LIMIT']):
        raise ApplicationError("{} source information limit reached".format(organisation), "S400", 400)

    source_info = SourceInformation(source_information=payload.get('source-information'))

    organisation_result.source_information.append(source_info)
    db.session.commit()

    response = json.dumps({'id': source_info.id, 'source-information': source_info.source_information})

    return response, 201, {'Content-Type': 'application/json'}


@organisations.route('/<organisation>/source-information/<source_information_id>', methods=['PUT'])
@consumes('application/json')
def update_organisation_source_information(organisation, source_information_id):
    payload = request.get_json()

    try:
        validate(payload, ORGANISATION_SOURCE_INFORMATION_SCHEMA)
    except ValidationError as e:
        raise ApplicationError("Payload failed validation Exception: {}".format(e),
                               "ORGANISATION_SOURCE_INFORMATION_VALIDATION_ERROR", 422)

    new_source_information = payload.get('source-information')

    organisation_result = db.session.query(Organisation).filter_by(title=organisation).first()

    if not organisation_result:
        raise ApplicationError("Organisation '{}' not found".format(organisation), "S404", 404)

    source_info_result = db.session.query(SourceInformation).get(source_information_id)
    response_code = 200

    if source_info_result:
        if not source_info_result.organisation == organisation_result:
            raise ApplicationError("Source information '{}' does not belong to '{}'"
                                   .format(source_information_id, organisation), "S500", 500)

        source_info_result.source_information = new_source_information
    else:
        source_info = SourceInformation(id=source_information_id, source_information=new_source_information)
        source_info.organisation = organisation_result
        response_code = 201

    db.session.commit()

    response = json.dumps({'id': source_information_id, 'source-information': new_source_information})

    return response, response_code, {'Content-Type': 'application/json'}


@organisations.route('/<organisation>/source-information/<source_information_id>', methods=['DELETE'])
def delete_organisation_source_information(organisation, source_information_id):
    current_app.logger.info("Endpoint called - Deleting source information")

    organisation_result = db.session.query(Organisation).filter_by(title=organisation).first()

    if not organisation_result:
        raise ApplicationError("Organisation '{}' not found".format(organisation), "S404", 404)

    source_information = db.session.query(SourceInformation).get(source_information_id)

    if not source_information:
        raise ApplicationError("Source information '{}' not found".format(source_information_id), "S404", 404)

    if not source_information.organisation == organisation_result:
        raise ApplicationError("Source information '{}' does not belong to '{}'"
                               .format(source_information_id, organisation), "S500", 500)

    db.session.delete(source_information)
    db.session.commit()

    return "", 204
