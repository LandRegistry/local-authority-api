from flask import Response, Blueprint, current_app, request
from local_authority_api.models import Boundaries, Organisation
from geoalchemy2 import shape
from local_authority_api.extensions import db
from local_authority_api.exceptions import ApplicationError
from shapely.geometry import mapping, shape as shapely_shape
from shapely.ops import unary_union
from shapely.validation import make_valid
from sqlalchemy import func
import json
from local_authority_api.config import BOUNDARY_BUFFER_IN_METERS
from enum import Enum

local_authority = Blueprint('local_authority', __name__)


class OrganisationTypes(Enum):
    Local_Authority = 1
    Other_Originating_Authority = 2
    Sensitive_Other_Originating_Authority = 3
    Merged_Local_Authority = 4
    Merged_Other_Originating_Authority = 5


@local_authority.route('/<local_authority>/bounding_box', methods=['GET'])
def local_authority_bounding_box(local_authority):
    current_app.logger.info("Endpoint called - Retrieving boundary for '{}'".format(local_authority))
    current_app.logger.info("Looking up stored name for authority with display name '{}'".format(local_authority))
    try:
        result = db.session.query(func.ST_Envelope(Boundaries.geom)).join(Organisation).filter(
            Organisation.title == local_authority).first()

    except Exception as ex:
        error_message = 'Failed to retrieve bounding box for authority {}. ' \
                        'Exception - {}'.format(local_authority, ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_BOUNDING_BOX_FOR_AUTHORITY')

    if not result or not result[0]:
        current_app.logger.warning("No bounding box found for authority '{}'".format(local_authority))
        raise ApplicationError("No bounding box  found for authority '{}'".format(local_authority), "L101", 404)

    bbox_json = mapping(shape.to_shape(result[0]))

    response_json = {
        "type": "Feature",
        "properties": {
            "local-authority-name": local_authority,
        },
        "geometry": bbox_json
    }

    current_app.logger.info("Boundary retrieved - Returning response")

    return Response(response=json.dumps(response_json), mimetype="application/json")


@local_authority.route('/<local_authority>/boundary', methods=['GET'])
def local_authority_boundary(local_authority):
    current_app.logger.info("Endpoint called - Retrieving boundary for '{}'".format(local_authority))
    current_app.logger.info("Looking up stored name for authority with display name '{}'".format(local_authority))
    try:
        result = db.session.query(Boundaries.geom).join(Organisation).filter(
            Organisation.title == local_authority).first()

    except Exception as ex:
        error_message = 'Failed to retrieve the boundary for authority {}. ' \
                        'Exception - {}'.format(local_authority, ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_BOUNDARY_FOR_AUTHORITY')

    if not result or not result[0]:
        current_app.logger.warning("No boundary found for authority '{}'".format(local_authority))
        raise ApplicationError("No boundary found for authority '{}'".format(local_authority), "L101", 404)

    boundary_json = mapping(shape.to_shape(result[0]))

    response_json = {
        "type": "Feature",
        "properties": {
            "local-authority-name": local_authority,
        },
        "geometry": boundary_json
    }

    current_app.logger.info("Boundary retrieved - Returning response")

    return Response(response=json.dumps(response_json), mimetype="application/json")


@local_authority.route('', methods=['POST'])
def local_authorities_by_bounding_box():
    current_app.logger.info("Get authorities by geometry proximity search")

    try:
        extent_shape = unary_union(make_valid(shapely_shape(request.get_json())))
        # Search only on minimum_rotated_rectangle since charge may be highly complex
        organisations = Organisation.query.join(Boundaries).filter(func.ST_DWithin(
            Boundaries.geom, shape.from_shape(extent_shape.minimum_rotated_rectangle, srid=27700),
            BOUNDARY_BUFFER_IN_METERS)) \
            .filter(Organisation.type_id == OrganisationTypes.Local_Authority.value) \
            .all()

        results = {}

        # Check boundaries that match minimum_rotated_rectangle match actual shape
        if organisations:
            for organisation in organisations:
                current_app.logger.debug("Checking {} boundaries".format(organisation.title))
                boundary_shape = shape.to_shape(organisation.boundary.geom)
                if extent_shape.intersects(boundary_shape.buffer(int(BOUNDARY_BUFFER_IN_METERS))):
                    current_app.logger.debug("Authority {} is within buffer distance".format(organisation.title))
                    results[organisation.title] = organisation.migrated

        if len(results.keys()) > 0:
            return Response(response=json.dumps(results), mimetype="application/json")

        raise ApplicationError("No authorities found", 'GET_AUTHORITIES_FOR_BOUNDING_BOX', 404)

    except AttributeError:
        raise ApplicationError("Bad request", 'GET_AUTHORITIES_FOR_BOUNDING_BOX', 400)
    except ApplicationError as ex:
        raise ex
    except Exception as ex:
        error_message = 'Failed to retrieve the authorities for request {}. ' \
                        'Exception - {}'.format(request.get_json(), ex)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'GET_AUTHORITIES_FOR_BOUNDING_BOX', 500)


@local_authority.route('/plus_minus_buffer', methods=['POST'])
def plus_minus_buffer():
    current_app.logger.info("Looking for authorities plus/minus buffer")

    try:
        extent_shape = unary_union(make_valid(shapely_shape(request.get_json())))
        geo_extent_shape = shape.from_shape(extent_shape, srid=27700)

        organisations = Organisation.query.join(Boundaries).filter(func.ST_DWithin(
            geo_extent_shape,
            Boundaries.geom,
            BOUNDARY_BUFFER_IN_METERS
        )).filter(Organisation.type_id != OrganisationTypes.Merged_Local_Authority.value) \
            .filter(Organisation.type_id != OrganisationTypes.Merged_Other_Originating_Authority.value).all()

        migrated_list = []
        plus_non_migrated_list = []
        plus_maintenance_list = []
        plus_scottish_list = []

        for org in organisations:
            if org.scottish:
                plus_scottish_list.append(org)
            elif org.maintenance:
                plus_maintenance_list.append(org)
            elif org.migrated:
                migrated_list.append(org)
            else:
                plus_non_migrated_list.append(org)

        minus_non_migrated_list = []
        minus_maintenance_list = []
        minus_scottish_list = []

        # Never interested in migrated minus buffer
        for org in (plus_non_migrated_list + plus_maintenance_list + plus_scottish_list):
            bound_minus_buf = shape.to_shape(org.boundary.geom).buffer(0 - int(BOUNDARY_BUFFER_IN_METERS))
            if extent_shape.intersects(bound_minus_buf):
                if org.scottish:
                    minus_scottish_list.append(org)
                elif org.maintenance:
                    minus_maintenance_list.append(org)
                else:
                    minus_non_migrated_list.append(org)

        response = {
            'migrated_list': org_list_strings(migrated_list),
            'plus_buffer': {
                'non_migrated_list': org_list_strings(plus_non_migrated_list),
                'maintenance_list': org_list_strings(plus_maintenance_list),
                'includes_scotland': len(plus_scottish_list) > 0
            },
            'minus_buffer': {
                'non_migrated_list': org_list_strings(minus_non_migrated_list),
                'maintenance_list': org_list_strings(minus_maintenance_list),
                'includes_scotland': len(minus_scottish_list) > 0
            }
        }

        current_app.logger.info("Returning plus/minus buffer response '{}'".format(response))
        return Response(json.dumps(response))

    except (ValueError, AttributeError):
        raise ApplicationError("Bad request", 'PLUS_MINUS_BUFFER', 400)

    except ApplicationError as exception:
        raise exception

    except Exception as exception:
        error_message = 'Failed to carry out plus/minus buffer check '
        'Exception - {}'.format(exception)
        current_app.logger.exception(error_message)
        raise ApplicationError(error_message, 'PLUS_MINUS_BUFFER', 500)


def org_list_strings(orgs):
    return [org.title for org in orgs]
