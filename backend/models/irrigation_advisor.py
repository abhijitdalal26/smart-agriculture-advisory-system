"""
Irrigation Need Model
Input : Soil_Type (str), Soil_pH (float), Soil_Moisture (float %),
        Temperature_C (float), Humidity (float %),
        Rainfall_mm (float), Wind_Speed_kmh (float),
        Season (str: Kharif/Rabi/Zaid), Region (str: North/South/Central/East/West)
Output: "Low" | "Medium" | "High"
Model : XGBoost multi-class classifier (irrigation_need.json)
PKL   : feature_label_encoders, target_encoder, feature_columns
"""

import os
import pickle
import pandas as pd
from xgboost import XGBClassifier

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model")


class IrrigationAdvisor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self):
        if self._loaded:
            return
        model_path    = os.path.join(MODEL_DIR, "irrigation_need.json")
        artifact_path = os.path.join(MODEL_DIR, "irrigation_need.pkl")

        self.model = XGBClassifier()
        self.model.load_model(model_path)

        with open(artifact_path, "rb") as f:
            artifacts = pickle.load(f)

        self.feature_label_encoders = artifacts["feature_label_encoders"]
        self.target_encoder         = artifacts["target_encoder"]
        self.feature_columns        = artifacts["feature_columns"]
        self._loaded = True
        print("[IrrigationAdvisor] Model loaded ✅")

    def predict(
        self,
        soil_type: str,
        soil_ph: float,
        soil_moisture: float,
        temperature: float,
        humidity: float,
        rainfall: float,
        wind_speed: float,
        season: str    = "Kharif",
        region: str    = "Central"
    ) -> str:
        """Returns 'Low', 'Medium', or 'High' irrigation need."""
        row = {
            "Soil_Type":      soil_type,
            "Soil_pH":        soil_ph,
            "Soil_Moisture":  soil_moisture,
            "Temperature_C":  temperature,
            "Humidity":       humidity,
            "Rainfall_mm":    rainfall,
            "Wind_Speed_kmh": wind_speed,
            "Season":         season,
            "Region":         region,
        }
        df = pd.DataFrame([row])

        # Label-encode categorical features using saved encoders
        for col, enc in self.feature_label_encoders.items():
            if col in df.columns:
                # Handle unseen labels gracefully
                known = list(enc.classes_)
                df[col] = df[col].apply(
                    lambda v: v if v in known else known[0]
                )
                df[col] = enc.transform(df[col])

        df = df.reindex(columns=self.feature_columns, fill_value=0)

        pred_enc    = self.model.predict(df)[0]
        pred_label  = self.target_encoder.inverse_transform([pred_enc])[0]
        return str(pred_label)


advisor = IrrigationAdvisor()
