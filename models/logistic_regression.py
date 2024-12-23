from __future__ import annotations

import pickle
import tempfile

import pandas as pd
from sklearn.linear_model import LogisticRegression

from .base_model import BaseModel


class LogisticRegressionModel(BaseModel):

    def __init__(self, params: dict | None = None, obj=None):
        super().__init__()
        self.clf = LogisticRegression(**params) if obj is None else obj

    def fit(self, x: pd.DataFrame, y: list):
        self.clf.fit(x, y)

    def predict(self, x: pd.DataFrame):
        return self.clf.predict_proba(x)[:, 1]

    def dumps(self) -> bytes:
        return self._saveModel(self.clf)

    @staticmethod
    def loads(blob: bytes):
        raise NotImplementedError(
            "Logistic Regression model does not support loading from bytes."
        )

    @staticmethod
    def _saveModel(model) -> bytes:
        with tempfile.NamedTemporaryFile() as t:
            pickle.dump(model, t)
            t.seek(0)
            return t.read()
