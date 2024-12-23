import unittest
from unittest.mock import MagicMock, patch

from api.service import Service


class TestService(unittest.TestCase):
    """Класс для тестирования сервиса, взаимодействующего с S3 и базой данных."""

    @patch("api.service.S3Service")
    @patch("api.service.DataBase")
    def setUp(self, mock_db, mock_s3_service):
        """Настройка тестового окружения перед каждым тестом."""
        # Инициализация мок-объекта для S3Service
        self.mock_s3_service = mock_s3_service.return_value
        # Создание экземпляра сервиса
        self.service = Service()
        # Подмена s3_service на мок-объект
        self.service.s3_service = self.mock_s3_service

    def test_upload_model_to_s3(self):
        """Тестирование функции загрузки модели в S3."""
        model_name = "test_model"  # Имя модели
        model_binary = b"test_model_binary"  # Бинарные данные модели

        # Подмена метода upload_file на мок-объект
        self.mock_s3_service.upload_file = MagicMock()

        # Вызов метода загрузки модели
        self.service.upload_model_to_s3(model_name, model_binary)

        # Ожидаемое имя файла в S3
        expected_file_name = f"{model_name}.model"

        # Проверка, что метод upload_file был вызван с правильным именем файла
        self.mock_s3_service.upload_file.assert_called_once_with(expected_file_name)

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_download_model_from_s3(self, mock_open):
        """Тестирование функции загрузки модели из S3."""
        model_name = "test_model"  # Имя модели
        mock_binary_data = b"test_model_binary"  # Ожидаемые бинарные данные

        # Подмена метода download_file на мок-объект
        self.mock_s3_service.download_file = MagicMock(return_value=None)

        # Настройка mock_open для возврата ожидаемых бинарных данных
        mock_open.return_value.read.return_value = mock_binary_data

        # Вызов метода загрузки модели
        result = self.service.download_model_from_s3(model_name)

        # Ожидаемое имя файла в S3
        expected_file_name = f"{model_name}.model"

        # Проверка, что метод download_file был вызван с правильными параметрами
        self.mock_s3_service.download_file.assert_called_once_with(
            expected_file_name, expected_file_name
        )

        # Проверка, что результат соответствует ожидаемым бинарным данным
        self.assertEqual(result, mock_binary_data)
