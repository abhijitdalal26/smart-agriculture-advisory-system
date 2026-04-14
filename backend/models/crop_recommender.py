"""
Crop Recommendation Model
Input : N, P, K (float), temperature (°C), humidity (%), ph, rainfall (mm)
Output: crop label string e.g. "rice", "maize"
Model : XGBoost classifier (crop_recommandation.json)
Encoder: LabelEncoder pkl  (crop_recommandation.pkl)
"""

import os
import joblib
import numpy as np
from xgboost import XGBClassifier

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model")


class CropRecommender:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self):
        if self._loaded:
            return
        model_path   = os.path.join(MODEL_DIR, "crop_recommandation.json")
        encoder_path = os.path.join(MODEL_DIR, "crop_recommandation.pkl")

        self.model = XGBClassifier()
        self.model.load_model(model_path)
        self.le = joblib.load(encoder_path)
        self._loaded = True
        print("[CropRecommender] Model loaded ✅")

    def predict(
        self,
        N: float, P: float, K: float,
        temperature: float, humidity: float,
        ph: float, rainfall: float
    ) -> str:
        """Returns the recommended crop name."""
        sample = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        pred_num  = self.model.predict(sample)
        pred_crop = self.le.inverse_transform(pred_num)
        return str(pred_crop[0])


# Singleton instance used by FastAPI
recommender = CropRecommender()
