import os
import time
import threading
import pandas as pd
import mlflow
import mlflow.pyfunc
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import make_asgi_app, start_http_server
from monitoring.monitor import monitor
import uvicorn

# === Set MLflow Tracking URI ===
mlflow.set_tracking_uri("http://localhost:5000")  # Update if remote MLflow

# === Lazy Load MLflow Model ===
MODEL_NAME = "ChurnModelNamrata"
MODEL_VERSION = 2
model = None  # Will load only when needed


def get_model():
    global model
    if model is None:
        print(f"📦 Loading model: {MODEL_NAME} (v{MODEL_VERSION})...")
        model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_VERSION}")
        print("✅ Model loaded successfully.")
    return model


# === FastAPI app ===
app = FastAPI(title="Churn Prediction API", version="1.0")

# === Mount Prometheus metrics ===
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# === Input Schema ===
class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float


@app.get("/")
def root():
    return {"message": "Welcome to the Churn Prediction API!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
def predict_churn(data: CustomerData):
    try:
        input_df = pd.DataFrame([data.dict()])
        loaded_model = get_model()
        prediction = loaded_model.predict(input_df)
        result = "Yes" if prediction[0] == 1 else "No"
        return {"prediction": result}
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Slack Alert Function ===
def send_slack_alert(message: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL not set. Skipping alert.")
        return

    try:
        response = requests.post(webhook_url, json={"text": message})
        response.raise_for_status()
        print("✅ Slack alert sent.")
    except Exception as e:
        print(f"❌ Failed to send Slack alert: {e}")


# === Background monitoring function ===
def background_monitoring():
    while True:
        print("🔍 Running monitor() in background...")
        try:
            monitor()
        except Exception as e:
            print(f"⚠️ Monitor error: {e}")
            send_slack_alert(f"⚠ Drift Detection Error:\n{e}")
        time.sleep(60)


# === Run app with Prometheus & Monitoring ===
if __name__ == "__main__":
    print("🚀 Starting Prometheus metrics server on port 8001...")
    start_http_server(8001)

    print("🧪 Starting background monitoring thread...")
    thread = threading.Thread(target=background_monitoring, daemon=True)
    thread.start()

    print("🌐 Starting FastAPI app on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
