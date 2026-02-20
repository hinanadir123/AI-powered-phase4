# Google GKE Deployment Setup Guide
## Todo AI Chatbot - Phase 5

**Version:** 1.0
**Date:** 2026-02-15
**Target Environment:** Google Kubernetes Engine (GKE)
**Estimated Setup Time:** 60-90 minutes
**Cost:** Free with $300 Google Cloud credits (90 days)

---

## Overview

Deploy the Todo AI Chatbot to Google GKE with production-ready infrastructure including HTTPS ingress, managed Kafka, and monitoring.

### Architecture

- GKE cluster (3 nodes, e2-medium)
- Confluent Cloud or Strimzi for Kafka
- Cloud SQL for PostgreSQL or Neon DB
- Google-managed SSL certificates or cert-manager
- Dapr runtime for microservices

---

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| gcloud CLI | 460+ | https://cloud.google.com/sdk/docs/install |
| kubectl | 1.28+ | https://kubernetes.io/docs/tasks/tools/ |
| Helm | 3.12+ | https://helm.sh/docs/intro/install/ |
| Dapr CLI | 1.12+ | https://docs.dapr.io/getting-started/install-dapr-cli/ |

### Google Cloud Account Setup

1. Sign up for Google Cloud: https://cloud.google.com/free
2. Get $300 free credits (valid for 90 days)
3. Credit card required but won't be charged during trial

### Verify Installations

```bash
gcloud --version       # Google Cloud SDK 460.0.0+
kubectl version --client  # v1.28.0+
helm version          # v3.12.0+
dapr --version        # 1.12.0+
```

---

## Step 1: Google Cloud Setup

### 1.1 Login to Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Initialize gcloud configuration
gcloud init

# Follow prompts to select/create project
```

### 1.2 Create or Select Project

```bash
# Create new project
gcloud projects create todo-project-$(date +%s) --name="Todo AI Chatbot"

# List projects
gcloud projects list

# Set active project
gcloud config set project <YOUR_PROJECT_ID>

# Verify current project
gcloud config get-value project
```

### 1.3 Enable Required APIs

```bash
# Enable Kubernetes Engine API
gcloud services enable container.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Cloud SQL API (if using Cloud SQL)
gcloud services enable sqladmin.googleapis.com

# Enable Compute Engine API
gcloud services enable compute.googleapis.com

# Verify enabled services
gcloud services list --enabled
```

---

## Step 2: Create GKE Cluster

### 2.1 Create GKE Cluster

```bash
# Create GKE cluster with 3 nodes (e2-medium for free tier)
gcloud container clusters create todo-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --disk-size=30 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5 \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-stackdriver-kubernetes

# This takes 5-10 minutes
```

### 2.2 Get GKE Credentials

```bash
# Configure kubectl to use GKE cluster
gcloud container clusters get-credentials todo-cluster \
  --zone=us-central1-a

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
# Initialize Dapr on GKE
dapr init -k

# Verify Dapr installation
dapr status -k

# Check Dapr pods
kubectl get pods -n dapr-system

# All pods should be Running
```

---

## Step 4: Deploy Kafka

### Option A: Confluent Cloud (Recommended)

**Advantages**: Fully managed, free tier available, excellent GCP integration

1. Sign up at https://www.confluent.io/confluent-cloud/tryfree/
2. Create a cluster (select Basic tier in GCP us-central1)
3. Create topics: `task-events`, `reminders`, `task-updates`, `task-events-dlq`, `reminders-dlq`
4. Create API key and secret
5. Get bootstrap servers URL
6. Save credentials for later

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

# Wait for operator
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

# Wait for Kafka (5-10 minutes)
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

# Bootstrap servers
echo "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
```

---

## Step 5: Deploy PostgreSQL

### Option A: Cloud SQL for PostgreSQL

```bash
# Create Cloud SQL instance
gcloud sql instances create todo-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=TodoPass123!

# Create database
gcloud sql databases create tododb --instance=todo-db

# Get connection name
gcloud sql instances describe todo-db --format="value(connectionName)"
# Format: PROJECT_ID:REGION:INSTANCE_NAME

# Enable Cloud SQL Proxy in GKE
# Install Cloud SQL Proxy sidecar in backend pod
# Connection string: postgresql://postgres:TodoPass123!@127.0.0.1:5432/tododb
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
  --from-literal=connectionString="postgresql://postgres:TodoPass123!@<YOUR_DB_HOST>:5432/tododb?sslmode=require" \
  -n todo-app

# Create Kafka secret
# For Confluent Cloud:
kubectl create secret generic kafka-credentials \
  --from-literal=brokers="<CONFLUENT_BROKER_URL>" \
  --from-literal=username="<API_KEY>" \
  --from-literal=password="<API_SECRET>" \
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

### 8.1 Configure Container Registry

```bash
# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Get project ID
export PROJECT_ID=$(gcloud config get-value project)
export GCR_REGISTRY="gcr.io/$PROJECT_ID"

echo "Registry: $GCR_REGISTRY"
```

### 8.2 Build and Push Images

```bash
# Build and push backend
docker build -t $GCR_REGISTRY/todo-backend:latest ./backend
docker push $GCR_REGISTRY/todo-backend:latest

# Build and push frontend
docker build -t $GCR_REGISTRY/todo-frontend:latest ./frontend
docker push $GCR_REGISTRY/todo-frontend:latest

# Build and push worker
docker build -t $GCR_REGISTRY/todo-worker:latest ./worker
docker push $GCR_REGISTRY/todo-worker:latest

# Verify images
gcloud container images list --repository=$GCR_REGISTRY
```

---

## Step 9: Deploy Application with Helm

```bash
# Deploy backend
helm install backend charts/todo-backend/ \
  --namespace todo-app \
  --set image.repository=$GCR_REGISTRY/todo-backend \
  --set image.tag=latest \
  --set dapr.enabled=true \
  --set dapr.appId=backend \
  --set dapr.appPort=8000

# Deploy frontend
helm install frontend charts/todo-frontend/ \
  --namespace todo-app \
  --set image.repository=$GCR_REGISTRY/todo-frontend \
  --set image.tag=latest \
  --set dapr.enabled=true \
  --set dapr.appId=frontend \
  --set dapr.appPort=3000

# Deploy worker
helm install worker charts/reminder-worker/ \
  --namespace todo-app \
  --set image.repository=$GCR_REGISTRY/todo-worker \
  --set image.tag=latest \
  --set dapr.enabled=true \
  --set dapr.appId=worker

# Wait for pods
kubectl wait --for=condition=ready pod --all -n todo-app --timeout=300s

# Verify deployments
kubectl get pods -n todo-app
kubectl get svc -n todo-app
```

---

## Step 10: Setup Ingress with HTTPS

### Option A: Google-Managed SSL Certificates (Recommended)

```bash
# Reserve static IP
gcloud compute addresses create todo-ip --global

# Get static IP
export STATIC_IP=$(gcloud compute addresses describe todo-ip --global --format="value(address)")
echo "Static IP: $STATIC_IP"

# Create managed certificate
cat <<EOF | kubectl apply -f -
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: todo-cert
  namespace: todo-app
spec:
  domains:
    - todo.YOUR_DOMAIN.com
EOF

# Create ingress with Google-managed certificate
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    kubernetes.io/ingress.global-static-ip-name: todo-ip
    networking.gke.io/managed-certificates: todo-cert
    kubernetes.io/ingress.class: "gce"
spec:
  rules:
  - host: todo.YOUR_DOMAIN.com
    http:
      paths:
      - path: /api/*
        pathType: ImplementationSpecific
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: frontend
            port:
              number: 3000
EOF

# Check ingress (may take 10-15 minutes for certificate provisioning)
kubectl get ingress -n todo-app
kubectl describe ingress todo-ingress -n todo-app
kubectl get managedcertificate -n todo-app
```

### Option B: cert-manager with Let's Encrypt

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Create ClusterIssuer
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
          class: gce
EOF

# Create ingress with cert-manager
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    kubernetes.io/ingress.class: "gce"
spec:
  tls:
  - hosts:
    - todo.YOUR_DOMAIN.com
    secretName: todo-tls
  rules:
  - host: todo.YOUR_DOMAIN.com
    http:
      paths:
      - path: /api/*
        pathType: ImplementationSpecific
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /*
        pathType: ImplementationSpecific
        backend:
          service:
            name: frontend
            port:
              number: 3000
EOF
```

---

## Step 11: Configure DNS

### 11.1 Point Domain to Static IP

Configure your DNS provider:

```
Type: A Record
Name: todo (or @ for root domain)
Value: <STATIC_IP from Step 10>
TTL: 300
```

### 11.2 Verify DNS Propagation

```bash
# Check DNS resolution
nslookup todo.YOUR_DOMAIN.com

# Should return the static IP

# Test with curl (may take 10-15 minutes for certificate provisioning)
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

# Check managed certificate (if using Google-managed)
kubectl get managedcertificate -n todo-app
kubectl describe managedcertificate todo-cert -n todo-app
```

### 12.2 Test Application

```bash
# Test health endpoint
curl https://todo.YOUR_DOMAIN.com/api/health

# Create a task
curl -X POST https://todo.YOUR_DOMAIN.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "GKE Production Test",
    "description": "Testing Google Cloud deployment",
    "priority": "high",
    "tags": ["production", "gke"]
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

### Google Cloud Operations (Built-in)

```bash
# GKE automatically sends logs and metrics to Cloud Operations

# View logs in Cloud Console:
# Kubernetes Engine > Workloads > Select pod > Logs

# View metrics:
# Kubernetes Engine > Workloads > Select pod > Metrics

# Create log-based alerts:
# Logging > Logs Explorer > Create alert
```

### Install Prometheus and Grafana (Optional)

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Get Grafana password
kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward to Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access at http://localhost:3000
# Username: admin
# Password: <from above>
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
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Certificate Provisioning Stuck

```bash
# Check managed certificate status
kubectl describe managedcertificate todo-cert -n todo-app

# Common issues:
# - DNS not pointing to static IP
# - Domain verification pending
# - Certificate provisioning can take 10-15 minutes
```

### Cloud SQL Connection Issues

```bash
# Verify Cloud SQL Proxy is running
kubectl logs <BACKEND_POD> -c cloud-sql-proxy -n todo-app

# Check Cloud SQL instance status
gcloud sql instances describe todo-db
```

---

## Cost Management

### Monitor Costs

```bash
# View billing in Cloud Console
# Billing > Reports

# Set budget alerts
# Billing > Budgets & alerts > Create budget
```

### Optimize Costs

- Use e2-medium nodes (cost-effective)
- Enable cluster autoscaling (scale to 1 node when idle)
- Use preemptible nodes for non-production
- Delete resources when not in use
- Use Neon DB free tier instead of Cloud SQL
- Use Confluent Cloud free tier

### Cost Estimates

- GKE cluster (3 x e2-medium): ~$75/month
- Cloud SQL (db-f1-micro): ~$15/month
- Load balancer: ~$18/month
- Total: ~$108/month (covered by $300 credits for 2-3 months)

---

## Cleanup

### Delete Application

```bash
helm uninstall backend frontend worker -n todo-app
kubectl delete namespace todo-app
```

### Delete Infrastructure

```bash
# Delete GKE cluster
gcloud container clusters delete todo-cluster --zone=us-central1-a --quiet

# Delete Cloud SQL instance
gcloud sql instances delete todo-db --quiet

# Delete static IP
gcloud compute addresses delete todo-ip --global --quiet

# Delete container images
gcloud container images delete $GCR_REGISTRY/todo-backend:latest --quiet
gcloud container images delete $GCR_REGISTRY/todo-frontend:latest --quiet
gcloud container images delete $GCR_REGISTRY/todo-worker:latest --quiet

# Delete project (deletes everything)
gcloud projects delete <PROJECT_ID> --quiet
```

---

## Next Steps

- Setup CI/CD with Cloud Build or GitHub Actions
- Configure Cloud Armor for DDoS protection
- Implement Cloud CDN for frontend caching
- Setup Cloud Monitoring alerts
- Review security best practices

---

## GKE-Specific Features

### Autopilot Mode (Alternative)

For fully managed experience, use GKE Autopilot:

```bash
gcloud container clusters create-auto todo-cluster-autopilot \
  --region=us-central1

# Autopilot manages nodes, scaling, and security automatically
# Higher cost but less operational overhead
```

### Workload Identity

For secure access to Google Cloud services:

```bash
# Enable Workload Identity on cluster
gcloud container clusters update todo-cluster \
  --workload-pool=<PROJECT_ID>.svc.id.goog \
  --zone=us-central1-a

# Configure service accounts to use Workload Identity
# See: https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity
```

---

**Guide Version**: 1.0
**Last Updated**: 2026-02-15

*Generated following constitution.md v5.0 and phase5-spec.md v1.0*
