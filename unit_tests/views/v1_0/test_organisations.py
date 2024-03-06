from unittest import TestCase
from unittest.mock import patch
import json
from jsonschema import ValidationError
from local_authority_api.main import app
from local_authority_api.models import Organisation

mock_organisation_1 = Organisation('Test Organisation 1', False, 1, False, False, False,
                                   {"valid_names": ["Test Organisation 1", "Old name 1"]}, None)
mock_organisation_2 = Organisation('Test Organisation 2', False, 1, False, False, False,
                                   {"valid_names": ["Test Organisation 2"]}, None)
mock_organisation_3 = Organisation('Test Organisation 3', False, 1, False, False, False,
                                   {"valid_names": ["Test Organisation 3"]}, None)
mock_organisation_4 = Organisation('Test Organisation 4', False, 2, False, False, False,
                                   {"valid_names": ["Test Organisation 4"]}, None)
mock_organisation_5 = Organisation('Test Sensitive Organisation 5', False, 3, False, False, False,
                                   {"valid_names": ["Test Sensitive Organisation 5"]}, None)


mock_organisation_list = [
    mock_organisation_1,
    mock_organisation_2,
    mock_organisation_3,
    mock_organisation_4,
    mock_organisation_5
]


class TestOrganisations(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.jwt_patcher = patch("local_authority_api.app.validate")
        self.mock_jwt_validate = self.jwt_patcher.start()
        self.headers = {'Authorization': 'NOTAREALJWT'}

    def tearDown(self):
        self.jwt_patcher.stop()

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    def test_get_ooa_organisations(self, mock_organisation):
        mock_organisation.query.distinct.return_value.filter.return_value.filter.return_value.all.return_value = \
            [mock_organisation_4]
        get_response = self.app.get("/v1.0/organisations",
                                    headers=self.headers,
                                    query_string={'organisation_type': 'ooa'})
        response_json = json.loads(get_response.get_data().decode("utf-8"))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(response_json), 1)
        self.assertEqual(
            {"title": "Test Organisation 4",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Organisation 4"]},
             "type": 2}, response_json[0]
        )

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    def test_get_la_organisations(self, mock_organisation):
        mock_organisation.query.distinct.return_value.filter.return_value.filter.return_value.all.return_value = \
            [mock_organisation_1, mock_organisation_2, mock_organisation_3]
        get_response = self.app.get("/v1.0/organisations", headers=self.headers,
                                    query_string={'organisation_type': 'la'})
        response_json = json.loads(get_response.get_data().decode("utf-8"))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(response_json), 3)
        self.assertEqual(
            {"title": "Test Organisation 1",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Organisation 1", "Old name 1"]},
             "type": 1}, response_json[0]
        )
        self.assertEqual(
            {"title": "Test Organisation 2",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Organisation 2"]},
             "type": 1}, response_json[1]
        )
        self.assertEqual(
            {"title": "Test Organisation 3",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Organisation 3"]},
             "type": 1}, response_json[2]
        )

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    def test_get_sooa_organisations(self, mock_organisation):
        mock_organisation.query.distinct.return_value.filter.return_value.filter.return_value.all.return_value = \
            [mock_organisation_5]
        get_response = self.app.get("/v1.0/organisations",
                                    headers=self.headers,
                                    query_string={'organisation_type': 'sooa'})
        response_json = json.loads(get_response.get_data().decode("utf-8"))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(response_json), 1)
        self.assertEqual(
            {"title": "Test Sensitive Organisation 5",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Sensitive Organisation 5"]},
             "type": 3}, response_json[0]
        )

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    def test_get_all_organisations(self, mock_organisation):
        mock_organisation.query.distinct.return_value.filter.return_value.filter.return_value.filter.return_value \
            .all.return_value = mock_organisation_list

        get_response = self.app.get("/v1.0/organisations", headers=self.headers)
        response_json = json.loads(get_response.get_data().decode("utf-8"))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(response_json), 5)
        self.assertEqual(
            {"title": "Test Organisation 1",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Organisation 1", "Old name 1"]},
             "type": 1}, response_json[0]
        )
        self.assertEqual(
            {"title": "Test Organisation 2",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Organisation 2"]},
             "type": 1}, response_json[1]
        )
        self.assertEqual(
            {"title": "Test Organisation 3",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Organisation 3"]},
             "type": 1}, response_json[2]
        )
        self.assertEqual(
            {"title": "Test Organisation 4",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Organisation 4"]},
             "type": 2}, response_json[3]
        )
        self.assertEqual(
            {"title": "Test Sensitive Organisation 5",
             "migrated": False,
             "maintenance": False,
             "notice": False,
             'last_updated': None,
             "historic_names": {"valid_names": ["Test Sensitive Organisation 5"]},
             "type": 3}, response_json[4]
        )

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    def test_get_latest_organisation_name(self, mock_organisation):
        mock_organisation.query.filter.return_value.order_by.return_value.first.return_value = mock_organisation_1

        get_response = self.app.get("/v1.0/organisations/Old name 1", headers=self.headers)
        response_json = json.loads(get_response.get_data().decode("utf-8"))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual({'historic_names': {'valid_names': ['Test Organisation 1', 'Old name 1']},
                          'maintenance': False,
                          'migrated': False,
                          "notice": False,
                          'last_updated': None,
                          'organisation_type': 'la',
                          'title': 'Test Organisation 1'}, response_json)

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    def test_get_latest_organisation_name_not_found(self, mock_organisation):
        mock_organisation.query.filter.return_value.order_by.return_value.first.return_value = None

        get_response = self.app.get("/v1.0/organisations/Mock name", headers=self.headers)
        json.loads(get_response.get_data().decode("utf-8"))
        self.assertEqual(get_response.status_code, 404)

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    def test_get_organisations_not_found(self, mock_organisation):
        mock_organisation.query.distinct.return_value.filter.return_value.filter.return_value.filter.return_value \
            .all.return_value = []

        get_response = self.app.get("/v1.0/organisations", headers=self.headers)
        self.assertEqual(get_response.status_code, 404)

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    def test_get_organisations_exception(self, mock_organisation):
        mock_organisation.query.distinct.return_value.filter.return_value = Exception('test exception')

        get_response = self.app.get("/v1.0/organisations", headers=self.headers)
        self.assertEqual(get_response.status_code, 500)

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_add_organisation(self, mock_db_session, mock_organisation):
        mock_organisation.query.filter.return_value.filter.return_value.filter.return_value.first.return_value = None
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        org_name = "test authority"
        org_type = "ooa"
        org_type_code = 2

        test_org = Organisation(title=org_name,
                                migrated=False,
                                type_id=org_type_code,
                                notice=False,
                                scottish=False,
                                maintenance=False,
                                historic_names={"valid_names": [org_name]},
                                last_updated=None)
        mock_organisation.return_value = test_org

        payload = json.dumps({"title": org_name,
                              "type": org_type})

        response = self.app.post("/v1.0/organisations/add", headers=headers,
                                 data=payload)

        self.assertEqual(response.status_code, 200)
        mock_db_session.add.assert_called_with(test_org)

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_add_sooa_organisation(self, mock_db_session, mock_organisation):
        mock_organisation.query.filter.return_value.filter.return_value.filter.return_value.first.return_value = None
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        org_name = "test authority"
        org_type = "sooa"
        org_type_code = 3

        test_org = Organisation(title=org_name,
                                migrated=False,
                                type_id=org_type_code,
                                notice=False,
                                scottish=False,
                                maintenance=False,
                                historic_names={"valid_names": [org_name]},
                                last_updated=None)
        mock_organisation.return_value = test_org

        payload = json.dumps({"title": org_name,
                              "type": org_type})

        response = self.app.post("/v1.0/organisations/add", headers=headers,
                                 data=payload)

        self.assertEqual(response.status_code, 200)
        mock_db_session.add.assert_called_with(test_org)

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_add_organisation_no_name(self, mock_db_session, mock_organisation):
        mock_organisation.query.filter.return_value.filter.return_value.filter.return_value.first.return_value = None
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        org_type = "ooa"

        payload = json.dumps({"type": org_type})

        response = self.app.post("/v1.0/organisations/add", headers=headers,
                                 data=payload)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Authority name not provided',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_add_organisation_no_type(self, mock_db_session, mock_organisation):
        mock_organisation.query.filter.return_value.filter.return_value.filter.return_value.first.return_value = None
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        org_name = "test authority"

        payload = json.dumps({"title": org_name})

        response = self.app.post("/v1.0/organisations/add", headers=headers,
                                 data=payload)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Authority type not provided',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_add_organisation_already_exists(self, mock_db_session, mock_organisation):
        mock_organisation.query.filter.return_value.first.return_value = mock_organisation_1
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        org_name = "test authority"
        org_type = "ooa"

        payload = json.dumps({"title": org_name,
                              "type": org_type})

        response = self.app.post("/v1.0/organisations/add", headers=headers,
                                 data=payload)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("Organisation already exists",
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_edit_organisation(self, mock_db_session, mock_organisation):
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        org_name = "test authority"
        new_org_name = "new test authority"

        test_org = Organisation(title=org_name,
                                migrated=False,
                                type_id=2,
                                notice=False,
                                scottish=False,
                                maintenance=False,
                                historic_names={"valid_names": [org_name]},
                                last_updated=None)
        mock_organisation.query.filter.return_value.filter.return_value.filter.return_value.first.return_value = None
        mock_organisation.query.filter.return_value.first.return_value = test_org

        payload = json.dumps({"title": org_name,
                              "new_title": new_org_name})

        response = self.app.post("/v1.0/organisations/edit", headers=headers,
                                 data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_org.title, new_org_name)
        self.assertEqual(test_org.historic_names['valid_names'], [org_name, new_org_name])
        mock_db_session.commit.assert_called()

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_edit_organisation_no_name(self, mock_db_session, mock_organisation):
        mock_organisation.query.filter.return_value.first.return_value = None
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        payload = json.dumps({"new_title": "new test authority"})

        response = self.app.post("/v1.0/organisations/edit", headers=headers,
                                 data=payload)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Authority name not provided',
                      response_json['error_message'])
        mock_db_session.commit.assert_not_called()

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_edit_organisation_no_new_name(self, mock_db_session, mock_organisation):
        mock_organisation.query.filter.return_value.first.return_value = None
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        payload = json.dumps({"title": "test authority"})

        response = self.app.post("/v1.0/organisations/edit", headers=headers,
                                 data=payload)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('New authority name not provided',
                      response_json['error_message'])
        mock_db_session.commit.assert_not_called()

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_edit_organisation_names_equal(self, mock_db_session, mock_organisation):
        mock_organisation.query.filter.return_value.first.return_value = None
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        payload = json.dumps({"title": "test authority",
                              "new_title": "test authority"})

        response = self.app.post("/v1.0/organisations/edit", headers=headers,
                                 data=payload)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('New and old name must not be the same',
                      response_json['error_message'])
        mock_db_session.commit.assert_not_called()

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_edit_organisation_historic_org_exists_ok(self, mock_db_session, mock_organisation):
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        org_name = "test authority"
        new_org_name = "new test authority"

        test_org = Organisation(title=org_name,
                                migrated=False,
                                type_id=2,
                                notice=False,
                                scottish=False,
                                maintenance=False,
                                historic_names={"valid_names": [org_name, new_org_name]},
                                last_updated=None)
        mock_organisation.query.filter.return_value.filter.return_value.filter.return_value.first.side_effect = \
            [test_org]

        payload = json.dumps({"title": org_name,
                              "new_title": new_org_name})

        response = self.app.post("/v1.0/organisations/edit", headers=headers,
                                 data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_org.title, new_org_name)
        self.assertEqual(test_org.historic_names['valid_names'], [org_name, new_org_name])
        mock_db_session.commit.assert_called()

    @patch('local_authority_api.views.v1_0.organisations.Organisation')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_edit_organisation_historic_org_exists_bad(self, mock_db_session, mock_organisation):
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        org_name = "test authority"
        new_org_name = "new test authority"
        different_org_name = "a totally different org"

        test_org = Organisation(title=different_org_name,
                                migrated=False,
                                type_id=2,
                                notice=False,
                                scottish=False,
                                maintenance=False,
                                historic_names={"valid_names": [different_org_name, new_org_name]},
                                last_updated=None)
        mock_organisation.query.filter.return_value.first.side_effect = [test_org]

        payload = json.dumps({"title": org_name,
                              "new_title": new_org_name})

        self.app.post("/v1.0/organisations/edit", headers=headers,
                      data=payload)

        mock_db_session.commit.assert_not_called()

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_migrated_success(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_organisation_1
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/migrated", headers=headers,
                                data=json.dumps({'migrated': True}))

        self.assertEqual(response.status_code, 200)

    @patch('local_authority_api.views.v1_0.organisations.validate')
    def test_update_organisation_migrated_no_payload(self, mock_validate):
        mock_validate.return_value = True

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/migrated", headers=headers)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Failed to get JSON payload',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    def test_update_organisation_migrated_validation_failure(self, mock_validate):
        mock_validate.side_effect = ValidationError('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/migrated", headers=headers,
                                data=json.dumps({'migrated': 'asdf'}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Payload failed validation',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_migrated_organisation_not_found(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/migrated", headers=headers,
                                data=json.dumps({'migrated': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Organisation \'test\' not found',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_migrated_db_read_exception(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.side_effect = Exception('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/migrated", headers=headers,
                                data=json.dumps({'migrated': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failed to retrieve the organisation from the database',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_migrated_db_update_exception(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_organisation_1
        mock_db_session.commit.side_effect = Exception('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/migrated", headers=headers,
                                data=json.dumps({'migrated': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failed to update the migrated field in the database.',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_notice_success(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_organisation_1
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/notice", headers=headers,
                                data=json.dumps({'notice': True}))

        self.assertEqual(response.status_code, 200)

    @patch('local_authority_api.views.v1_0.organisations.validate')
    def test_update_organisation_notice_no_payload(self, mock_validate):
        mock_validate.return_value = True

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/notice", headers=headers)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Failed to get JSON payload',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    def test_update_organisation_notice_validation_failure(self, mock_validate):
        mock_validate.side_effect = ValidationError('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/notice", headers=headers,
                                data=json.dumps({'notice': 'asdf'}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Payload failed validation',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_notice_organisation_not_found(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/notice", headers=headers,
                                data=json.dumps({'notice': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Organisation \'test\' not found',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_notice_db_read_exception(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.side_effect = Exception('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/notice", headers=headers,
                                data=json.dumps({'notice': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failed to retrieve the organisation from the database',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_notice_db_update_exception(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_organisation_1
        mock_db_session.commit.side_effect = Exception('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/notice", headers=headers,
                                data=json.dumps({'notice': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failed to update the notice field in the database.',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_maintenance_success(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_organisation_1
        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/maintenance", headers=headers,
                                data=json.dumps({'maintenance': True}))

        self.assertEqual(response.status_code, 200)

    @patch('local_authority_api.views.v1_0.organisations.validate')
    def test_update_organisation_maintenance_no_payload(self, mock_validate):
        mock_validate.return_value = True

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/maintenance", headers=headers)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Failed to get JSON payload',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    def test_update_organisation_maintenance_validation_failure(self, mock_validate):
        mock_validate.side_effect = ValidationError('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/maintenance", headers=headers,
                                data=json.dumps({'maintenance': 'asdf'}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Payload failed validation',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_maintenance_organisation_not_found(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/maintenance", headers=headers,
                                data=json.dumps({'maintenance': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self.assertIn('Organisation \'test\' not found',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_maintenance_db_read_exception(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.side_effect = Exception('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/maintenance", headers=headers,
                                data=json.dumps({'maintenance': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failed to retrieve the organisation from the database',
                      response_json['error_message'])

    @patch('local_authority_api.views.v1_0.organisations.validate')
    @patch('local_authority_api.views.v1_0.organisations.db.session')
    def test_update_organisation_maintenance_db_update_exception(self, mock_db_session, mock_validate):
        mock_validate.return_value = True
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_organisation_1
        mock_db_session.commit.side_effect = Exception('test')

        headers = dict(self.headers)
        headers.update({'Content-Type': 'application/json'})

        response = self.app.put("/v1.0/organisations/test/maintenance", headers=headers,
                                data=json.dumps({'maintenance': True}))

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 500)
        self.assertIn('Failed to update the maintenance field in the database.',
                      response_json['error_message'])
