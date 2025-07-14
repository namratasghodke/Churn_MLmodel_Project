import os
import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, ConfusionMatrixDisplay
)

def train_model(data=None, target_column="Churn", run_mlflow=True):
    """
    Trains a RandomForest model on processed data.
    If `data` is provided, it will train on that; otherwise, uses X_train/y_train from disk.

    Returns:
        model: trained model object
        accuracy: float
    """
    if data is not None:
        X = data.drop(columns=[target_column])
        y = data[target_column].values.ravel()
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_val, y_val = X_test, y_test  # use test as validation here
    else:
        data_dir = "data/processed"
        X_train = pd.read_csv(f"{data_dir}/X_train.csv")
        y_train = pd.read_csv(f"{data_dir}/y_train.csv").values.ravel()
        X_val = pd.read_csv(f"{data_dir}/X_val.csv")
        y_val = pd.read_csv(f"{data_dir}/y_val.csv").values.ravel()
        X_test = pd.read_csv(f"{data_dir}/X_test.csv")
        y_test = pd.read_csv(f"{data_dir}/y_test.csv").values.ravel()

    # === Model Training ===
    params = {
        "n_estimators": 100,
        "max_depth": 5,
        "random_state": 42
    }
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # === Validation Prediction ===
    val_preds = model.predict(X_val)
    metrics = {
        "val_accuracy": accuracy_score(y_val, val_preds),
        "val_precision": precision_score(y_val, val_preds),
        "val_recall": recall_score(y_val, val_preds),
        "val_f1": f1_score(y_val, val_preds)
    }

    if run_mlflow:
        # === MLflow URI Setup ===
        if os.getenv("CI") == "true":
            mlflow.set_tracking_uri("file:///tmp/mlruns")
        else:
            mlflow.set_tracking_uri("http://localhost:5000")

        mlflow.set_experiment("churn-prediction-namrata")

        with mlflow.start_run():
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)

            # Confusion matrix
            cm = confusion_matrix(y_val, val_preds)
            disp = ConfusionMatrixDisplay(cm)
            disp.plot()
            os.makedirs("artifacts", exist_ok=True)
            cm_path = "artifacts/confusion_matrix.png"
            plt.savefig(cm_path)
            mlflow.log_artifact(cm_path)

            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                registered_model_name="ChurnModelNamrata"
            )
            print("✅ Model trained, metrics logged, and model registered to MLflow.")
    else:
        print("✅ Model trained (no MLflow run).")

    return model, metrics["val_accuracy"]

# === Optional direct run ===
if __name__ == "__main__":
    train_model()
