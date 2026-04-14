"""
Yield Prediction Model
Input : state (str), crop (str), area (float, hectares), season (str)
Output: predicted yield (float, kg/hectare — same unit as training data)
Model : XGBoost regressor (crop_yield.json)
PKL   : feature_columns, dropped_columns, target_column
"""

import os
import pickle
import pandas as pd
from xgboost import XGBRegressor

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model")


class YieldPredictor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self):
        if self._loaded:
            return
        model_path    = os.path.join(MODEL_DIR, "crop_yield.json")
        artifact_path = os.path.join(MODEL_DIR, "crop_yield.pkl")

        self.model = XGBRegressor()
        self.model.load_model(model_path)

        with open(artifact_path, "rb") as f:
            artifacts = pickle.load(f)

        self.feature_columns  = artifacts["feature_columns"]
        self.dropped_columns  = artifacts["dropped_columns"]   # ['Crop_Year','Fertilizer','Production']
        self.target_column    = artifacts["target_column"]     # 'Yield'
        self._loaded = True
        print("[YieldPredictor] Model loaded ✅")

    def predict(
        self,
        state: str,
        crop: str,
        area: float,
        season: str = "Kharif"
    ) -> float:
        """
        Returns predicted yield (float).
        Builds a one-row DataFrame, one-hot encodes it,
        and aligns to training feature columns.
        """
        row = {
            "State_Name": state,
            "Crop":       crop,
            "Season":     season,
            "Area":       area,
        }
        df = pd.DataFrame([row])
        # One-hot encode categorical columns (same as training)
        categorical = df.select_dtypes(include=["object", "string"]).columns.tolist()
        df = pd.get_dummies(df, columns=categorical, drop_first=True)

        bool_cols = df.select_dtypes(include=["bool"]).columns
        if len(bool_cols):
            df[bool_cols] = df[bool_cols].astype(int)

        # Align columns to the training set (fill missing with 0)
        df = df.reindex(columns=self.feature_columns, fill_value=0)

        pred = self.model.predict(df)[0]
        return float(round(pred, 4))


predictor = YieldPredictor()
