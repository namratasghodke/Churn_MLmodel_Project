# mlops-churn-capstone
✅ Step-by-Step Cleanup Guide
🔁 1. Delete Your App Resources (Model Inference + Monitoring)
Run these commands to delete Kubernetes manifests:


# Navigate to your k8s folder where YAMLs are defined
cd path/to/k8s/

# Delete all resources in your churn-app
kubectl delete -f churn-deployment.yaml
kubectl delete -f churn-service.yaml
kubectl delete -f churn-hpa.yaml

# Delete monitoring resources
kubectl delete -f ../monitor/service_monitor.yaml --ignore-not-found
kubectl delete -f ../monitor/prometheus_values.yaml --ignore-not-found
kubectl delete -f ../monitor/install_promethe.sh --ignore-not-found
Or, if everything is in one folder:


kubectl delete -f . --recursive
🧼 2. Delete Prometheus and Grafana via Helm (if installed that way)

helm uninstall kube-prometheus-stack -n monitoring
kubectl delete namespace monitoring
🧹 3. Delete All Pods/Services/Deployments Leftover

kubectl delete all --all -n default
kubectl delete all --all -n monitoring
🛑 4. Delete Nodegroups from EKS

eksctl delete nodegroup --cluster churn-eks --name spot-nodes --region us-east-1
eksctl delete nodegroup --cluster churn-eks --name mixed-nodes --region us-east-1
💣 5. Delete EKS Cluster

eksctl delete cluster --name churn-eks --region us-east-1
🧽 6. (Optional) Delete Docker Images Locally

docker image rm churn-app
docker image prune -f
🔚 7. Confirm Cleanup
Run:

