import typing

from .base_model import BaseModel
from .catboost_classifier import CatBoostClassifierModel
from .logistic_regression import LogisticRegressionModel
from .xgboost_classifier import XGBoostClassifierModel

# Словарь для сопоставления типов моделей с их классами
modelTypes = {
    "catboost_classifier": CatBoostClassifierModel,
    "logistic_regression": LogisticRegressionModel,
    "xgboost_classifier": XGBoostClassifierModel,
}


def getModelType(modelType: str) -> typing.Optional[type[BaseModel]]:
    """
    Получить класс модели по её типу
    :param modelType: тип модели
    :return: класс модели
    """
    return modelTypes.get(modelType)


def loadModel(modelType: str, blob: bytes) -> typing.Optional[BaseModel]:
    """
    Загрузить бинарное представление модели по её типу
    :param modelType: тип модели
    :param blob: бинарное представление модели
    :return: загруженная (обученная) модель определённого типа
    """
    modelClass = modelTypes.get(modelType)
    return modelClass.loads(blob) if modelClass else None
