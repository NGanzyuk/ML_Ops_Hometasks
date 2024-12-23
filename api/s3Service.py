import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class S3Service:
    def __init__(self):
        self.endpoint_url = os.getenv("S3_ENDPOINT_URL")
        self.access_key = os.getenv("S3_ACCESS_KEY")
        self.secret_key = os.getenv("S3_SECRET_KEY")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

        self.s3 = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

        self.create_bucket_if_not_exists()

    def create_bucket_if_not_exists(self):
        """Создание бакета, если он не существует."""
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            self.s3.create_bucket(Bucket=self.bucket_name)

    def upload_file(self, file_name, object_name=None):
        """Загрузка файла на S3."""
        if object_name is None:
            object_name = file_name
        try:
            self.s3.upload_file(file_name, self.bucket_name, object_name)
            print(f"Файл {file_name} загружен как {object_name} в {self.bucket_name}.")
        except FileNotFoundError:
            print(f"Файл {file_name} не найден.")
        except NoCredentialsError:
            print("Ошибка: отсутствуют учетные данные.")
        except ClientError as e:
            print(f"Ошибка при загрузке файла: {e}")

    def download_file(self, object_name, file_name):
        """Скачивание файла с S3."""
        try:
            self.s3.download_file(self.bucket_name, object_name, file_name)
            print(f"Файл {object_name} скачан как {file_name}.")
        except ClientError as e:
            print(f"Ошибка при скачивании файла: {e}")

    def list_files(self):
        """Список файлов в бакете."""
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            files = [obj["Key"] for obj in response.get("Contents", [])]
            return files
        except ClientError as e:
            print(f"Ошибка при получении списка файлов: {e}")
            return []
