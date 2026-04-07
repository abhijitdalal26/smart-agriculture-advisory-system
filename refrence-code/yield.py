import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


DATA_PATH = "./data/crop-yield-in-indian-states-dataset.csv"
RANDOM_STATE = 42


def main():
    df = pd.read_csv(DATA_PATH)

    print("Data loaded:", df.shape)
    print(df.head())
    print("\nColumn dtypes:\n", df.dtypes)
    print("\nNull values:\n", df.isnull().sum())

    # Follow the reference notebook's preprocessing direction, but avoid target leakage.
    # Using Production with Yield makes prediction nearly trivial because yield is derived from it.
    model_df = df.drop(columns=["Crop_Year", "Fertilizer", "Production"]).copy()

    categorical_columns = model_df.select_dtypes(include=["object", "string"]).columns.tolist()
    model_df = pd.get_dummies(model_df, columns=categorical_columns, drop_first=True)

    bool_columns = model_df.select_dtypes(include=["bool"]).columns
    if len(bool_columns) > 0:
        model_df[bool_columns] = model_df[bool_columns].astype(int)

    X = model_df.drop(columns=["Yield"])
    y = model_df["Yield"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    model = XGBRegressor(
        n_estimators=500,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        eval_metric="rmse",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    print("\nTraining XGBoost regressor...")
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=100,
    )

    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\nYield Prediction Metrics:")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE:  {mae:.4f}")
    print(f"R2:   {r2:.4f}")

    feature_importance = (
        pd.Series(model.feature_importances_, index=X.columns)
        .sort_values(ascending=False)
        .head(15)
    )
    print("\nTop Feature Importances:")
    print(feature_importance.to_string())


if __name__ == "__main__":
    main()
