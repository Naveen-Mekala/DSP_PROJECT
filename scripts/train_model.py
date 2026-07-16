import os
from pathlib import Path
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# =====================================================
# LOAD DATASET
# =====================================================

data_folder = Path("data/clean")
csv_files = list(data_folder.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("No CSV file found in data/clean")

dataset_path = csv_files[0]

print(f"\nLoading Dataset: {dataset_path.name}")

df = pd.read_csv(dataset_path)

# =====================================================
# TARGET COLUMN
# =====================================================

TARGET = "Recovery_Score"

if TARGET not in df.columns:
    raise ValueError(f"{TARGET} column not found!")

# =====================================================
# REMOVE UNUSED COLUMNS
# =====================================================

columns_to_drop = [
    "Athlete_ID",
    "Day",
    "Week",
    "Day_of_Week"
]

df = df.drop(
    columns=[col for col in columns_to_drop if col in df.columns]
)

print("\nRemaining Columns:")
print(df.columns.tolist())

# =====================================================
# FEATURES & TARGET
# =====================================================

X = df.drop(columns=[TARGET])
y = df[TARGET]

# =====================================================
# DETECT COLUMN TYPES
# =====================================================

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numeric_features = X.select_dtypes(
    exclude=["object"]
).columns.tolist()

print("\nCategorical Features")
print(categorical_features)

print("\nNumeric Features")
print(numeric_features)

# =====================================================
# PREPROCESSING
# =====================================================

numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

# =====================================================
# MODEL
# =====================================================

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

# =====================================================
# TRAIN TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("\nTraining Model...")

pipeline.fit(X_train, y_train)

print("Training Complete!")

# =====================================================
# PREDICTIONS
# =====================================================

predictions = pipeline.predict(X_test)

# =====================================================
# EVALUATION
# =====================================================

mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================")

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")

# =====================================================
# SAVE MODEL
# =====================================================

os.makedirs("models", exist_ok=True)

model_path = "models/model.pkl"

joblib.dump(pipeline, model_path)

print("\n==============================")
print("Model Saved Successfully!")
print("==============================")
print(f"Location : {model_path}")