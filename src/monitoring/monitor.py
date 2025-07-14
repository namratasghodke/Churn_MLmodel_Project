import os
import pandas as pd
import requests
from prometheus_client import Gauge
from scipy.stats import wasserstein_distance
from training.train import train_model  # Your train function

# === Prometheus metrics ===
model_accuracy = Gauge('model_accuracy', 'Accuracy of the trained model')
data_drift_metric = Gauge('data_drift_distance', 'Wasserstein distance between training and inference data')

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
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Slack alert: {e}")

# === Simple Drift Detector ===
def compute_drift(train_df, live_df):
    drift_score = 0
    count = 0
    for col in train_df.columns:
        if col in live_df.columns and pd.api.types.is_numeric_dtype(train_df[col]):
            score = wasserstein_distance(train_df[col], live_df[col])
            drift_score += score
            count += 1
    return drift_score, count

# === Main Monitoring ===
def monitor(reference_path="data/processed/X_train.csv", current_path="data/live/new_inference_data.csv"):
    ref = pd.read_csv(reference_path)
    current = pd.read_csv(current_path)

    if 'target' in current.columns or 'Churn' in current.columns:
        target_col = 'target' if 'target' in current.columns else 'Churn'
        _, acc = train_model(current, target_col)
        model_accuracy.set(acc)
        print(f"✅ Model accuracy: {acc:.4f}")
        
        # === Accuracy Slack Alert ===
        if acc < 0.75:
            send_slack_alert(f"⚠️ Low model accuracy detected: {acc:.2f}. Please investigate.")
        else:
            send_slack_alert(f"✅ Model accuracy is good: {acc:.2f}")
    else:
        print("⚠️ No target column — skipping accuracy check.")

    drift_value, num_features = compute_drift(ref, current)
    data_drift_metric.set(drift_value)
    print(f"📊 Drift (Wasserstein sum): {drift_value:.4f} across {num_features} features")

    # Alert if high drift
    if drift_value > 0.1:
        send_slack_alert(f"⚠️ High data drift detected! Drift score: {drift_value:.2f}")
    else:
        print("✅ No significant drift.")

# === Entry point ===
if __name__ == "__main__":
    monitor()
