"""
Fertilizer Advisory Model
Input : Temparature (float), Humidity (float), Moisture (float %),
        Soil Type (str), Crop Type (str),
        Nitrogen (float), Potassium (float), Phosphorous (float)
Output: Fertilizer name string e.g. "Urea", "DAP"
Model : XGBoost classifier (fertilizer_recommendation.json)
PKL   : label_encoders (for Soil Type, Crop Type, Fertilizer Name), feature_columns

Soil Color → NPK Mapping (used when farmer doesn't know NPK):
  Black Soil  → N=80, P=40, K=40
  Red Soil    → N=20, P=15, K=35
  Alluvial    → N=60, P=45, K=80
  Sandy Soil  → N=15, P=10, K=20
  Clay Soil   → N=50, P=35, K=45
"""

import os
import pickle
import pandas as pd
from xgboost import XGBClassifier

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model")

SOIL_COLOR_NPK = {
    "Black Soil":   {"N": 80, "P": 40, "K": 40},
    "Red Soil":     {"N": 20, "P": 15, "K": 35},
    "Alluvial":     {"N": 60, "P": 45, "K": 80},
    "Sandy Soil":   {"N": 15, "P": 10, "K": 20},
    "Clay Soil":    {"N": 50, "P": 35, "K": 45},
}

CATEGORICAL_COLS = ["Soil Type", "Crop Type"]
TARGET_COL       = "Fertilizer Name"


class FertilizerAdvisor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self):
        if self._loaded:
            return
        model_path    = os.path.join(MODEL_DIR, "fertilizer_recommendation.json")
        artifact_path = os.path.join(MODEL_DIR, "fertilizer_recommendation.pkl")

        self.model = XGBClassifier()
        self.model.load_model(model_path)

        with open(artifact_path, "rb") as f:
            artifacts = pickle.load(f)

        self.label_encoders  = artifacts["label_encoders"]
        self.feature_columns = artifacts["feature_columns"]
        self._loaded = True
        print("[FertilizerAdvisor] Model loaded ✅")

    @staticmethod
    def npk_from_soil_color(color: str) -> dict:
        """Return NPK dict for a given soil color name."""
        return SOIL_COLOR_NPK.get(color, {"N": 40, "P": 30, "K": 40})

    def predict(
        self,
        temperature: float,
        humidity: float,
        moisture: float,
        soil_type: str,
        crop_type: str,
        nitrogen: float,
        potassium: float,
        phosphorous: float,
    ) -> str:
        """Returns the recommended fertilizer name."""
        row = {
            "Temparature":  temperature,
            "Humidity":     humidity,
            "Moisture":     moisture,
            "Soil Type":    soil_type,
            "Crop Type":    crop_type,
            "Nitrogen":     nitrogen,
            "Potassium":    potassium,
            "Phosphorous":  phosphorous,
        }
        # Label-encode categorical columns
        for col in CATEGORICAL_COLS:
            enc   = self.label_encoders[col]
            known = list(enc.classes_)
            val   = row[col] if row[col] in known else known[0]
            row[col] = int(enc.transform([val])[0])

        df         = pd.DataFrame([row])[self.feature_columns]
        pred_enc   = self.model.predict(df)[0]
        pred_label = self.label_encoders[TARGET_COL].inverse_transform([pred_enc])[0]
        return str(pred_label)


advisor = FertilizerAdvisor()
