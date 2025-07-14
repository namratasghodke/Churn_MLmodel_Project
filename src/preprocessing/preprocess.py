import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# === 1. Load Raw Data ===
raw_path = "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"  # ensure this is your actual file path
df = pd.read_csv(raw_path)

# === 2. Basic Cleaning ===
# Drop customerID (not useful for modeling)
df.drop(columns=["customerID"], inplace=True)

# Fix TotalCharges to numeric (some may be empty or spaces)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors='coerce')

# Drop rows with null target or TotalCharges
df = df.dropna(subset=["Churn", "TotalCharges"])

# === 3. Define target & features ===
target_col = "Churn"
y = df[target_col].map({"Yes": 1, "No": 0})  # binary encode target
X = df.drop(columns=[target_col])

# === 4. Identify column types ===
categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
numerical_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

# === 5. Preprocessing Pipelines ===
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numerical_cols),
    ("cat", OneHotEncoder(handle_unknown='ignore', sparse=False), categorical_cols)
])

pipeline = Pipeline([
    ("preprocessor", preprocessor)
])

# === 6. Fit & Transform ===
X_processed = pipeline.fit_transform(X)

# Save preprocessor for later use
os.makedirs("artifacts", exist_ok=True)
joblib.dump(pipeline, "artifacts/preprocessor.pkl")

# === 7. Train/Test/Val Split ===
X_train, X_temp, y_train, y_temp = train_test_split(X_processed, y, test_size=0.3, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

# === 8. Save Processed Data ===
output_dir = "data/processed"
os.makedirs(output_dir, exist_ok=True)

pd.DataFrame(X_train).to_csv(f"{output_dir}/X_train.csv", index=False)
pd.DataFrame(y_train).to_csv(f"{output_dir}/y_train.csv", index=False)
pd.DataFrame(X_val).to_csv(f"{output_dir}/X_val.csv", index=False)
pd.DataFrame(y_val).to_csv(f"{output_dir}/y_val.csv", index=False)
pd.DataFrame(X_test).to_csv(f"{output_dir}/X_test.csv", index=False)
pd.DataFrame(y_test).to_csv(f"{output_dir}/y_test.csv", index=False)
