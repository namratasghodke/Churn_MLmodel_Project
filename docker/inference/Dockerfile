# Use official Python base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY src/ /app/src
COPY data/ /app/data
COPY artifacts/ /app/artifacts
COPY mlruns/ /app/mlruns

# Set PYTHONPATH so `monitoring` can be imported in app.py
ENV PYTHONPATH="/app/src"

# Expose ports: FastAPI (8000), Prometheus (8001), MLflow optional (5000)
EXPOSE 8000 8001 5000

# Set MLflow tracking URI
ENV MLFLOW_TRACKING_URI=http://localhost:5000

# Default command to run FastAPI app
CMD ["python", "src/inference/app.py"]

