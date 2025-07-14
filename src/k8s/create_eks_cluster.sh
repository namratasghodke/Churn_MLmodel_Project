#!/bin/bash

set -e  # Exit immediately on any error

# === Configuration ===
CLUSTER_NAME="churn-eks"
REGION="us-east-1"
NODE_TYPE="t3.small"
NODE_COUNT=2
NODEGROUP_NAME="spot-nodes"

echo "🔍 Checking if EKS cluster '$CLUSTER_NAME' exists..."

if eksctl get cluster --name "$CLUSTER_NAME" --region "$REGION" >/dev/null 2>&1; then
  echo "⚠️ Cluster '$CLUSTER_NAME' already exists in region '$REGION'. Skipping cluster creation."
else
  echo "🔧 Creating EKS cluster: $CLUSTER_NAME (control plane only) in $REGION"
  eksctl create cluster \
    --name "$CLUSTER_NAME" \
    --region "$REGION" \
    --version "1.30" \
    --without-nodegroup
fi

echo "🔍 Checking if nodegroup '$NODEGROUP_NAME' exists for cluster '$CLUSTER_NAME'..."

if eksctl get nodegroup --cluster "$CLUSTER_NAME" --region "$REGION" | grep -q "$NODEGROUP_NAME"; then
  echo "⚠️ Nodegroup '$NODEGROUP_NAME' already exists. Skipping nodegroup creation."
else
  echo "🚀 Creating nodegroup: $NODEGROUP_NAME for cluster $CLUSTER_NAME"
  eksctl create nodegroup \
    --cluster "$CLUSTER_NAME" \
    --name "$NODEGROUP_NAME" \
    --region "$REGION" \
    --node-type "$NODE_TYPE" \
    --nodes "$NODE_COUNT" \
    --nodes-min 1 \
    --nodes-max 3 \
    --managed \
    --spot \
    --asg-access \
    --full-ecr-access \
    --alb-ingress-access
fi

echo "✅ EKS cluster '$CLUSTER_NAME' and nodegroup '$NODEGROUP_NAME' are ready!"
