# Azure AKS Deployment Setup Guide
## Todo AI Chatbot - Phase 5

**Version:** 1.0
**Date:** 2026-02-15
**Target Environment:** Azure Kubernetes Service (AKS)
**Estimated Setup Time:** 60-90 minutes
**Cost:** Free with $200 Azure credits (30 days)

---

## Overview

Deploy the Todo AI Chatbot to Azure AKS with production-ready infrastructure including HTTPS ingress, managed Kafka, and monitoring.

### Architecture

- Azure AKS cluster (3 nodes, Standard_B2s)
- Redpanda Cloud or Strimzi for Kafka
- Azure Database for PostgreSQL or Neon DB
- NGINX Ingress with Let's Encrypt TLS
- Dapr runtime for microservices

---

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Azure CLI | 2.55+ | https://docs.microsoft.com/cli/azure/install-azure-cli |
| kubectl | 1.28+ | https://kubernetes.io/docs/tasks/tools/ |
| Helm | 3.12+ | https://helm.sh/docs/intro/install/ |
| Dapr CLI | 1.12+ | https://docs.dapr.io/getting-started/install-dapr-cli/ |

### Azure Account Setup

1. Sign up for Azure free account: https://azure.microsoft.com/free/
2. Get $200 free credits (valid for 30 days)
3. No credit card required for signup

### Verify Installations

```bash
az --version          # Azure CLI 2.55.0+
kubectl version --client  # v1.28.0+
helm version          # v3.12.0+
dapr --version        # 1.12.0+
```

---

## Step 1: Azure Login and Setup

### 1.1 Login to Azure

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account list --output table
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"

# Verify current subscription
az account show --output table
```

### 1.2 Create Resource Group

```bash
# Create resource group in East US region
az group create \
  --name todo-rg \
  --location eastus

# Verify resource group
az group show --name todo-rg --output table
```

---

## Step 2: Create AKS Cluster

### 2.1 Create AKS Cluster

```bash
# Create AKS cluster with 3 nodes (Standard_B2s for free tier)
az aks create \
  --name todo-cluster \
  --resource-group todo-rg \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys \
  --network-plugin azure \
  --enable-addons monitoring

# This takes 5-10 minutes
```

### 2.2 Get AKS Credentials

```bash
# Configure kubectl to use AKS cluster
az aks get-credentials \
  --name todo-cluster \
  --resource-group todo-rg \
  --overwrite-existing

# Verify connection
kubectl get nodes

# Expected: 3 nodes in Ready state
```

### 2.3 Verify Cluster

```bash
# Check cluster info
kubectl cluster-info

# Check nodes
kubectl get nodes -o wide

# Check system pods
kubectl get pods -n kube-system
```

---

## Step 3: Install Dapr Runtime

```bash
# Initialize Dapr on AKS
dapr init -k

# Verify Dapr installation
dapr status -k

# Check Dapr pods
kubectl get pods -n dapr-system

# All pods should be Running
```

---

## Step 4: Deploy Kafka

### Option A: Redpanda Cloud (Recommended)

**Advantages**: Fully managed, free tier available, no cluster maintenance

1. Sign up at https://redpanda.com/try-redpanda
2. Create a cluster (select free tier)
3. Create topics: `task-events`, `reminders`, `task-updates`, `task-events-dlq`, `reminders-dlq`
4. Get connection details (bootstrap servers, SASL credentials)
5. Save broker URLs for later

### Option B: Strimzi (Self-Hosted)

```bash
# Add Strimzi Helm repo
helm repo add strimzi https://strimzi.io/charts/
helm repo update

# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
helm install strimzi strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --set watchNamespaces={kafka}

# Wait for operator to be ready
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Create Kafka cluster
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
    storage:
      type: persistent-claim
      size: 10Gi
      deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

# Wait for Kafka to be ready (5-10 minutes)
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n kafka

# Create topics
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 3
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 3
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 3
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events-dlq
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 1
  replicas: 3
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders-dlq
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 1
  replicas: 3
EOF

# Verify topics
kubectl get kafkatopics -n kafka

# Get Kafka bootstrap servers
echo "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
```

---

## Step 5: Deploy PostgreSQL

### Option A: Azure Database for PostgreSQL (Recommended)

```bash
# Create PostgreSQL flexible server
az postgres flexible-server create \
  --name todo-db-$(date +%s) \
  --resource-group todo-rg \
  --location eastus \
  --admin-user todoadmin \
  --admin-password "TodoPass123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 15 \
  --public-access 0.0.0.0

# Create database
az postgres flexible-server db create \
  --resource-group todo-rg \
  --server-name <YOUR_SERVER_NAME> \
  --database-name tododb

# Get connection string
az postgres flexible-server show \
  --resource-group todo-rg \
  --name <YOUR_SERVER_NAME> \
  --query "fullyQualifiedDomainName" -o tsv

# Connection string format:
# postgresql://todoadmin:TodoPass123!@<SERVER_FQDN>:5432/tododb?sslmode=require
```

### Option B: Neon DB (Serverless, Free Tier)

1. Sign up at https://neon.tech/
2. Create a new project
3. Create database named `tododb`
4. Copy connection string from dashboard
5. Connection string format: `postgresql://user:pass@host/tododb?sslmode=require`

---

## Step 6: Create Kubernetes Secrets

```bash
# Create application namespace
kubectl create namespace todo-app

# Create database secret (replace with your connection string)
kubectl create secret generic db-credentials \
  --from-literal=connectionString="postgresql://todoadmin:TodoPass123!@<YOUR_DB_HOST>:5432/tododb?sslmode=require" \
  -n todo-app

# Create Kafka secret
# For Redpanda Cloud:
kubectl create secret generic kafka-credentials \
  --from-literal=brokers="<REDPANDA_BROKER_URL>" \
  --from-literal=username="<SASL_USERNAME>" \
  --from-literal=password="<SASL_PASSWORD>" \
  -n todo-app

# For Strimzi:
kubectl create secret generic kafka-credentials \
  --from-literal=brokers="todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092" \
  -n todo-app

# Verify secrets
kubectl get secrets -n todo-app
```

---

## Step 7: Deploy Dapr Components

```bash
# Navigate to project directory
cd "D:/4-phases of hackathon/phase-4"

# Update Dapr component files with your connection details
# Edit dapr-components/pubsub-kafka.yaml with Kafka brokers
# Edit dapr-components/statestore-postgresql.yaml with DB connection

# Apply Dapr components
kubectl apply -f dapr-components/ -n todo-app

# Verify components
dapr components -k -n todo-app
kubectl get components -n todo-app
```

---

## Step 8: Build and Push Docker Images

### 8.1 Setup Container Registry

```bash
# Create Azure Container Registry
az acr create \
  --name todoregistry$(date +%s) \
  --resource-group todo-rg \
  --sku Basic

# Login to ACR
az acr login --name <YOUR_ACR_NAME>

# Get ACR login server
az acr show --name <YOUR_ACR_NAME> --query loginServer -o tsv
# Example: todoregistry123.azurecr.io

# Attach ACR to AKS
az aks update \
  --name todo-cluster \
  --resource-group todo-rg \
  --attach-acr <YOUR_ACR_NAME>
```

### 8.2 Build and Push Images

```bash
# Set registry variable
export ACR_NAME="<YOUR_ACR_NAME>.azurecr.io"

# Build and push backend
docker build -t $ACR_NAME/todo-backend:latest ./backend
docker push $ACR_NAME/todo-backend:latest

# Build and push frontend
docker build -t $ACR_NAME/todo-frontend:latest ./frontend
docker push $ACR_NAME/todo-frontend:latest

# Build and push worker
docker build -t $ACR_NAME/todo-worker:latest ./worker
docker push $ACR_NAME/todo-worker:latest

# Verify images
az acr repository list --name <YOUR_ACR_NAME> --output table
```

---

## Step 9: Deploy Application with Helm

```bash
# Deploy backend
helm install backend charts/todo-backend/ \
  --namespace todo-app \
  --set image.repository=$ACR_NAME/todo-backend \
  --set image.tag=latest \
  --set dapr.enabled=true \
  --set dapr.appId=backend \
  --set dapr.appPort=8000

# Deploy frontend
helm install frontend charts/todo-frontend/ \
  --namespace todo-app \
  --set image.repository=$ACR_NAME/todo-frontend \
  --set image.tag=latest \
  --set dapr.enabled=true \
  --set dapr.appId=frontend \
  --set dapr.appPort=3000

# Deploy worker
helm install worker charts/reminder-worker/ \
  --namespace todo-app \
  --set image.repository=$ACR_NAME/todo-worker \
  --set image.tag=latest \
  --set dapr.enabled=true \
  --set dapr.appId=worker

# Wait for pods to be ready
kubectl wait --for=condition=ready pod --all -n todo-app --timeout=300s

# Verify deployments
kubectl get pods -n todo-app
kubectl get svc -n todo-app
```

---

## Step 10: Setup Ingress with HTTPS

### 10.1 Install NGINX Ingress Controller

```bash
# Add ingress-nginx Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer

# Wait for external IP (may take 2-3 minutes)
kubectl get svc -n ingress-nginx -w

# Get external IP
export INGRESS_IP=$(kubectl get svc nginx-ingress-ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Ingress IP: $INGRESS_IP"
```

### 10.2 Install cert-manager for Let's Encrypt

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Create Let's Encrypt ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Verify ClusterIssuer
kubectl get clusterissuer
```

### 10.3 Create Ingress Resource

```bash
# Create ingress (replace YOUR_DOMAIN with your actual domain)
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo.YOUR_DOMAIN.com
    secretName: todo-tls
  rules:
  - host: todo.YOUR_DOMAIN.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
EOF

# Check ingress
kubectl get ingress -n todo-app
kubectl describe ingress todo-ingress -n todo-app
```

---

## Step 11: Configure DNS

### 11.1 Point Domain to Ingress IP

Configure your DNS provider to point your domain to the ingress IP:

```
Type: A Record
Name: todo (or @ for root domain)
Value: <INGRESS_IP from Step 10.1>
TTL: 300
```

### 11.2 Verify DNS Propagation

```bash
# Check DNS resolution
nslookup todo.YOUR_DOMAIN.com

# Should return the ingress IP

# Test with curl (may take 5-10 minutes for DNS propagation)
curl -I https://todo.YOUR_DOMAIN.com

# Expected: HTTP/2 200 or 301/302 redirect
```

---

## Step 12: Verification

### 12.1 Check All Resources

```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Check certificate
kubectl get certificate -n todo-app
kubectl describe certificate todo-tls -n todo-app
```

### 12.2 Test Application

```bash
# Test health endpoint
curl https://todo.YOUR_DOMAIN.com/api/health

# Create a task
curl -X POST https://todo.YOUR_DOMAIN.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production Test",
    "description": "Testing Azure deployment",
    "priority": "high",
    "tags": ["production", "azure"]
  }'

# List tasks
curl https://todo.YOUR_DOMAIN.com/api/tasks
```

### 12.3 Access in Browser

Open https://todo.YOUR_DOMAIN.com in your browser. You should see:
- Valid HTTPS certificate (green padlock)
- Todo AI Chatbot interface
- All features working

---

## Monitoring and Logging

### Azure Monitor Integration

```bash
# AKS already has Azure Monitor enabled
# View logs in Azure Portal:
# AKS cluster > Monitoring > Logs

# Query example (KQL):
# ContainerLog
# | where Namespace == "todo-app"
# | order by TimeGenerated desc
# | take 100
```

### Install Prometheus and Grafana (Optional)

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Get Grafana password
kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward to Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access Grafana at http://localhost:3000
# Username: admin
# Password: <from above command>
```

---

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod <POD_NAME> -n todo-app
kubectl logs <POD_NAME> -n todo-app
kubectl logs <POD_NAME> -c daprd -n todo-app
```

### Ingress Not Working

```bash
kubectl describe ingress todo-ingress -n todo-app
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### Certificate Issues

```bash
kubectl describe certificate todo-tls -n todo-app
kubectl describe certificaterequest -n todo-app
kubectl logs -n cert-manager -l app=cert-manager
```

### Database Connection Issues

```bash
# Test from pod
kubectl exec -it <BACKEND_POD> -n todo-app -c backend -- sh
# Inside pod:
nc -zv <DB_HOST> 5432
```

---

## Cost Management

### Monitor Costs

```bash
# View cost analysis in Azure Portal
# Cost Management + Billing > Cost Analysis

# Set budget alerts
# Cost Management + Billing > Budgets > Add
```

### Optimize Costs

- Use Standard_B2s nodes (cheapest option)
- Scale down to 1 node for development
- Delete resources when not in use
- Use Neon DB free tier instead of Azure Database
- Use Redpanda Cloud free tier

---

## Cleanup

### Delete Application

```bash
helm uninstall backend frontend worker -n todo-app
kubectl delete namespace todo-app
```

### Delete Infrastructure

```bash
# Delete AKS cluster
az aks delete --name todo-cluster --resource-group todo-rg --yes --no-wait

# Delete PostgreSQL (if using Azure Database)
az postgres flexible-server delete --name <SERVER_NAME> --resource-group todo-rg --yes

# Delete ACR
az acr delete --name <ACR_NAME> --resource-group todo-rg --yes

# Delete resource group (deletes everything)
az group delete --name todo-rg --yes --no-wait
```

---

## Next Steps

- Setup CI/CD with GitHub Actions
- Configure monitoring and alerting
- Implement backup and disaster recovery
- Scale application based on load
- Review security best practices

---

**Guide Version**: 1.0
**Last Updated**: 2026-02-15

*Generated following constitution.md v5.0 and phase5-spec.md v1.0*
