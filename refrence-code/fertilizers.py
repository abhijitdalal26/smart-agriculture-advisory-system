import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

DATA_PATH = "./data/fertilizer-prediction.csv"
RANDOM_STATE = 42
MODEL_PATH = "./model/fertilizer_recommendation_xgboost.json"
ENCODER_PATH = "./model/fertilizer_recommendation_label_encoders.pkl"

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
print("Data loaded:", df.shape)
print(df.head())
print("\nColumn dtypes:\n", df.dtypes)
print("\nNull values:\n", df.isnull().sum())

# ─────────────────────────────────────────────
# 2. LABEL ENCODE CATEGORICAL COLUMNS
#    Store each encoder so we can inverse_transform later
# ─────────────────────────────────────────────
CATEGORICAL_COLS = ["Soil Type", "Crop Type"]
TARGET_COL = "Fertilizer Name"

label_encoders = {}

for col in CATEGORICAL_COLS:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le
    print(f"Encoded '{col}': {list(le.classes_)}")

target_le = LabelEncoder()
df[TARGET_COL] = target_le.fit_transform(df[TARGET_COL])
label_encoders[TARGET_COL] = target_le
print(f"\nTarget classes ({len(target_le.classes_)}):\n  {list(target_le.classes_)}")

# ─────────────────────────────────────────────
# 3. FEATURES & TARGET SPLIT
# ─────────────────────────────────────────────
FEATURE_COLS = [c for c in df.columns if c != TARGET_COL]
X = df[FEATURE_COLS]
y = df[TARGET_COL]

print(f"\nFeatures: {FEATURE_COLS}")
print(f"X shape: {X.shape} | y shape: {y.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

print(f"\nTrain size: {len(X_train)} | Test size: {len(X_test)}")

# ─────────────────────────────────────────────
# 4. TRAIN XGBOOST
# ─────────────────────────────────────────────
model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric="mlogloss",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

print("\nTraining XGBoost...")
model.fit(
    X_train,
    y_train,
    eval_set=[(X_test, y_test)],
    verbose=50,
)

# ─────────────────────────────────────────────
# 5. EVALUATE
# ─────────────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy: {acc * 100:.2f}%")

y_test_labels = target_le.inverse_transform(y_test)
y_pred_labels = target_le.inverse_transform(y_pred)
print("\nClassification Report:")
print(classification_report(y_test_labels, y_pred_labels))

# ─────────────────────────────────────────────
# 6. FEATURE IMPORTANCE
# ─────────────────────────────────────────────
fi = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(
    ascending=False
)
print("\nFeature Importances:")
print(fi.to_string())

os.makedirs("./model", exist_ok=True)
model.save_model(MODEL_PATH)
with open(ENCODER_PATH, "wb") as f:
    pickle.dump(
        {
            "label_encoders": label_encoders,
            "feature_columns": FEATURE_COLS,
        },
        f,
    )

print(f"\nSaved model to {MODEL_PATH}")
print(f"Saved encoders to {ENCODER_PATH}")


# ─────────────────────────────────────────────
# 8. PREDICTION HELPER — reuse anytime
# ─────────────────────────────────────────────
def predict_fertilizer(sample: dict) -> str:
    """
    Pass a raw sample dict with original string values for categorical cols.

    Example:
        predict_fertilizer({
            "Temparature": 33,
            "Humidity": 56,
            "Moisture": 56,
            "Soil Type": "Loamy",
            "Crop Type": "Ground Nuts",
            "Nitrogen": 37,
            "Potassium": 5,
            "Phosphorous": 24,
        })
    """
    row = sample.copy()
    for col in CATEGORICAL_COLS:
        row[col] = label_encoders[col].transform([row[col]])[0]

    input_df = pd.DataFrame([row])[FEATURE_COLS]
    pred_encoded = model.predict(input_df)[0]
    return label_encoders[TARGET_COL].inverse_transform([pred_encoded])[0]


loaded_model = XGBClassifier()
loaded_model.load_model(MODEL_PATH)

with open(ENCODER_PATH, "rb") as f:
    saved_artifacts = pickle.load(f)

loaded_label_encoders = saved_artifacts["label_encoders"]
loaded_feature_columns = saved_artifacts["feature_columns"]


def predict_fertilizer_from_saved_model(sample: dict) -> str:
    row = sample.copy()
    for col in CATEGORICAL_COLS:
        row[col] = loaded_label_encoders[col].transform([row[col]])[0]

    input_df = pd.DataFrame([row])[loaded_feature_columns]
    pred_encoded = loaded_model.predict(input_df)[0]
    return loaded_label_encoders[TARGET_COL].inverse_transform([pred_encoded])[0]


sample = {
    "Temparature": 32,
    "Humidity": 51,
    "Moisture": 41,
    "Soil Type": "Red",
    "Crop Type": "Ground Nuts",
    "Nitrogen": 7,
    "Potassium": 3,
    "Phosphorous": 19,
}

result = predict_fertilizer(sample)
print("\nDemo Prediction for sample input:")
for k, v in sample.items():
    print(f"   {k}: {v}")
print(f"   Recommended Fertilizer: {result}")

saved_result = predict_fertilizer_from_saved_model(sample)
print("\nDemo Prediction from saved model:")
for k, v in sample.items():
    print(f"   {k}: {v}")
print(f"   Recommended Fertilizer: {saved_result}")
