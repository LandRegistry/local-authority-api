import unittest
from unittest.mock import patch
import mock
from shapely.geometry import shape as shapely_shape
from geoalchemy2 import shape
import json
from local_authority_api.main import app
from local_authority_api.models import Boundaries, Organisation

mock_boundary_data = json.dumps(
    {"crs": {"type": "name", "properties": {"name": "EPSG:27700"}}, "type": "Polygon",
     "coordinates": [[[0, 0], [1000, 0], [1000, 1000], [0, 1000], [0, 0]]]})

mock_boundary_data2 = json.dumps(
    {"crs": {"type": "name", "properties": {"name": "EPSG:27700"}}, "type": "Polygon",
     "coordinates": [[[2000, 2000], [3000, 2000], [3000, 3000], [2000, 3000], [2000, 2000]]]})


class TestLocalAuthority(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.jwt_patcher = patch("local_authority_api.app.validate")
        self.mock_jwt_validate = self.jwt_patcher.start()
        self.headers = {'Authorization': 'NOTAREALJWT'}

    def tearDown(self):
        self.jwt_patcher.stop()

    @mock.patch('local_authority_api.views.v1_0.local_authority.db.session')
    def test_bounding_box_notfound(self, mock_session):

        mock_session.query.return_value.join.return_value.filter.return_value.first \
            .return_value = None

        res = self.app.get('/v1.0/local-authorities/madeupname/bounding_box', headers=self.headers)
        self.assertEqual(res.status_code, 404)

    @mock.patch('local_authority_api.views.v1_0.local_authority.db.session')
    def test_bounding_box_found(self, mock_session):
        geo = {"coordinates": [[[472688.90390059707, 183461.40397461667],
                                [472688.90390059707, 209979.90313319373],
                                [492264.6989945782, 209979.90313319373],
                                [492264.6989945782, 183461.40397461667],
                                [472688.90390059707, 183461.40397461667]]],
               "type": "Polygon"}
        geo_shape = shapely_shape(geo)
        geometry = shape.from_shape(geo_shape, srid=27700)
        mock_session.query.return_value.join.return_value.filter.return_value.first \
            .return_value = [geometry]
        res = self.app.get('/v1.0/local-authorities/madeupname/bounding_box', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data.decode())['geometry'], geo)

    @mock.patch('local_authority_api.views.v1_0.local_authority.db.session')
    def test_bounding_box_exception(self, mock_session):
        mock_session.query.return_value.join.return_value.filter.return_value.first \
            .side_effect = Exception('test')
        res = self.app.get('/v1.0/local-authorities/madeupname/bounding_box', headers=self.headers)
        response_json = json.loads(res.get_data().decode("utf-8"))
        self.assertEqual(res.status_code, 500)
        self.assertEqual(response_json['error_message'],
                         'Failed to retrieve bounding box for '
                         'authority madeupname. Exception - test')

    @mock.patch('local_authority_api.views.v1_0.local_authority.db.session')
    def test_boundary_notfound(self, mock_session):
        mock_session.query.return_value.join.return_value.filter.return_value.first \
            .return_value = None
        res = self.app.get('/v1.0/local-authorities/madeupname/boundary', headers=self.headers)
        self.assertEqual(res.status_code, 404)

    @mock.patch('local_authority_api.views.v1_0.local_authority.db.session')
    def test_boundary_found(self, mock_session):
        geo = {"coordinates": [[[472688.90390059707, 183461.40397461667],
                                [472688.90390059707, 209979.90313319373],
                                [492264.6989945782, 209979.90313319373],
                                [492264.6989945782, 183461.40397461667],
                                [472688.90390059707, 183461.40397461667]]],
               "type": "Polygon"}
        geo_shape = shapely_shape(geo)
        geometry = shape.from_shape(geo_shape, srid=27700)
        mock_session.query.return_value.join.return_value.filter.return_value.first \
            .return_value = [geometry]
        res = self.app.get('/v1.0/local-authorities/madeupname/boundary', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data.decode())['geometry'], geo)

    @mock.patch('local_authority_api.views.v1_0.local_authority.db.session')
    def test_boundary_exception(self, mock_session):
        mock_session.query.return_value.join.return_value.filter.return_value.first \
            .side_effect = Exception('test')
        res = self.app.get('/v1.0/local-authorities/madeupname/boundary', headers=self.headers)
        response_json = json.loads(res.get_data().decode("utf-8"))
        self.assertEqual(res.status_code, 500)
        self.assertEqual(response_json['error_message'],
                         'Failed to retrieve the boundary for '
                         'authority madeupname. Exception - test')

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_authority_by_bounding_box(self, mock_org):
        mock_boundary_dict = json.loads(mock_boundary_data)
        mock_boundary = Boundaries()
        mock_boundary.geom = shape.from_shape(shapely_shape(mock_boundary_dict), srid=27700)
        org = Organisation("abc", True, 1, False, False, False, {"test": True}, None)
        org.boundary = mock_boundary
        orgs = [org]

        mock_org.query.\
            join.return_value.\
            filter.return_value. \
            filter.return_value. \
            all.return_value = orgs

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        res = self.app.post('/v1.0/local-authorities', data=mock_boundary_data, headers=headers)
        response_json = json.loads(res.get_data().decode("utf-8"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_json['abc'], True)

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_authority_by_bounding_box_multiples(self, mock_org):
        mock_boundary_dict = json.loads(mock_boundary_data)
        mock_boundary = Boundaries()
        mock_boundary.geom = shape.from_shape(shapely_shape(mock_boundary_dict), srid=27700)
        org1 = Organisation("abc", True, 1, False, False, False, {"test": True}, None)
        org2 = Organisation("def", False, 1, False, False, False, {"test": True}, None)
        org3 = Organisation("ghi", True, 1, False, False, False, {"test": True}, None)
        org1.boundary = mock_boundary
        org2.boundary = mock_boundary
        org3.boundary = mock_boundary
        orgs = [org1, org2, org3]

        mock_org.query.\
            join.return_value.\
            filter.return_value. \
            filter.return_value. \
            all.return_value = orgs

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        res = self.app.post('/v1.0/local-authorities', data=mock_boundary_data, headers=headers)
        response_json = json.loads(res.get_data().decode("utf-8"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_json['abc'], True)
        self.assertEqual(response_json['def'], False)
        self.assertEqual(response_json['ghi'], True)

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_authority_by_bounding_box_one_outside(self, mock_org):
        mock_boundary_dict = json.loads(mock_boundary_data)
        mock_boundary = Boundaries()
        mock_boundary.geom = shape.from_shape(shapely_shape(mock_boundary_dict), srid=27700)
        mock_boundary_dict2 = json.loads(mock_boundary_data2)
        mock_boundary2 = Boundaries()
        mock_boundary2.geom = shape.from_shape(shapely_shape(mock_boundary_dict2), srid=27700)

        org1 = Organisation("abc", True, 1, False, False, False, {"test": True}, None)
        org2 = Organisation("def", False, 1, False, False, False, {"test": True}, None)
        org3 = Organisation("ghi", True, 1, False, False, False, {"test": True}, None)
        org1.boundary = mock_boundary
        org2.boundary = mock_boundary
        org3.boundary = mock_boundary2
        orgs = [org1, org2, org3]

        mock_org.query.\
            join.return_value.\
            filter.return_value. \
            filter.return_value. \
            all.return_value = orgs

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        res = self.app.post('/v1.0/local-authorities', data=mock_boundary_data, headers=headers)
        response_json = json.loads(res.get_data().decode("utf-8"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(response_json['abc'], True)
        self.assertEqual(response_json['def'], False)
        self.assertNotIn('ghi', response_json)

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_authority_by_bounding_box_404(self, mock_org):

        orgs = []

        mock_org.query.\
            join.return_value.\
            filter.return_value. \
            filter.return_value. \
            all.return_value = orgs

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        res = self.app.post('/v1.0/local-authorities', data=mock_boundary_data, headers=headers)
        response_json = json.loads(res.get_data().decode("utf-8"))
        self.assertEqual(res.status_code, 404)
        self.assertEqual(response_json['error_message'], 'No authorities found')

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_authority_by_bounding_box_bad_request(self, mock_org):

        orgs = []

        mock_org.query.\
            join.return_value.\
            filter.return_value. \
            filter.return_value. \
            all.return_value = orgs

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        res = self.app.post('/v1.0/local-authorities', data=json.dumps({"abc": 123}), headers=headers)
        response_json = json.loads(res.get_data().decode("utf-8"))
        self.assertEqual(res.status_code, 400)
        self.assertEqual(response_json['error_message'], 'Bad request')

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_authority_by_bounding_box_500(self, mock_org):

        mock_org.query.\
            join.return_value.\
            filter.return_value. \
            filter.return_value. \
            all.side_effect = Exception('test')

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        res = self.app.post('/v1.0/local-authorities', data=mock_boundary_data, headers=headers)
        response_json = json.loads(res.get_data().decode("utf-8"))
        self.assertEqual(res.status_code, 500)
        self.assertIn('Exception - test', response_json['error_message'])

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_plus_minus_buffer_no_organisations(self, mock_organisation):
        organisations = []

        mock_organisation.query. \
            join.return_value. \
            filter.return_value. \
            filter.return_value. \
            filter.return_value. \
            all.return_value = organisations

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        response = self.app.post(
            '/v1.0/local-authorities/plus_minus_buffer',
            data=mock_boundary_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data().decode("utf-8")),
                         {'migrated_list': [],
                          'plus_buffer': {'non_migrated_list': [],
                                          'maintenance_list': [],
                                          'includes_scotland': False},
                          'minus_buffer': {'non_migrated_list': [],
                                           'maintenance_list': [],
                                           'includes_scotland': False}})

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_plus_minus_buffer_all_migrated(self, mock_organisation):
        organisations = [
            Organisation("some_title_1", True, 1, False, False, False, {"test": True}, None),
            Organisation("some_title_2", True, 1, False, False, False, {"test": True}, None)
        ]
        mock_boundary = Boundaries()
        mock_boundary.geom = shape.from_shape(shapely_shape(json.loads(mock_boundary_data)), srid=27700)
        organisations[0].boundary = mock_boundary
        organisations[1].boundary = mock_boundary

        mock_organisation.query. \
            join.return_value. \
            filter.return_value. \
            filter.return_value. \
            filter.return_value. \
            all.return_value = organisations

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        response = self.app.post(
            '/v1.0/local-authorities/plus_minus_buffer',
            data=mock_boundary_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data().decode("utf-8")),
                         {'migrated_list': ['some_title_1', 'some_title_2'],
                          'plus_buffer': {'non_migrated_list': [],
                                          'maintenance_list': [],
                                          'includes_scotland': False},
                          'minus_buffer': {'non_migrated_list': [],
                                           'maintenance_list': [],
                                           'includes_scotland': False}})

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_plus_minus_buffer_all_non_migrated(self, mock_organisation):
        organisations = [
            Organisation("some_title_1", False, 1, False, False, False, {"test": True}, None),
            Organisation("some_title_2", False, 1, False, False, False, {"test": True}, None)
        ]
        mock_boundary = Boundaries()
        mock_boundary.geom = shape.from_shape(shapely_shape(json.loads(mock_boundary_data)), srid=27700)
        organisations[0].boundary = mock_boundary
        organisations[1].boundary = mock_boundary

        mock_organisation.query. \
            join.return_value. \
            filter.return_value. \
            filter.return_value. \
            filter.return_value. \
            all.return_value = organisations

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        response = self.app.post(
            '/v1.0/local-authorities/plus_minus_buffer',
            data=mock_boundary_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data().decode("utf-8")),
                         {'migrated_list': [],
                          'plus_buffer': {'non_migrated_list': ['some_title_1', 'some_title_2'],
                                          'maintenance_list': [],
                                          'includes_scotland': False},
                          'minus_buffer': {'non_migrated_list': ['some_title_1', 'some_title_2'],
                                           'maintenance_list': [],
                                           'includes_scotland': False}})

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_plus_minus_buffer_all_non_migrated_scotland(self, mock_organisation):
        organisations = [
            Organisation("some_title_1", False, 1, False, True, False, {"test": True}, None),
            Organisation("some_title_2", False, 1, False, False, False, {"test": True}, None)
        ]
        mock_boundary = Boundaries()
        mock_boundary.geom = shape.from_shape(shapely_shape(json.loads(mock_boundary_data)), srid=27700)
        organisations[0].boundary = mock_boundary
        organisations[1].boundary = mock_boundary

        mock_organisation.query. \
            join.return_value. \
            filter.return_value. \
            filter.return_value. \
            filter.return_value. \
            all.return_value = organisations

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        response = self.app.post(
            '/v1.0/local-authorities/plus_minus_buffer',
            data=mock_boundary_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data().decode("utf-8")),
                         {'migrated_list': [],
                          'plus_buffer': {'non_migrated_list': ['some_title_2'],
                                          'maintenance_list': [],
                                          'includes_scotland': True},
                          'minus_buffer': {'non_migrated_list': ['some_title_2'],
                                           'maintenance_list': [],
                                           'includes_scotland': True}})

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_plus_minus_buffer_all_non_migrated_one_not_minus(self, mock_organisation):
        organisations = [
            Organisation("some_title_1", False, 1, False, False, False, {"test": True}, None),
            Organisation("some_title_2", False, 1, False, False, False, {"test": True}, None)
        ]
        mock_boundary = Boundaries()
        mock_boundary.geom = shape.from_shape(shapely_shape(json.loads(mock_boundary_data)), srid=27700)
        mock_boundary2 = Boundaries()
        mock_boundary2.geom = shape.from_shape(shapely_shape(json.loads(mock_boundary_data2)), srid=27700)
        organisations[0].boundary = mock_boundary
        organisations[1].boundary = mock_boundary2

        mock_organisation.query. \
            join.return_value. \
            filter.return_value. \
            filter.return_value. \
            filter.return_value. \
            all.return_value = organisations

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        response = self.app.post(
            '/v1.0/local-authorities/plus_minus_buffer',
            data=mock_boundary_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data().decode("utf-8")),
                         {'migrated_list': [],
                          'plus_buffer': {'non_migrated_list': ['some_title_1', 'some_title_2'],
                                          'maintenance_list': [],
                                          'includes_scotland': False},
                          'minus_buffer': {'non_migrated_list': ['some_title_1'],
                                           'maintenance_list': [],
                                           'includes_scotland': False}})

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_plus_minus_buffer_maintenance(self, mock_organisation):
        organisations = [
            Organisation("some_title_1", False, 1, False, False, False, {"test": True}, None),
            Organisation("some_title_2", False, 1, False, False, True, {"test": True}, None)
        ]
        mock_boundary = Boundaries()
        mock_boundary.geom = shape.from_shape(shapely_shape(json.loads(mock_boundary_data)), srid=27700)
        organisations[0].boundary = mock_boundary
        organisations[1].boundary = mock_boundary

        mock_organisation.query. \
            join.return_value. \
            filter.return_value. \
            filter.return_value. \
            filter.return_value. \
            all.return_value = organisations

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        response = self.app.post(
            '/v1.0/local-authorities/plus_minus_buffer',
            data=mock_boundary_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data().decode("utf-8")),
                         {'migrated_list': [],
                          'plus_buffer': {'non_migrated_list': ['some_title_1'],
                                          'maintenance_list': ['some_title_2'],
                                          'includes_scotland': False},
                          'minus_buffer': {'non_migrated_list': ['some_title_1'],
                                           'maintenance_list': ['some_title_2'],
                                           'includes_scotland': False}})

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_plus_minus_buffer_400(self, mock_organisation):
        mock_organisation.query. \
            join.return_value. \
            filter.return_value. \
            filter.return_value. \
            filter.return_value. \
            all.side_effect = ValueError()

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        response = self.app.post(
            '/v1.0/local-authorities/plus_minus_buffer',
            data=mock_boundary_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 400)

    @mock.patch('local_authority_api.views.v1_0.local_authority.Organisation')
    def test_plus_minus_buffer_500(self, mock_organisation):
        mock_organisation.query. \
            join.return_value. \
            filter.return_value. \
            filter.return_value. \
            filter.return_value. \
            all.side_effect = Exception()

        headers = self.headers
        headers['Content-Type'] = 'application/json'

        response = self.app.post(
            '/v1.0/local-authorities/plus_minus_buffer',
            data=mock_boundary_data,
            headers=headers
        )
        self.assertEqual(response.status_code, 500)
