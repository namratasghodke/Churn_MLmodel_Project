#!/bin/bash

# Exit on error
set -e

NAMESPACE="monitoring"
RELEASE_NAME="prometheus"
VALUES_FILE="prometheus-values.yaml"

echo "🔄 Adding Helm repos..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

echo "📦 Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE || echo "Namespace already exists"

echo "🚀 Installing Prometheus + Grafana via Helm..."
helm upgrade --install $RELEASE_NAME prometheus-community/kube-prometheus-stack \
  --namespace $NAMESPACE \
  -f $VALUES_FILE

echo "✅ Prometheus + Grafana installed in namespace: $NAMESPACE"
