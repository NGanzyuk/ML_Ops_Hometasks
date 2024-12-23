from __future__ import annotations

import tempfile

import catboost
import pandas as pd

from .base_model import BaseModel


class CatBoostClassifierModel(BaseModel):

    def __init__(self, params: dict | None = None, obj=None):
        super().__init__()
        self.clf = catboost.CatBoostClassifier(**params) if obj is None else obj

    def fit(self, x: pd.DataFrame, y: list):
        self.clf.fit(x, y)

    def predict(self, x: pd.DataFrame):
        return self.clf.predict_proba(x)[:, 1]

    def dumps(self) -> bytes:
        return self._saveModel(self.clf)

    @staticmethod
    def loads(blob: bytes):
        clf = catboost.CatBoostClassifier()
        clf.load_model(blob=blob)
        return CatBoostClassifierModel(obj=clf)

    @staticmethod
    def _saveModel(model) -> bytes:
        with tempfile.NamedTemporaryFile() as t:
            model.save_model(t.name)
            t.seek(0)
            return t.read()
