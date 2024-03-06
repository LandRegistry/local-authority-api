from unittest import TestCase
from unittest.mock import patch
import json
from local_authority_api.main import app
from local_authority_api.models import Organisation, SourceInformation
from flask import current_app


class TestOrganisationSourceInformation(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.jwt_patcher = patch("local_authority_api.app.validate")
        self.mock_jwt_validate = self.jwt_patcher.start()
        self.headers = {'Authorization': 'NOTAREALJWT'}
        self.mock_organisation = Organisation('Test Organisation 1', False, 1, False, False, False,
                                              {"valid_names": ["Test Organisation 1"]}, None)
        self.mock_organisation.source_information = [SourceInformation(id=1, source_information="test"),
                                                     SourceInformation(id=2, source_information="test2")]

    def tearDown(self):
        self.jwt_patcher.stop()

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_get_organisation_source_information(self, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = self.mock_organisation

        response = self.app.get("/v1.0/organisations/test/source-information", headers=self.headers)

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json,
                         [{"id": 1, "source-information": "test"}, {"id": 2, "source-information": "test2"}])

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_get_organisation_source_information_invalid_organisation(self, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None

        response = self.app.get("/v1.0/organisations/test/source-information", headers=self.headers)
        response_json = json.loads(response.get_data().decode("utf-8"))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['error_message'], "Organisation 'test' not found")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_post_organisation_source_information(self, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = self.mock_organisation

        response = self.app.post("/v1.0/organisations/test/source-information", headers=self.headers,
                                 data=json.dumps({"source-information": "test"}),
                                 content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['source-information'], "test")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_post_organisation_source_information_invalid_organisation(self, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None

        response = self.app.post("/v1.0/organisations/test/source-information", headers=self.headers,
                                 data=json.dumps({"source-information": "test"}),
                                 content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['error_message'], "Organisation 'test' not found")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_post_organisation_source_information_invalid(self, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = self.mock_organisation

        response = self.app.post("/v1.0/organisations/test/source-information", headers=self.headers,
                                 data=json.dumps({"information": "test"}),
                                 content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_json['error_code'], "ORGANISATION_SOURCE_INFORMATION_VALIDATION_ERROR")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_post_organisation_source_information_limit_reached(self, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = self.mock_organisation

        with app.app_context():
            current_app.config['SOURCE_INFORMATION_LIMIT'] = 2

        response = self.app.post("/v1.0/organisations/test-organisation/source-information", headers=self.headers,
                                 data=json.dumps({"source-information": "test"}),
                                 content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_json['error_message'], "test-organisation source information limit reached")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_update_organisation_source_information(self, mock_db):
        mock_organisation = Organisation('Test Organisation 1', False, 1, False, False, False,
                                         {"valid_names": ["Test Organisation 1"]}, None)
        mock_source_information = SourceInformation(id=1, source_information="Test")
        mock_source_information.organisation = mock_organisation

        mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_organisation
        mock_db.session.query.return_value.get.return_value = mock_source_information

        response = self.app.put("/v1.0/organisations/test/source-information/1",
                                headers=self.headers,
                                data=json.dumps({"source-information": "test update"}),
                                content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['id'], '1')
        self.assertEqual(response_json['source-information'], "test update")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_update_organisation_source_information_creates_when_not_exist(self, mock_db):
        mock_organisation = Organisation('Test Organisation 1', False, 1, False, False, False,
                                         {"valid_names": ["Test Organisation 1"]}, None)
        mock_source_information = SourceInformation(id=1, source_information="Test")
        mock_source_information.organisation = mock_organisation

        mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_organisation
        mock_db.session.query.return_value.get.return_value = None

        response = self.app.put("/v1.0/organisations/test/source-information/1",
                                headers=self.headers,
                                data=json.dumps({"source-information": "test update"}),
                                content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json['id'], '1')
        self.assertEqual(response_json['source-information'], "test update")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_update_organisation_source_information_invalid(self, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = self.mock_organisation

        response = self.app.put("/v1.0/organisations/test/source-information/1",
                                headers=self.headers,
                                data=json.dumps({"information": "test update"}),
                                content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_json['error_code'], "ORGANISATION_SOURCE_INFORMATION_VALIDATION_ERROR")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_update_organisation_source_information_invalid_organisation(self, mock_db):
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None

        response = self.app.put("/v1.0/organisations/test/source-information/1",
                                headers=self.headers,
                                data=json.dumps({"source-information": "test update"}),
                                content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['error_message'], "Organisation 'test' not found")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_update_organisation_source_information_wrong_organisation(self, mock_db):
        mock_source_information = SourceInformation(id=1, source_information="Test")
        mock_source_information.organisation = Organisation('Test Organisation 2', False, 1, False, False, False,
                                                            {"valid_names": ["Test Organisation 1"]}, None)

        mock_db.session.query.return_value.filter_by.return_value.first.return_value = self.mock_organisation
        mock_db.session.query.return_value.get.return_value = mock_source_information

        response = self.app.put("/v1.0/organisations/test-organisation/source-information/1",
                                headers=self.headers,
                                data=json.dumps({"source-information": "test update"}),
                                content_type='application/json')

        response_json = json.loads(response.get_data().decode("utf-8"))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response_json['error_message'],
                         "Source information '1' does not belong to 'test-organisation'")

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_delete_source_information_successful(self, mock_db):
        mock_source_information = SourceInformation(id=1, source_information='Test Source')
        mock_source_information.organisation = self.mock_organisation

        mock_db.session.query.return_value.get.return_value = mock_source_information
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = self.mock_organisation

        response = self.app.delete("/v1.0/organisations/{}/source-information/{}"
                                   .format(self.mock_organisation.title, mock_source_information.id),
                                   headers=self.headers)

        self.assertEqual(response.status_code, 204)

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_delete_source_information_not_found(self, mock_db):
        mock_source_information = SourceInformation(id=1, source_information='Test Source')
        mock_source_information.organisation = self.mock_organisation

        mock_db.session.query.return_value.get.return_value = None

        response = self.app.delete("/v1.0/organisations/{}/source-information/{}"
                                   .format(self.mock_organisation.title, mock_source_information.id),
                                   headers=self.headers)

        self.assertEqual(response.status_code, 404)

    @patch('local_authority_api.views.v1_0.organisations.db')
    def test_delete_source_information_organisation_not_matching(self, mock_db):
        mock_source_information = SourceInformation(id=1, source_information='Test Source')
        mock_source_information.organisation = self.mock_organisation
        mock_organisation2 = Organisation('Test Organisation 2', False, 1, False, False, False,
                                          {"valid_names": ["Test Organisation 1"]}, None)

        mock_db.session.query.return_value.get.return_value = mock_source_information
        mock_db.session.query.return_value.filter_by.return_value = mock_organisation2

        response = self.app.delete("/v1.0/organisations/{}/source-information/{}"
                                   .format(self.mock_organisation.title, mock_source_information.id),
                                   headers=self.headers)

        self.assertEqual(response.status_code, 500)
