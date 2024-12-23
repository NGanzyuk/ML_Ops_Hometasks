import unittest
from unittest.mock import MagicMock, patch
from api.service import Service


class TestService(unittest.TestCase):

    @patch('api.service.S3Service')
    @patch('api.service.DataBase')
    def setUp(self, mock_db, mock_s3_service):
        self.mock_s3_service = mock_s3_service.return_value
        self.service = Service()
        self.service.s3_service = self.mock_s3_service

    def test_upload_model_to_s3(self):
        model_name = 'test_model'
        model_binary = b'test_model_binary'
        self.mock_s3_service.upload_file = MagicMock()
        self.service.upload_model_to_s3(model_name, model_binary)
        expected_file_name = f"{model_name}.model"
        self.mock_s3_service.upload_file.assert_called_once_with(expected_file_name)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_download_model_from_s3(self, mock_open):
        model_name = 'test_model'
        mock_binary_data = b'test_model_binary'
        self.mock_s3_service.download_file = MagicMock(return_value=None)
        mock_open.return_value.read.return_value = mock_binary_data
        result = self.service.download_model_from_s3(model_name)
        expected_file_name = f"{model_name}.model"
        self.mock_s3_service.download_file.assert_called_once_with(expected_file_name, expected_file_name)
        self.assertEqual(result, mock_binary_data)
