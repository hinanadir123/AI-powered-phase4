# Oracle Cloud Deployment Guide: Todo AI Chatbot on OKE (Always Free Tier)

## Overview

This document provides comprehensive instructions for deploying the Todo AI Chatbot to Oracle Kubernetes Engine (OKE) using Oracle's Always Free tier. The deployment includes Kafka event streaming, Dapr integration, PostgreSQL database, and production-grade ingress with HTTPS. The solution is designed to run within Oracle Cloud's Always Free limits while providing a fully functional production environment.

**Platform Choice:** Oracle OKE (Always Free) - Preferred for sustainable free deployment
**Duration:** 2-3 hours for full deployment
**Cost:** $0 USD (within Oracle Always Free limits)

## Prerequisites

### Oracle Cloud Requirements
- Oracle Cloud Free Tier account (Always Free eligible resources)
  - Sign up at: https://www.oracle.com/cloud/free/
  - Includes: 2 VM.Standard.A1.Flex instances (4 OCPUs, 24 GB memory, 400 GB storage)
- Oracle Cloud Infrastructure (OCI) CLI installed and configured
- Docker Desktop installed and running
- Domain name (optional) for HTTPS access

### Local Development Environment
- Git CLI (for version control)
- Helm 3.0+ (for package management)
- kubectl (for Kubernetes commands)
- Docker (for building container images)
- Python 3.6+ (for OCI CLI installation)

### Oracle OKE Free Tier Limits
- 4 OCPUs across all compute instances
- 24 GB memory across all compute instances
- 400 GB of attached block storage or 100 GB VM compute images (whichever is greater)
- Always Free tier is permanent as long as account remains active

## Oracle OKE Deployment (Primary) - Always Free

### 1. Prepare Oracle Cloud Account

#### 1.1 Install and Configure OCI CLI
```bash
# Option A: For Windows using PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.ps1'))"

# Option B: Using pip (if system supports it)
pip install oci-cli

# Verify installation
oci --version
```

#### 1.2 Configure OCI CLI
```bash
# Run the setup configuration wizard
oci setup config

# You'll be prompted for:
# - Config location: Accept default (~/.oci/config)
# - User OCID: Get from Oracle Cloud Console → Profile → User Settings
# - Tenancy OCID: Get from Oracle Cloud Console → Tenancy Details
# - Region: Select your preferred region (e.g., us-ashburn-1)
# - Generate key pair: Yes
# - Key location: Accept default
# - Passphrase: Press Enter (no passphrase for simplicity)
```

#### 1.3 Upload API Key to Oracle Cloud
```bash
# Find your public key (created by setup)
# Windows: C:\Users\<YourUsername>\.oci\oci_api_key_public.pem
# After setup, verify configuration works
oci iam region list
```
1. Copy contents of `oci_api_key_public.pem`
2. In Oracle Cloud Console → Profile → User Settings → API Keys → Add API Key
3. Paste the public key content

### 2. Create Oracle Resources

#### 2.1 Create Virtual Cloud Network (VCN)
```bash
# Create VCN with Internet Connectivity via Console
# In Oracle Cloud Console:
# 1. Navigate to Networking → Virtual Cloud Networks
# 2. Click "Start VCN Wizard"
# 3. Select "Create VCN with Internet Connectivity"
# 4. Enter details:
#    - VCN Name: "todo-vcn"
#    - Compartment: Your root compartment
#    - VCN CIDR: "10.0.0.0/16" (default)
#    - Public Subnet: "10.0.0.0/24" (default)
#    - Private Subnet: "10.0.1.0/24" (default)
# 5. Click "Next" → "Create"
```

#### 2.2 Create OKE Cluster (Always Free Tier Configuration)
```bash
# Create OKE cluster via Console with Free Tier resources
# In Oracle Cloud Console:
# 1. Navigate to Developer Services → Kubernetes Clusters (OKE)
# 2. Click "Create Cluster"
# 3. Select "Quick Create"
# 4. Enter cluster details:
#    - Name: "todo-cluster"
#    - Compartment: Your compartment
#    - Kubernetes Version: Latest stable (v1.28+)
#    - Kubernetes API Endpoint: Public Endpoint
#    - Node Type: Managed
#    - Worker Nodes: Public Workers
#    - Shape: VM.Standard.A1.Flex (ARM-based, Always Free eligible)
#    - OCPUs: 1 (per node - to stay within 4 total OCPU limit)
#    - Memory: 12 GB (per node)
#    - Number of Nodes: 2 (to stay within 24GB total memory limit)
#    - VCN: Select "todo-vcn" (created in step 2.1)
# 5. Click "Next" → "Create Cluster"
```

#### 2.3 Configure kubectl for OKE
Wait for cluster creation to complete (10-15 minutes), then:
```bash
# Get cluster's OCID from Console (click the cluster name)
# Use this command to configure kubectl (example):
oci ce cluster create-kubeconfig --cluster-id ocid1.cluster.oc1.iad.aaaaaaaaabbbbbbbbbbccccccccddddddeeeeeeffffff --file $HOME/.kube/config --region us-ashburn-1 --token-version 2.0.0

# Verify connectivity
kubectl get nodes
# Should show 2 worker nodes in "Ready" state
```

### 3. Install Dapr Runtime on OKE

#### 3.1 Add Dapr Helm Repository and Install Runtime
```bash
# Add and update Dapr Helm repository
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Create Dapr system namespace
kubectl create namespace dapr-system

# Install Dapr using Helm chart
helm install dapr dapr/dapr --namespace dapr-system --wait

# Verify Dapr installation
dapr status -k
# Should show 8 Dapr components as HEALTHY
```

### 4. Deploy Kafka to OKE (Redpanda Cloud Free Tier)

#### 4.1 Create Redpanda Cloud Account
```bash
# Sign up for Redpanda Cloud free tier
# 1. Go to https://redpanda.com/try-redpanda
# 2. Create an account
# 3. Create a free cluster:
#    - Name: "todo-cluster-free"
#    - Region: Closest to your OKE region
#    - Tier: Free (10GB/month)
# 4. Create required topics:
#    - `task-events` (3 partitions)
#    - `reminders` (3 partitions)
#    - `task-updates` (3 partitions)
# 5. Get connection credentials from Redpanda Console
```

#### 4.2 Create Kafka Connection Secrets
```bash
# Create Kubernetes secret with Redpanda connection details
kubectl create secret generic kafka-secrets \
  --from-literal=brokers='your-cluster.redpanda.com:9092' \
  --from-literal=username='your-sasl-username' \
  --from-literal=password='your-sasl-password'
```

### 5. Deploy Database to OKE (Oracle Autonomous Database)

#### 5.1 Create Oracle Autonomous Database (Always Free)
```bash
# In Oracle Cloud Console:
# 1. Navigate to Oracle Database → Autonomous Database
# 2. Click "Create Autonomous Database"
# 3. Enter details:
#    - Compartment: Your compartment
#    - Display Name: "todo-db"
#    - Database Name: "todoappdb"
#    - Workload Type: Transaction Processing
#    - Deployment Type: Shared Infrastructure
#    - Always Free: ENABLE (critical for free tier)
#    - Database Version: 19c or 21c
#    - OCPU Count: 1 (Always Free limit)
#    - Storage: 20 GB (Always Free limit)
#    - Password: Set a strong password (save it!)
#    - Network Access: Secure access from everywhere
# 4. Click "Create Autonomous Database"
```

#### 5.2 Create Database Connection Secret
```bash
# Create secret with database connection string
kubectl create secret generic postgres-secrets \
  --from-literal=connection-string='postgresql://admin:YourPassword@your-db-host.region.oraclecloudapps.com:1521/todoappdb_high'
```

### 6. Apply Dapr Components to OKE

#### 6.1 Verify Dapr Component Files Exist
Ensure the following files exist in `dapr-components/`:
- pubsub-kafka.yaml
- statestore-postgresql.yaml
- jobs-scheduler.yaml
- secretstore-kubernetes.yaml
- bindings-cron.yaml

#### 6.2 Update Kafka Dapr Component for Cloud
Update `dapr-components/pubsub-kafka.yaml`:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    secretKeyRef:
      name: kafka-secrets
      key: brokers
  - name: authType
    value: "password"
  - name: saslUsername
    secretKeyRef:
      name: kafka-secrets
      key: username
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: password
  - name: consumerGroup
    value: "todo-group"
  - name: disableTls
    value: "false"
  - name: version
    value: "2.8.0"
```

#### 6.3 Apply All Dapr Components
```bash
kubectl apply -f dapr-components/
# Verify components loaded
kubectl get components.dapr.io
```

### 7. Containerize and Push Images to Oracle Container Registry (OCIR)

#### 7.1 Configure OCIR Access
```bash
# Get your OCIR details:
# - Region Key: From Oracle documentation (e.g., 'iad' for us-ashburn-1)
# - Tenancy Namespace: In OCI Console → Tenancy Details → Object Storage Namespace

# Create Auth Token for OCIR access
# 1. In OCI Console → Profile → User Settings → Auth Tokens
# 2. Click "Generate Token"
# 3. Description: "OCIR Access Token"
# 4. Copy the token (will only show once!)
```

#### 7.2 Login to OCIR and Build Images
```bash
# Replace with your values
export REGION_KEY=iad  # Your region key
export TENANCY_NAMESPACE=your-tenancy-namespace  # From Console
export OCIR_REPO=${REGION_KEY}.ocir.io/${TENANCY_NAMESPACE}/todo

# Login to OCIR
docker login ${REGION_KEY}.ocir.io

# Build and tag images
docker build -t ${OCIR_REPO}/backend:latest -f backend/Dockerfile .
docker build -t ${OCIR_REPO}/frontend:latest -f frontend/Dockerfile .
docker build -t ${OCIR_REPO}/worker:latest -f backend/Dockerfile.worker .

# Push images to OCIR
docker push ${OCIR_REPO}/backend:latest
docker push ${OCIR_REPO}/frontend:latest
docker push ${OCIR_REPO}/worker:latest
```

### 8. Deploy Application to OKE

#### 8.1 Create Image Pull Secret
```bash
kubectl create secret docker-registry ocir-secret \
  --docker-server=${REGION_KEY}.ocir.io \
  --docker-username="${TENANCY_NAMESPACE}/oracleidentitycloudservice/your-email@example.com" \
  --docker-password="your-auth-token" \
  --docker-email="your-email@example.com"
```

#### 8.2 Update Helm Values for OKE Deployment
Create/modify `helm-values-oke.yaml` for OKE-specific configuration:

```yaml
# backend/values-oke.yaml
image:
  repository: iad.ocir.io/your-tenancy-namespace/todo/backend
  tag: latest
  pullPolicy: Always

imagePullSecrets:
  - name: ocir-secret

dapr:
  enabled: true
  appId: todo-backend
  config: daprConfig

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: postgres-secrets
        key: connection-string
  - name: KAFKA_BROKERS
    valueFrom:
      secretKeyRef:
        name: kafka-secrets
        key: brokers
```

#### 8.3 Deploy All Services with Helm
```bash
# Deploy database (if not using external)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql --set auth.postgresPassword=todo123 --set primary.persistence.enabled=false

# Deploy reminder worker (with Dapr annotations)
helm install reminder-worker charts/reminder-worker/ \
  --set image.repository=${OCIR_REPO}/worker \
  --set image.tag=latest \
  --set image.pullPolicy=Always \
  --set imagePullSecrets={ocir-secret} \
  --set dapr.appId=reminder-worker

# Deploy backend (with Dapr annotations and secrets)
helm install todo-backend charts/todo-backend/ \
  --set image.repository=${OCIR_REPO}/backend \
  --set image.tag=latest \
  --set image.pullPolicy=Always \
  --set imagePullSecrets={ocir-secret} \
  --set dapr.enabled=true \
  --set dapr.appId=todo-backend

# Deploy frontend (with Dapr annotations)
helm install todo-frontend charts/todo-frontend/ \
  --set image.repository=${OCIR_REPO}/frontend \
  --set image.tag=latest \
  --set image.pullPolicy=Always \
  --set imagePullSecrets={ocir-secret} \
  --set dapr.enabled=true \
  --set dapr.appId=todo-frontend
```

#### 8.4 Check Deployment Status
```bash
# Verify all pods are running with Dapr sidecars
kubectl get pods
# All pods should show "2/2" ready (app + Dapr sidecar)

# Check service status
kubectl get services

# Check deployment logs if needed
kubectl logs -l app=todo-backend -c todo-backend
kubectl logs -l app=todo-backend -c daprd  # Check Dapr logs too
```

### 9. Configure Ingress and TLS for HTTPS

#### 9.1 Deploy NGINX Ingress Controller
```bash
# Deploy NGINX Ingress Controller for OKE
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

#### 9.2 Install cert-manager for HTTPS Certificates
```bash
# Install cert-manager (prerequisite for Let's Encrypt)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager --timeout=300s -n cert-manager
```

#### 9.3 Create Certificate Issuer for Let's Encrypt
Create `letsencrypt-issuer.yaml`:
```yaml
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
```

```bash
kubectl apply -f letsencrypt-issuer.yaml
```

#### 9.4 Create Ingress Configuration with TLS
Create `todo-ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      # Enable websockets for real-time updates
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection $http_connection;
      # Dapr sidecar communication
      dapr-app-id: todo-backend
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - todo.yourdomain.com  # Replace with your domain
    secretName: todo-tls
  rules:
  - host: todo.yourdomain.com  # Replace with your domain
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
      - path: /daprsystem
        pathType: Prefix
        backend:
          service:
            name: dapr-dashboard
            port:
              number: 8080
```

#### 9.5 Apply Ingress Configuration
```bash
kubectl apply -f todo-ingress.yaml

# Get load balancer external IP
kubectl get svc -n ingress-nginx ingress-nginx-controller
# Note the EXTERNAL-IP (this is your public IP)
```

### 10. DNS Configuration
#### 10.1 Using Custom Domain (Recommended)
```bash
# If you have a custom domain:
# 1. Go to your DNS provider (GoDaddy, Namecheap, AWS Route 53, etc.)
# 2. Create an A record:
#    - Type: A
#    - Name: todo (or @ for root domain)
#    - Value: <EXTERNAL-IP from Step 9.5>
#    - TTL: 300

# Wait up to 48 hours for DNS propagation (usually 4-48 hours)
```

#### 10.2 HTTPS Certificate Validation
```bash
# Monitor certificate issuance (may take a few minutes)
kubectl describe certificate todo-tls -n default

# Check ingress status after certificate is issued
kubectl describe ingress todo-ingress -n default
# Should show that TLS/SSL certificate has been provisioned
```

## Google GKE Deployment (Alternative) with Free Credits

### Prerequisites for GKE
- Google Cloud account with $300 free trial credits
  - Sign up at: https://cloud.google.com/free
- gcloud CLI installed and configured
  - `gcloud auth login`
- Enable required APIs: `gcloud services enable container.googleapis.com`

### Create GKE Cluster
```bash
# Initialize gcloud CLI
gcloud init

# Create GKE cluster (within free credits - 3 nodes using f2-micro instances)
gcloud container clusters create todo-cluster \
  --num-nodes=2 \
  --machine-type=e2-micro \
  --zone=us-central1-a \
  --enable-autorepair \
  --enable-autoupgrade

# Get cluster credentials
gcloud container clusters get-credentials todo-cluster --zone=us-central1-a

# Verify connection
kubectl get nodes
```

### Follow Steps 3-10 Above with GKE-Specific Adjustments
- Skip VCN creation (Google manages networking)
- Use Google Container Registry (gcr.io) instead of OCIR
- Use Cloud SQL (free trial tier) instead of Oracle DB
- Use Google-managed certificates for HTTPS

## Verification Steps

### 1. Check All Kubernetes Resources
```bash
# Verify all pods are running (2/2 ready due to Dapr sidecars)
kubectl get pods -o wide

# Check services
kubectl get services

# Check Dapr components status
dapr status -k

# Check ingress status
kubectl get ingress

# Check secrets (sanitized view)
kubectl get secrets
```

### 2. Verify Application Health
```bash
# Check backend health endpoint
kubectl port-forward svc/todo-backend 8000:8000
curl http://localhost:8000/health
# Should return: {"status": "healthy", "kafka": "connected", "database": "connected"}

# Check if Kafka connection is working
kubectl logs -l app=todo-backend -c todo-backend
# Look for "Kafka connection established" or similar success message

# Check if Dapr sidecars are healthy
kubectl logs -l app=todo-backend -c daprd
# Look for successful component initialization
```

### 3. Test Public URL Access
```bash
# Get the ingress IP
kubectl get ingress

# Test with curl from command line
curl -k https://<your-domain-or-ip>/health
# Should return health status without SSL errors
```

### 4. Verify Features Work
- Navigate to the public URL
- Create tasks with various priority levels
- Add due dates and reminders
- Test recurring task creation
- Verify tag assignment and filtering
- Check sort functionality
- Verify that all Kafka events are processed correctly

### 5. Check Kafka and Dapr Integration
```bash
# Look for Kafka event logs
kubectl logs -l app=todo-backend -c todo-backend | grep "Kafka"

# Check if reminder worker is processing events
kubectl logs -l app=reminder-worker -c reminder-worker

# Check Dapr sidecar logs for pubsub operations
kubectl logs -l app=todo-backend -c daprd | grep pubsub
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Pods stuck in "ContainerCreating" state
```bash
# Check events for pod creation issues
kubectl get events --sort-by='.lastTimestamp'

# Check if image pull secret is correct
kubectl describe pod <pod-name>

# Solution: Verify OCIR credentials were entered correctly
```

#### Issue 2: Certificate not issued (TLS/SSL problems)
```bash
# Check cert-manager status
kubectl describe certificate todo-tls -n default

# Check ingress controller
kubectl logs -n ingress-nginx ingress-nginx-controller-*

# Verify DNS points to correct IP
nslookup your-domain.com
```

#### Issue 3: Kafka connectivity issues
```bash
# Check if Kafka secret is properly configured
kubectl describe secret kafka-secrets

# Verify connection from pod to Kafka
kubectl run test-kafka --image=busybox --rm -it -- sh
# Inside pod: nc -zv your-kafka-cluster.redpanda.com 9092
```

#### Issue 4: Database connection errors
```bash
# Check database secret content
kubectl describe secret postgres-secrets

# Test connection from backend pod
kubectl exec -it $(kubectl get pods -l app=todo-backend -o name | head -1) -c todo-backend -- env | grep DATABASE_URL
```

#### Issue 5: Dapr component errors
```bash
# Check for Dapr component loading errors
kubectl logs -l app=todo-backend -c daprd

# List Dapr components
kubectl get components.dapr.io

# Verify Dapr is working
kubectl exec -it <pod-name> -c daprd -- dapr health-check
```

#### Issue 6: Out of Memory or CPU Limits
```bash
# Check resource usage
kubectl top pods

# Check if pods are being OOMKilled
kubectl describe pods | grep -i "oom\|oomkilled\|memory"

# Scale down resources to stay within Always Free limits
kubectl patch deployment todo-backend -p '{"spec":{"resources":{"requests":{"memory":"256Mi","cpu":"250m"},"limits":{"memory":"512Mi","cpu":"500m"}}}}'
```

## Cleanup and Cost Management

### Important: Prevent Unexpected Charges
```bash
# Remove OKE cluster when not needed (stops billing)
# via Console: Developer Services → Kubernetes Clusters → Delete Cluster

# Delete load balancers to stop networking charges
kubectl delete ingress todo-ingress

# Clean up PVs and PVCs (may incur storage charges)
kubectl delete pvc --all

# Delete secrets containing sensitive data
kubectl delete secret kafka-secrets postgres-secrets ocir-secret
```

### Always Free Tier Monitoring
- Regularly check Oracle Cloud Console → Costs → Cost Analysis
- Set up budget alerts to monitor usage
- Verify that Always Free resources are being used (no overage charges)
- Consider stopping cluster during non-usage hours if needed

### Backup Strategy
```bash
# Backup production database periodically
# For Oracle Autonomous DB, use the Console → Backup tab

# Document current configuration for reproducibility
kubectl get all -o yaml > production-backup.yaml
```

## Final Verification

### Success Checklist
- [ ] Oracle OKE cluster with 2 Always Free nodes created and running
- [ ] All pods show "2/2" READY status (app + Dapr sidecar)
- [ ] Dapr runtime installed and all components HEALTHY
- [ ] Application accessible via HTTPS with valid Let's Encrypt certificate
- [ ] Backend returns health status successfully
- [ ] Frontend loads and all UI features work
- [ ] Kafka events are published and consumed (check logs)
- [ ] All Dapr components load without errors (pubsub, secrets, state)
- [ ] Reminder worker processes events (if implemented)
- [ ] TLS/SSL certificate is valid and active
- [ ] Ingress routes traffic correctly to backend and frontend
- [ ] All advanced features work (priorities, tags, due dates, reminders)
- [ ] Database connects successfully and maintains state
- [ ] Stay within Always Free tier limits ($0/month)

### Performance Validation
- [ ] Page load times under 3 seconds
- [ ] API endpoints respond within 500ms
- [ ] Kafka event processing latency under 1 second
- [ ] Application handles concurrent requests without errors

Your Todo AI Chatbot is now successfully deployed to Oracle OKE using Always Free tier resources and is accessible via HTTPS!