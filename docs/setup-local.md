# Local Deployment Setup Guide (Minikube)
## Todo AI Chatbot - Phase 5

**Version:** 1.0
**Date:** 2026-02-15
**Target Environment:** Local Development (Minikube)
**Estimated Setup Time:** 45-60 minutes

---

## Overview

This guide walks you through setting up the Todo AI Chatbot application on your local machine using Minikube. This setup is ideal for development, testing, and learning the application architecture before deploying to cloud environments.

### What You'll Deploy

- Minikube Kubernetes cluster (local)
- Dapr runtime for microservices
- Kafka messaging (Redpanda)
- PostgreSQL database
- Backend API service
- Frontend web application
- Reminder worker service

---

## Prerequisites

### Required Software

Install the following tools before proceeding:

| Tool | Minimum Version | Installation Link |
|------|----------------|-------------------|
| **Docker Desktop** | 24.0+ | https://www.docker.com/products/docker-desktop/ |
| **Minikube** | 1.32+ | https://minikube.sigs.k8s.io/docs/start/ |
| **kubectl** | 1.28+ | https://kubernetes.io/docs/tasks/tools/ |
| **Helm** | 3.12+ | https://helm.sh/docs/intro/install/ |
| **Dapr CLI** | 1.12+ | https://docs.dapr.io/getting-started/install-dapr-cli/ |

### System Requirements

- **CPU**: 4 cores minimum (8 cores recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 20GB free space
- **OS**: Windows 10/11, macOS 11+, or Linux

### Verify Installations

```bash
# Check Docker
docker --version
# Expected: Docker version 24.0.0 or higher

# Check Minikube
minikube version
# Expected: minikube version: v1.32.0 or higher

# Check kubectl
kubectl version --client
# Expected: Client Version: v1.28.0 or higher

# Check Helm
helm version
# Expected: version.BuildInfo{Version:"v3.12.0" or higher}

# Check Dapr CLI
dapr --version
# Expected: CLI version: 1.12.0 or higher
```

---

## Step 1: Start Minikube Cluster

### 1.1 Start Minikube with Recommended Settings

```bash
# Start Minikube with 4 CPUs and 8GB RAM
minikube start --cpus=4 --memory=8192 --driver=docker

# Expected output:
# 😄  minikube v1.32.0 on Darwin 13.0
# ✨  Using the docker driver based on user configuration
# 👍  Starting control plane node minikube in cluster minikube
# 🚜  Pulling base image ...
# 🔥  Creating docker container (CPUs=4, Memory=8192MB) ...
# 🐳  Preparing Kubernetes v1.28.3 on Docker 24.0.7 ...
# 🔎  Verifying Kubernetes components...
# 🌟  Enabled addons: storage-provisioner, default-storageclass
# 🏄  Done! kubectl is now configured to use "minikube" cluster
```

### 1.2 Verify Cluster is Running

```bash
# Check cluster status
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured

# Check kubectl context
kubectl config current-context
# Expected: minikube

# Check nodes
kubectl get nodes
# Expected: minikube   Ready    control-plane   1m   v1.28.3
```

### 1.3 Enable Minikube Addons (Optional)

```bash
# Enable metrics server for resource monitoring
minikube addons enable metrics-server

# Enable ingress for local URL access (optional)
minikube addons enable ingress

# List enabled addons
minikube addons list
```

---

## Step 2: Install Dapr Runtime

### 2.1 Initialize Dapr on Kubernetes

```bash
# Initialize Dapr in Kubernetes mode
dapr init -k

# Expected output:
# ⌛  Making the jump to hyperspace...
# ℹ️  Note: To install Dapr using Helm, see here: https://docs.dapr.io/getting-started/install-dapr-kubernetes/#install-with-helm-advanced
# ✅  Deploying the Dapr control plane to your cluster...
# ✅  Success! Dapr has been installed to namespace dapr-system. To verify, run `dapr status -k' in your terminal.
```

### 2.2 Verify Dapr Installation

```bash
# Check Dapr status
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m   2026-02-15 10:00.00
# dapr-sentry            dapr-system  True     Running  1         1.12.0   1m   2026-02-15 10:00.00
# dapr-operator          dapr-system  True     Running  1         1.12.0   1m   2026-02-15 10:00.00
# dapr-placement         dapr-system  True     Running  1         1.12.0   1m   2026-02-15 10:00.00

# Check Dapr pods
kubectl get pods -n dapr-system

# All pods should be in Running state
```

---

## Step 3: Deploy Kafka (Redpanda)

### 3.1 Add Redpanda Helm Repository

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com/

# Update Helm repos
helm repo update

# Expected output:
# "redpanda" has been added to your repositories
# Hang tight while we grab the latest from your chart repositories...
# ...Successfully got an update from the "redpanda" chart repository
```

### 3.2 Create Kafka Namespace

```bash
# Create namespace for Kafka
kubectl create namespace kafka

# Verify namespace
kubectl get namespaces | grep kafka
# Expected: kafka   Active   5s
```

### 3.3 Deploy Redpanda Cluster

```bash
# Install Redpanda with minimal resources for local development
helm install redpanda redpanda/redpanda \
  --namespace kafka \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=2Gi \
  --set storage.persistentVolume.size=10Gi

# Expected output:
# NAME: redpanda
# LAST DEPLOYED: Fri Feb 15 10:05:00 2026
# NAMESPACE: kafka
# STATUS: deployed
# REVISION: 1
```

### 3.4 Wait for Redpanda to be Ready

```bash
# Watch Redpanda pods until ready (may take 2-3 minutes)
kubectl get pods -n kafka -w

# Press Ctrl+C when pod shows 1/1 Running
# Expected: redpanda-0   1/1   Running   0   2m

# Verify Redpanda is healthy
kubectl exec -it redpanda-0 -n kafka -- rpk cluster info

# Expected output showing cluster information
```

### 3.5 Create Kafka Topics

```bash
# Create task-events topic
kubectl exec -it redpanda-0 -n kafka -- \
  rpk topic create task-events --partitions 3 --replicas 1

# Create reminders topic
kubectl exec -it redpanda-0 -n kafka -- \
  rpk topic create reminders --partitions 3 --replicas 1

# Create task-updates topic
kubectl exec -it redpanda-0 -n kafka -- \
  rpk topic create task-updates --partitions 3 --replicas 1

# Create dead letter queues
kubectl exec -it redpanda-0 -n kafka -- \
  rpk topic create task-events-dlq --partitions 1 --replicas 1

kubectl exec -it redpanda-0 -n kafka -- \
  rpk topic create reminders-dlq --partitions 1 --replicas 1

# List all topics
kubectl exec -it redpanda-0 -n kafka -- rpk topic list

# Expected output:
# NAME              PARTITIONS  REPLICAS
# task-events       3           1
# reminders         3           1
# task-updates      3           1
# task-events-dlq   1           1
# reminders-dlq     1           1
```

---

## Step 4: Deploy PostgreSQL Database

### 4.1 Add Bitnami Helm Repository

```bash
# Add Bitnami Helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update Helm repos
helm repo update
```

### 4.2 Create Database Namespace

```bash
# Create namespace for database
kubectl create namespace database

# Verify namespace
kubectl get namespaces | grep database
```

### 4.3 Deploy PostgreSQL

```bash
# Install PostgreSQL with custom password
helm install postgres bitnami/postgresql \
  --namespace database \
  --set auth.postgresPassword=postgres123 \
  --set auth.database=tododb \
  --set primary.persistence.size=5Gi

# Expected output:
# NAME: postgres
# LAST DEPLOYED: Fri Feb 15 10:10:00 2026
# NAMESPACE: database
# STATUS: deployed
```

### 4.4 Verify PostgreSQL is Running

```bash
# Check PostgreSQL pod
kubectl get pods -n database

# Expected: postgres-postgresql-0   1/1   Running   0   1m

# Test database connection
kubectl exec -it postgres-postgresql-0 -n database -- \
  psql -U postgres -d tododb -c "SELECT version();"

# Expected: PostgreSQL version information
```

### 4.5 Get Database Connection String

```bash
# Connection string for internal cluster access
echo "postgresql://postgres:postgres123@postgres-postgresql.database.svc.cluster.local:5432/tododb"

# Save this connection string for later use
```

---

## Step 5: Create Kubernetes Secrets

### 5.1 Create Application Namespace

```bash
# Create namespace for application
kubectl create namespace todo-app

# Verify namespace
kubectl get namespaces | grep todo-app
```

### 5.2 Create Database Secret

```bash
# Create secret with database connection string
kubectl create secret generic db-credentials \
  --from-literal=connectionString="postgresql://postgres:postgres123@postgres-postgresql.database.svc.cluster.local:5432/tododb" \
  -n todo-app

# Verify secret
kubectl get secret db-credentials -n todo-app
```

### 5.3 Create Kafka Secret

```bash
# Create secret with Kafka broker addresses
kubectl create secret generic kafka-credentials \
  --from-literal=brokers="redpanda-0.redpanda.kafka.svc.cluster.local:9092" \
  -n todo-app

# Verify secret
kubectl get secret kafka-credentials -n todo-app
```

---

## Step 6: Deploy Dapr Components

### 6.1 Navigate to Project Directory

```bash
# Navigate to your project root
cd "D:/4-phases of hackathon/phase-4"

# Verify dapr-components directory exists
ls dapr-components/
# Expected: pubsub-kafka.yaml, statestore-postgresql.yaml, etc.
```

### 6.2 Apply Dapr Components

```bash
# Apply all Dapr component configurations
kubectl apply -f dapr-components/ -n todo-app

# Expected output:
# component.dapr.io/pubsub-kafka created
# component.dapr.io/statestore-postgresql created
# component.dapr.io/jobs-scheduler created
# component.dapr.io/secretstore-kubernetes created
```

### 6.3 Verify Dapr Components

```bash
# List Dapr components
dapr components -k -n todo-app

# Expected output showing all components with CREATED status

# Check component details
kubectl get components -n todo-app
```

---

## Step 7: Deploy Application with Helm

### 7.1 Deploy Backend Service

```bash
# Install backend Helm chart
helm install backend charts/todo-backend/ \
  --namespace todo-app \
  --set dapr.enabled=true \
  --set dapr.appId=backend \
  --set dapr.appPort=8000

# Expected output:
# NAME: backend
# LAST DEPLOYED: Fri Feb 15 10:20:00 2026
# NAMESPACE: todo-app
# STATUS: deployed

# Wait for backend pod to be ready
kubectl wait --for=condition=ready pod -l app=backend -n todo-app --timeout=120s
```

### 7.2 Deploy Frontend Service

```bash
# Install frontend Helm chart
helm install frontend charts/todo-frontend/ \
  --namespace todo-app \
  --set dapr.enabled=true \
  --set dapr.appId=frontend \
  --set dapr.appPort=3000

# Expected output:
# NAME: frontend
# LAST DEPLOYED: Fri Feb 15 10:22:00 2026
# NAMESPACE: todo-app
# STATUS: deployed

# Wait for frontend pod to be ready
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=120s
```

### 7.3 Deploy Reminder Worker Service

```bash
# Install reminder worker Helm chart
helm install worker charts/reminder-worker/ \
  --namespace todo-app \
  --set dapr.enabled=true \
  --set dapr.appId=worker

# Expected output:
# NAME: worker
# LAST DEPLOYED: Fri Feb 15 10:24:00 2026
# NAMESPACE: todo-app
# STATUS: deployed

# Wait for worker pod to be ready
kubectl wait --for=condition=ready pod -l app=worker -n todo-app --timeout=120s
```

### 7.4 Verify All Deployments

```bash
# Check all pods in todo-app namespace
kubectl get pods -n todo-app

# Expected output (all pods should be Running with 2/2 containers):
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxxxxxxxxx-xxxxx    2/2     Running   0          2m
# frontend-xxxxxxxxxx-xxxxx   2/2     Running   0          2m
# worker-xxxxxxxxxx-xxxxx     2/2     Running   0          1m

# Check services
kubectl get svc -n todo-app

# Expected output:
# NAME       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
# backend    ClusterIP   10.96.xxx.xxx   <none>        8000/TCP   2m
# frontend   ClusterIP   10.96.xxx.xxx   <none>        3000/TCP   2m
```

---

## Step 8: Access the Application

### 8.1 Port Forward to Frontend

```bash
# Forward local port 3000 to frontend service
kubectl port-forward -n todo-app svc/frontend 3000:3000

# Expected output:
# Forwarding from 127.0.0.1:3000 -> 3000
# Forwarding from [::1]:3000 -> 3000

# Keep this terminal open
```

### 8.2 Access Application in Browser

Open your web browser and navigate to:

```
http://localhost:3000
```

You should see the Todo AI Chatbot application interface.

### 8.3 Port Forward to Backend (Optional)

In a new terminal, forward backend API:

```bash
# Forward local port 8000 to backend service
kubectl port-forward -n todo-app svc/backend 8000:8000

# Test backend API
curl http://localhost:8000/health

# Expected: {"status":"healthy","timestamp":"2026-02-15T10:30:00Z"}
```

---

## Step 9: Verification and Testing

### 9.1 Check Pod Health

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Check pod logs for errors
kubectl logs -l app=backend -n todo-app --tail=50
kubectl logs -l app=frontend -n todo-app --tail=50
kubectl logs -l app=worker -n todo-app --tail=50

# Check Dapr sidecar logs
kubectl logs -l app=backend -n todo-app -c daprd --tail=50
```

### 9.2 Test API Endpoints

```bash
# Test health endpoint
curl http://localhost:8000/health

# Create a test task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing local deployment",
    "priority": "high",
    "tags": ["test", "local"]
  }'

# List all tasks
curl http://localhost:8000/api/tasks

# Expected: JSON array with the created task
```

### 9.3 Verify Kafka Events

```bash
# Check Kafka topics have messages
kubectl exec -it redpanda-0 -n kafka -- \
  rpk topic consume task-events --num 1

# Expected: JSON event for task creation
```

### 9.4 Verify Dapr Components

```bash
# Check Dapr component status
dapr components -k -n todo-app

# All components should show CREATED status

# Test Dapr state store
kubectl exec -it $(kubectl get pod -l app=backend -n todo-app -o jsonpath='{.items[0].metadata.name}') -n todo-app -c backend -- \
  curl -X POST http://localhost:3500/v1.0/state/statestore-postgresql \
  -H "Content-Type: application/json" \
  -d '[{"key":"test","value":"hello"}]'

# Retrieve state
kubectl exec -it $(kubectl get pod -l app=backend -n todo-app -o jsonpath='{.items[0].metadata.name}') -n todo-app -c backend -- \
  curl http://localhost:3500/v1.0/state/statestore-postgresql/test

# Expected: "hello"
```

---

## Troubleshooting

### Issue: Minikube Won't Start

**Symptoms**: `minikube start` fails or hangs

**Solutions**:
```bash
# Delete existing cluster and start fresh
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker

# Try different driver
minikube start --cpus=4 --memory=8192 --driver=virtualbox

# Check Docker is running
docker ps

# Increase resources in Docker Desktop settings
# Docker Desktop > Settings > Resources > Increase CPU/Memory
```

### Issue: Pods Stuck in Pending State

**Symptoms**: Pods show `Pending` status for extended time

**Solutions**:
```bash
# Check pod events
kubectl describe pod <POD_NAME> -n todo-app

# Check node resources
kubectl top nodes

# Check if PVC is bound
kubectl get pvc -n database
kubectl get pvc -n kafka

# If storage issue, delete and recreate
kubectl delete pvc <PVC_NAME> -n <NAMESPACE>
```

### Issue: Dapr Sidecar Not Injecting

**Symptoms**: Pods show 1/1 instead of 2/2 containers

**Solutions**:
```bash
# Check Dapr annotations in deployment
kubectl get deployment backend -n todo-app -o yaml | grep dapr

# Verify Dapr is installed
dapr status -k

# Restart Dapr operator
kubectl rollout restart deployment dapr-operator -n dapr-system

# Delete and recreate pod
kubectl delete pod -l app=backend -n todo-app
```

### Issue: Cannot Connect to Kafka

**Symptoms**: Errors in logs about Kafka connection

**Solutions**:
```bash
# Check Redpanda is running
kubectl get pods -n kafka

# Check Redpanda logs
kubectl logs redpanda-0 -n kafka

# Test Kafka connectivity from backend pod
kubectl exec -it $(kubectl get pod -l app=backend -n todo-app -o jsonpath='{.items[0].metadata.name}') -n todo-app -c backend -- \
  nc -zv redpanda-0.redpanda.kafka.svc.cluster.local 9092

# Verify Kafka secret
kubectl get secret kafka-credentials -n todo-app -o yaml
```

### Issue: Database Connection Errors

**Symptoms**: Backend logs show PostgreSQL connection errors

**Solutions**:
```bash
# Check PostgreSQL is running
kubectl get pods -n database

# Check PostgreSQL logs
kubectl logs postgres-postgresql-0 -n database

# Test database connectivity from backend pod
kubectl exec -it $(kubectl get pod -l app=backend -n todo-app -o jsonpath='{.items[0].metadata.name}') -n todo-app -c backend -- \
  nc -zv postgres-postgresql.database.svc.cluster.local 5432

# Verify database secret
kubectl get secret db-credentials -n todo-app -o yaml

# Manually test connection
kubectl exec -it postgres-postgresql-0 -n database -- \
  psql -U postgres -d tododb -c "SELECT 1;"
```

### Issue: Port Forward Disconnects

**Symptoms**: `kubectl port-forward` command exits unexpectedly

**Solutions**:
```bash
# Use --address flag to bind to all interfaces
kubectl port-forward -n todo-app svc/frontend 3000:3000 --address 0.0.0.0

# Run in background with nohup
nohup kubectl port-forward -n todo-app svc/frontend 3000:3000 &

# Use kubefwd for automatic port forwarding (install separately)
# https://github.com/txn2/kubefwd
```

### Issue: High Resource Usage

**Symptoms**: Laptop fan running loud, system slow

**Solutions**:
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n todo-app

# Reduce Minikube resources
minikube stop
minikube delete
minikube start --cpus=2 --memory=4096

# Reduce replica counts in Helm values
# Edit charts/*/values.yaml and set replicaCount: 1

# Set resource limits
kubectl set resources deployment backend -n todo-app \
  --limits=cpu=500m,memory=512Mi \
  --requests=cpu=250m,memory=256Mi
```

---

## Cleanup and Uninstall

### Uninstall Application

```bash
# Uninstall Helm releases
helm uninstall backend -n todo-app
helm uninstall frontend -n todo-app
helm uninstall worker -n todo-app

# Delete Dapr components
kubectl delete -f dapr-components/ -n todo-app

# Delete secrets
kubectl delete secret db-credentials -n todo-app
kubectl delete secret kafka-credentials -n todo-app

# Delete namespace
kubectl delete namespace todo-app
```

### Uninstall Infrastructure

```bash
# Uninstall PostgreSQL
helm uninstall postgres -n database
kubectl delete namespace database

# Uninstall Redpanda
helm uninstall redpanda -n kafka
kubectl delete namespace kafka

# Uninstall Dapr
dapr uninstall -k
```

### Stop Minikube

```bash
# Stop Minikube cluster
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete

# Verify deletion
minikube status
# Expected: host: Nonexistent
```

---

## Next Steps

After successfully deploying locally, you can:

1. **Explore Features**: Test all intermediate and advanced features (priorities, tags, search, recurring tasks, reminders)
2. **Review Logs**: Use `kubectl logs` to understand application behavior
3. **Modify Code**: Make changes and redeploy with `helm upgrade`
4. **Deploy to Cloud**: Follow [Azure AKS Setup Guide](setup-azure.md) or [Google GKE Setup Guide](setup-gke.md)
5. **Setup Monitoring**: Deploy Prometheus and Grafana for observability

---

## Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
- [Redpanda Documentation](https://docs.redpanda.com/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Setup Guide Version**: 1.0
**Last Updated**: 2026-02-15
**Maintained By**: Cloud Deploy Engineer Agent

*Generated following constitution.md v5.0 and phase5-spec.md v1.0*
