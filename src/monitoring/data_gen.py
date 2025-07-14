import os
import pandas as pd
import random
import numpy as np

# === 1. Load Source Data (processed train) ===
source_path = "data/processed/X_train.csv"
df = pd.read_csv(source_path)

# === 2. Simulate "live" data drift by:
# - Sampling random rows
# - Modifying some values (e.g., tenure, MonthlyCharges)
sampled = df.sample(n=200, random_state=42).copy()

# Simulate slight drift in numerical features
if 'MonthlyCharges' in sampled.columns:
    sampled['MonthlyCharges'] += np.random.normal(0, 5, size=sampled.shape[0])  # ±5 unit noise
if 'TotalCharges' in sampled.columns:
    sampled['TotalCharges'] += np.random.normal(0, 20, size=sampled.shape[0])  # ±20 unit noise
if 'tenure' in sampled.columns:
    sampled['tenure'] = sampled['tenure'].apply(lambda x: max(0, x + random.choice([-2, 0, 1, 3])))

# === 3. Save as "live" data ===
os.makedirs("data/live", exist_ok=True)
sampled.to_csv("data/live/new_inference_data.csv", index=False)

print("✅ Live data generated and saved to data/live/new_inference_data.csv")
