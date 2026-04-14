# Machine Learning Models

KrishiMitra includes four distinct machine learning pipelines, all utilizing **XGBoost**. The system employs a local inference approach without relying on cloud computation for predictive inputs, reducing latency and allowing edge-case offline operability.

The models are pre-trained on regional Indian datasets and deployed as paired files: `model_name.json` for the XGBoost core algorithm, and `model_name.pkl` for data preprocessing metadata (such as `LabelEncoder` objects and categorical column configurations).

## 1. Crop Recommender (`CropRecommender`)
- **Classifier:** XGBoost Classifier
- **Goal:** Predicts the best crop to plant based on soil nutrient profile and immediate local weather conditions.
- **Inputs:**
  - `N`, `P`, `K` (Nitrogen, Phosphorous, Potassium)
  - `temperature` (°C)
  - `humidity` (%)
  - `ph` (Soil pH)
  - `rainfall` (mm in last 24h)
- **Output:** Categorical string (e.g., `wheat`, `rice`, `cotton`). It requires a `.pkl` label encoder to inverse-transform the boolean classification.

## 2. Yield Predictor (`YieldPredictor`)
- **Classifier:** XGBoost Regressor
- **Goal:** Forecast expected crop harvests to support economic planning.
- **Inputs:**
  - `State_Name` (Categorical, automatically handled by IP Geolocation)
  - `Crop_Type` (Categorical, what is currently planted)
  - `Area` (Numerical, size of farm in hectares)
  - `Season` (Categorical, extracted globally from current month)
- **Output:** Yield in kg/hectare. The system UI transforms this to tonnes/acre for simpler farmer readability.
- **Implementation Note:** Requires complex One-Hot Encoding via pandas matrices specifically shaped to the exact dimensional width seen during the model's training phase.

## 3. Irrigation Advisor (`IrrigationAdvisor`)
- **Classifier:** XGBoost Classifier
- **Goal:** Generate a three-tiered rating based heavily on live ground water statuses.
- **Inputs:**
  - `Soil_Type`, `Soil_pH`, `Soil_Moisture`
  - `Temperature`, `Humidity`, `Rainfall`, `Wind_Speed`
  - `Season`, `Region`
- **Output:** String corresponding to risk level: `Low`, `Medium`, or `High`.

## 4. Fertilizer Advisor (`FertilizerAdvisor`)
- **Classifier:** XGBoost Classifier
- **Goal:** Standard chemical supplementation recommendation based on live and predicted statuses.
- **Inputs:**
  - `Temperature`, `Humidity`, `Moisture`, `Soil Type`
  - `Crop Type`, `Nitrogen`, `Potassium`, `Phosphorous`
- **Output:** Output string of recommended chemical compound (e.g., `Urea`, `10-26-26`, `DAP`).
- **Feature Layering:** Includes a smart fallback layer. If a user doesn't know their exact lab-tested NPK levels, they can use the UI to select a visual "Soil Color" (e.g., Red Soil, Black Soil) which KrishiMitra instantly maps to baseline NPK integers.
