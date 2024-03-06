from local_authority_api.alembic_utils.shapefile_loader import load_shapefile
import unittest
from unittest.mock import patch, MagicMock, call


class TestShapefileLoader(unittest.TestCase):

    @patch('local_authority_api.alembic_utils.shapefile_loader.Popen')
    def test_load_shapefile_ok(self, mock_popen):
        mock_op = MagicMock()
        mock_client_encoding = [['clientencoding']]
        mock_standard_conforming_strings = [['standardconformingstrings']]
        mock_op.get_bind.return_value.exec_driver_sql.return_value.fetchall.side_effect = \
            [mock_client_encoding, mock_standard_conforming_strings]
        mock_popen.return_value.stdout.readline.return_value.decode.side_effect = \
            ["blah;\n", "blah2;\n", "blah3;\n", ""]
        mock_popen.return_value.poll.side_effect = [None, None, None, 0, 0]
        load_shapefile(mock_op, "ashapefile", "atable")

        mock_op.execute.assert_has_calls([call("blah;\n"), call("blah2;\n"), call("blah3;\n"),
                                          call("SET client_encoding TO clientencoding"),
                                          call("SET standard_conforming_strings TO standardconformingstrings")])

    @patch('local_authority_api.alembic_utils.shapefile_loader.Popen')
    def test_load_shapefile_exception(self, mock_popen):
        mock_op = MagicMock()
        mock_client_encoding = [['clientencoding']]
        mock_standard_conforming_strings = [['standardconformingstrings']]
        mock_op.get_bind.return_value.execute.return_value.fetchall.side_effect = \
            [mock_client_encoding, mock_standard_conforming_strings]
        mock_popen.return_value.stdout.readline.return_value.decode.side_effect = \
            ["blah;\n", "blah2;\n", "blah3;\n", ""]
        mock_popen.return_value.poll.side_effect = [None, None, None, 1, 1, 1]

        with self.assertRaisesRegex(Exception, "shp2pgsql command failed with exit code 1"):
            load_shapefile(mock_op, "ashapefile", "atable")
