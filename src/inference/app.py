import os
import time
import threading
import pandas as pd
import mlflow
import mlflow.pyfunc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import make_asgi_app, start_http_server
from monitoring.monitor import monitor  # Make sure this works
import uvicorn

# === Set MLflow Tracking URI ===
mlflow.set_tracking_uri("http://localhost:5000")  # Update if remote MLflow

# === Load model by version ===
MODEL_NAME = "ChurnModelNamrata"
MODEL_VERSION = 2
model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_VERSION}")

# === Define input schema ===
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

# === FastAPI app ===
app = FastAPI(title="Churn Prediction API", version="1.0")

# === Mount Prometheus metrics ===
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/")
def root():
    return {"message": "Welcome to the Churn Prediction API!"}

@app.post("/predict")
def predict_churn(data: CustomerData):
    try:
        input_df = pd.DataFrame([data.dict()])
        prediction = model.predict(input_df)
        result = "Yes" if prediction[0] == 1 else "No"
        return {"prediction": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Background monitoring function ===
def background_monitoring():
    while True:
        print("🔍 Running monitor() in background...")
        try:
            monitor()
        except Exception as e:
            print(f"⚠️ Monitor error: {e}")
        time.sleep(60)

# === Run app with Prometheus & Monitoring ===
if __name__ == "__main__":
    start_http_server(8001)  # Prometheus pulls metrics from here
    thread = threading.Thread(target=background_monitoring, daemon=True)
    thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
