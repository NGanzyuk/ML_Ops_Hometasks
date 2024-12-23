import subprocess
import uuid

import mlflow
import pandas as pd
from sklearn.metrics import accuracy_score

from api.s3Service import S3Service
from database.db import DataBase
from models.model_factory import modelTypes, getModelType, loadModel


class Service:
    def __init__(self, databaseDsn=None):
        if databaseDsn is None:
            databaseDsn = "host='mydb' dbname='mydb' user='mydb' password='mydb'"
        self.db = DataBase(databaseDsn)
        self.s3_service = S3Service()

    def load_dataset(self, dataset_name: str) -> pd.DataFrame:
        subprocess.run(["dvc", "pull", dataset_name], check=True)
        return pd.read_csv(dataset_name)

    @staticmethod
    def getModelList() -> list:
        """Получить список всех возможных типов моделей."""
        return list(modelTypes.keys())

    def getModelInstances(self) -> list[dict]:
        """Получить информацию о всех обученных моделях."""
        return self.db.get_models()

    def modelRetrain(self, data: pd.DataFrame, target: list, modelName: str) -> str:
        """Переобучить модель на новых данных с использованием старых параметров."""
        modelDict = self.db.get_model(modelName)
        if modelDict is None:
            raise ValueError(f"Модель с именем '{modelName}' не найдена.")

        modelType = modelDict["type"]
        params = modelDict["params"]
        newModelName = str(uuid.uuid4())
        clfClass = getModelType(modelType)

        if clfClass is None:
            raise ValueError(f"Тип модели '{modelType}' не найден.")

        clf = clfClass(params)
        clf.fit(data, target)

        if not self.db.create_model(newModelName, modelType, params, clf.dumps()):
            raise Exception("Ошибка при создании модели в базе данных.")

        return newModelName

    def modelTrain(self, data: pd.DataFrame, target: list, modelType: str, params: dict) -> str:
        """Обучить модель с заданными параметрами и данными."""
        modelName = str(uuid.uuid4())
        clfClass = getModelType(modelType)
        if data is None:
            dataset = self.load_dataset("data/train.csv")
            target = dataset['target']
            data = dataset.drop('target')
        if clfClass is None:
            raise ValueError(f"Тип модели '{modelType}' не найден.")

        clf = clfClass(params)

        with mlflow.start_run():
            clf.fit(data, target)

            mlflow.log_param("model_type", modelType)
            mlflow.log_params(params)
            mlflow.log_metric("accuracy", self.evaluate_model(clf, data, target))
            mlflow.sklearn.log_model(clf, modelName)

        if not self.db.create_model(modelName, modelType, params, clf.dumps()):
            raise Exception("Ошибка при создании модели в базе данных.")

        return modelName

    def evaluate_model(self, model, data, target):
        return accuracy_score(target, model.predict(data))

    def getModel(self, data: pd.DataFrame, modelName: str) -> list:
        """Получить предсказания модели по идентификатору модели."""
        modelDict = self.db.get_model(modelName)
        if modelDict is None:
            raise ValueError(f"Модель с именем '{modelName}' не найдена.")

        clf = loadModel(modelDict["type"], modelDict["binary"])
        if clf is None:
            raise ValueError(f"Не удалось загрузить модель типа '{modelDict['type']}'.")

        predictions = clf.predict(data)
        return list(predictions)

    def deleteModel(self, modelName: str):
        """Удалить модель из базы данных по идентификатору модели."""
        if self.db.get_model(modelName) is None:
            raise ValueError(f"Модель с именем '{modelName}' не найдена.")

        self.db.delete_model(modelName)

    def upload_model_to_s3(self, model_name: str, model_binary: bytes):
        """Загрузка модели в S3."""
        file_name = f"{model_name}.model"
        with open(file_name, 'wb') as f:
            f.write(model_binary)
        self.s3_service.upload_file(file_name)

    def download_model_from_s3(self, model_name: str):
        """Скачивание модели из S3."""
        file_name = f"{model_name}.model"
        self.s3_service.download_file(file_name, file_name)
        with open(file_name, 'rb') as f:
            return f.read()
