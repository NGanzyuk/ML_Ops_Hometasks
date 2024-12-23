import abc

import pandas as pd


class BaseModel(abc.ABC):

    @abc.abstractmethod
    def fit(self, x: pd.DataFrame, y: list):
        pass

    @abc.abstractmethod
    def predict(self, x: pd.DataFrame):
        pass

    @abc.abstractmethod
    def dumps(self) -> bytes:
        pass

    @staticmethod
    @abc.abstractmethod
    def loads(blob: bytes):
        pass
