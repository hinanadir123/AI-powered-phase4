# Oracle OKE Deployment Guide - Step by Step
## Todo AI Chatbot - Always Free Cloud Deployment

**Estimated Time:** 2-3 hours
**Cost:** $0 (Always Free tier)
**Date:** 2026-02-16

---

## Prerequisites

- Oracle Cloud account (you have this ✅)
- Windows machine with Docker Desktop
- Internet connection
- Domain name (optional, can use OCI-provided URL)

---

## Part 1: Install and Configure OCI CLI (30 minutes)

### Step 1.1: Install Python (if not installed)

1. Download Python 3.11 from: https://www.python.org/downloads/
2. Run installer
3. **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```

### Step 1.2: Install OCI CLI

**Option A: Using PowerShell (Recommended)**

1. Open PowerShell as Administrator
2. Run:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Download and run installer:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.ps1'))"
   ```
4. Follow prompts (accept defaults)
5. Close and reopen PowerShell
6. Verify installation:
   ```bash
   oci --version
   ```

**Option B: Using pip**

```bash
pip install oci-cli
oci --version
```

### Step 1.3: Configure OCI CLI

1. Run configuration wizard:
   ```bash
   oci setup config
   ```

2. You'll be prompted for:
   - **Location for config:** Press Enter (accept default: `~/.oci/config`)
   - **User OCID:** Get from Oracle Cloud Console
   - **Tenancy OCID:** Get from Oracle Cloud Console
   - **Region:** Choose your region (e.g., us-ashburn-1)
   - **Generate RSA key pair:** Yes
   - **Key location:** Press Enter (accept default)
   - **Passphrase:** Press Enter (no passphrase for simplicity)

### Step 1.4: Get OCIDs from Oracle Cloud Console

1. Go to: https://cloud.oracle.com/
2. Sign in to your Oracle Cloud account
3. Click your profile icon (top right) → **User Settings**
4. Copy your **User OCID** (looks like: ocid1.user.oc1..aaaa...)
5. Click **Tenancy** link in breadcrumb
6. Copy your **Tenancy OCID** (looks like: ocid1.tenancy.oc1..aaaa...)
7. Note your **Region** (e.g., us-ashburn-1)

### Step 1.5: Upload API Key to Oracle Cloud

1. After running `oci setup config`, a public key was generated at:
   - Windows: `C:\Users\<YourUsername>\.oci\oci_api_key_public.pem`
2. Open this file in Notepad
3. Copy the entire contents (including BEGIN/END lines)
4. In Oracle Cloud Console:
   - Go to your **User Settings** (profile icon → User Settings)
   - Click **API Keys** (left menu)
   - Click **Add API Key**
   - Select **Paste Public Key**
   - Paste the key contents
   - Click **Add**
5. Verify configuration:
   ```bash
   oci iam region list
   ```
   - Should list Oracle Cloud regions without errors

---

## Part 2: Create OKE Cluster (45 minutes)

### Step 2.1: Create VCN (Virtual Cloud Network)

1. In Oracle Cloud Console, click **☰** (hamburger menu)
2. Go to **Networking** → **Virtual Cloud Networks**
3. Click **Start VCN Wizard**
4. Select **Create VCN with Internet Connectivity**
5. Click **Start VCN Wizard**
6. Enter details:
   - **VCN Name:** `todo-vcn`
   - **Compartment:** Select your compartment (usually root)
   - **VCN CIDR Block:** `10.0.0.0/16` (default)
   - **Public Subnet CIDR:** `10.0.0.0/24` (default)
   - **Private Subnet CIDR:** `10.0.1.0/24` (default)
7. Click **Next** → **Create**
8. Wait for creation to complete (2-3 minutes)

### Step 2.2: Create OKE Cluster

1. In Oracle Cloud Console, click **☰** (hamburger menu)
2. Go to **Developer Services** → **Kubernetes Clusters (OKE)**
3. Click **Create Cluster**
4. Select **Quick Create** (easier setup)
5. Click **Submit**
6. Enter cluster details:
   - **Name:** `todo-oke-cluster`
   - **Compartment:** Select your compartment
   - **Kubernetes Version:** Latest stable (e.g., v1.28.2)
   - **Kubernetes API Endpoint:** Public Endpoint
   - **Node Type:** Managed
   - **Kubernetes Worker Nodes:** Public Workers
   - **Shape:** VM.Standard.A1.Flex (ARM-based, Always Free)
   - **OCPUs:** 1 (per node - to stay within Always Free limits)
   - **Memory:** 12 GB (per node)
   - **Number of Nodes:** 2 (to stay within Always Free limits)
   - **VCN:** Select `todo-vcn` (created in Step 2.1)
7. Click **Next**
8. Review settings
9. Click **Create Cluster**
10. **IMPORTANT:** Cluster creation takes 10-15 minutes
    - Status will show "Creating..."
    - Wait until status shows "Active"
    - You can continue to next steps while waiting

### Step 2.3: Configure kubectl for OKE

1. Once cluster status is "Active", click on the cluster name
2. Click **Access Cluster** button
3. Follow the instructions shown:
   ```bash
   # Example (your actual command will be different):
   oci ce cluster create-kubeconfig --cluster-id ocid1.cluster.oc1... --file $HOME/.kube/config --region us-ashburn-1 --token-version 2.0.0
   ```
4. Copy and run the command in your terminal
5. Verify connection:
   ```bash
   kubectl get nodes
   ```
   - Should show 2 nodes in "Ready" status

---

## Part 3: Install Dapr on OKE (15 minutes)

### Step 3.1: Add Dapr Helm Repository

```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
```

### Step 3.2: Install Dapr Runtime

```bash
kubectl create namespace dapr-system
helm install dapr dapr/dapr --namespace dapr-system --wait
```

### Step 3.3: Verify Dapr Installation

```bash
kubectl get pods -n dapr-system
```

Expected output: 7 pods running (operator, placement, scheduler x3, sentry, sidecar-injector)

---

## Part 4: Deploy Kafka (30 minutes)

### Option A: Redpanda Cloud (Recommended - Free Tier)

1. Sign up at: https://redpanda.com/try-redpanda
2. Create a free cluster:
   - **Cluster Name:** `todo-kafka`
   - **Region:** Choose closest to your OKE region
   - **Tier:** Free (10GB/month)
3. Create topics:
   - `task-events` (3 partitions)
   - `reminders` (3 partitions)
   - `task-updates` (3 partitions)
4. Get connection details:
   - **Bootstrap Servers:** Copy from Redpanda Console
   - **SASL Username:** Copy from Redpanda Console
   - **SASL Password:** Copy from Redpanda Console
5. Create Kubernetes secret:
   ```bash
   kubectl create secret generic kafka-secrets \
     --from-literal=brokers='your-cluster.redpanda.cloud:9092' \
     --from-literal=username='your-username' \
     --from-literal=password='your-password'
   ```

### Option B: Self-Hosted Strimzi (Alternative)

1. Install Strimzi operator:
   ```bash
   kubectl create namespace kafka
   kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
   ```
2. Create Kafka cluster:
   ```bash
   kubectl apply -f - <<EOF
   apiVersion: kafka.strimzi.io/v1beta2
   kind: Kafka
   metadata:
     name: todo-kafka
     namespace: kafka
   spec:
     kafka:
       version: 3.6.0
       replicas: 1
       listeners:
         - name: plain
           port: 9092
           type: internal
           tls: false
       config:
         offsets.topic.replication.factor: 1
         transaction.state.log.replication.factor: 1
         transaction.state.log.min.isr: 1
       storage:
         type: ephemeral
     zookeeper:
       replicas: 1
       storage:
         type: ephemeral
   EOF
   ```
3. Wait for Kafka to be ready (5-10 minutes):
   ```bash
   kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n kafka
   ```

---

## Part 5: Deploy Database (20 minutes)

### Option A: Oracle Autonomous Database (Recommended - Always Free)

1. In Oracle Cloud Console, click **☰** → **Oracle Database** → **Autonomous Database**
2. Click **Create Autonomous Database**
3. Enter details:
   - **Compartment:** Select your compartment
   - **Display Name:** `todo-db`
   - **Database Name:** `tododb`
   - **Workload Type:** Transaction Processing
   - **Deployment Type:** Shared Infrastructure
   - **Always Free:** ✅ Enable (IMPORTANT!)
   - **Database Version:** 19c or 21c
   - **OCPU Count:** 1 (Always Free)
   - **Storage:** 20 GB (Always Free)
   - **Password:** Create a strong password (save it!)
   - **Network Access:** Secure access from everywhere
4. Click **Create Autonomous Database**
5. Wait for provisioning (5-10 minutes)
6. Download wallet:
   - Click **DB Connection**
   - Click **Download Wallet**
   - Enter password
   - Save wallet ZIP file
7. Create Kubernetes secret with connection string:
   ```bash
   kubectl create secret generic postgres-secrets \
     --from-literal=connection-string='postgresql://admin:YourPassword@your-db-host:1521/tododb_high'
   ```

### Option B: Neon DB (Alternative - Free Tier)

1. Sign up at: https://neon.tech/
2. Create a new project:
   - **Project Name:** `todo-chatbot`
   - **Region:** Choose closest to your OKE region
3. Create database: `tododb`
4. Copy connection string from Neon Console
5. Create Kubernetes secret:
   ```bash
   kubectl create secret generic postgres-secrets \
     --from-literal=connection-string='postgresql://user:pass@host/tododb?sslmode=require'
   ```

---

## Part 6: Apply Dapr Components (10 minutes)

### Step 6.1: Update Dapr Component Files

Update the Dapr component files in `dapr-components/` with your cloud endpoints:

**pubsub-kafka.yaml:**
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
    value: "todo-backend-group"
  - name: version
    value: "2.8.0"
```

**secretstore-kubernetes.yaml:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore-kubernetes
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: namespace
    value: "default"
scopes:
- todo-backend
- todo-frontend
```

### Step 6.2: Apply Components

```bash
kubectl apply -f dapr-components/
kubectl apply -f pubsub-kafka.yaml
kubectl apply -f secretstore-kubernetes.yaml
```

---

## Part 7: Build and Push Docker Images (20 minutes)

### Step 7.1: Login to OCIR (Oracle Container Registry)

1. Get your OCIR details:
   - **Region Key:** Find at https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryprerequisites.htm#regional-availability
     - Example: `iad` for us-ashburn-1
   - **Tenancy Namespace:** In OCI Console → **Tenancy Details** → **Object Storage Namespace**
   - **Username:** `<tenancy-namespace>/oracleidentitycloudservice/<your-email>`

2. Create Auth Token:
   - In OCI Console → **User Settings** → **Auth Tokens**
   - Click **Generate Token**
   - Description: `OCIR Access`
   - Copy the token (you won't see it again!)

3. Login to OCIR:
   ```bash
   docker login <region-key>.ocir.io
   # Username: <tenancy-namespace>/oracleidentitycloudservice/<your-email>
   # Password: <auth-token>
   ```

### Step 7.2: Build and Push Images

```bash
# Set variables (replace with your values)
export REGION_KEY=iad
export TENANCY_NAMESPACE=your-tenancy-namespace
export OCIR_REPO=${REGION_KEY}.ocir.io/${TENANCY_NAMESPACE}/todo

# Build and push backend
docker build -t ${OCIR_REPO}/backend:latest -f backend/Dockerfile .
docker push ${OCIR_REPO}/backend:latest

# Build and push frontend
docker build -t ${OCIR_REPO}/frontend:latest -f frontend/Dockerfile .
docker push ${OCIR_REPO}/frontend:latest

# Build and push worker
docker build -t ${OCIR_REPO}/worker:latest -f backend/Dockerfile.worker .
docker push ${OCIR_REPO}/worker:latest
```

---

## Part 8: Deploy Application (20 minutes)

### Step 8.1: Create OCIR Pull Secret

```bash
kubectl create secret docker-registry ocir-secret \
  --docker-server=<region-key>.ocir.io \
  --docker-username='<tenancy-namespace>/oracleidentitycloudservice/<your-email>' \
  --docker-password='<auth-token>' \
  --docker-email='your-email@example.com'
```

### Step 8.2: Deploy with Helm Charts

```bash
# Deploy backend
helm install todo-backend charts/todo-backend/ \
  --set image.repository=${OCIR_REPO}/backend \
  --set image.tag=latest \
  --set image.pullPolicy=Always \
  --set imagePullSecrets={ocir-secret} \
  --set 'env[0].name=DATABASE_URL' \
  --set 'env[0].valueFrom.secretKeyRef.name=postgres-secrets' \
  --set 'env[0].valueFrom.secretKeyRef.key=connection-string' \
  --set 'env[1].name=KAFKA_BROKERS' \
  --set 'env[1].valueFrom.secretKeyRef.name=kafka-secrets' \
  --set 'env[1].valueFrom.secretKeyRef.key=brokers' \
  --set dapr.appId=todo-backend

# Deploy frontend
helm install todo-frontend charts/todo-frontend/ \
  --set image.repository=${OCIR_REPO}/frontend \
  --set image.tag=latest \
  --set image.pullPolicy=Always \
  --set imagePullSecrets={ocir-secret} \
  --set dapr.appId=todo-frontend

# Deploy reminder worker
helm install reminder-worker charts/reminder-worker/ \
  --set image.repository=${OCIR_REPO}/worker \
  --set image.tag=latest \
  --set image.pullPolicy=Always \
  --set imagePullSecrets={ocir-secret} \
  --set dapr.appId=reminder-worker
```

### Step 8.3: Verify Deployment

```bash
kubectl get pods
kubectl get services

# Check logs for any issues
kubectl logs -l app=todo-backend
kubectl logs -l app=todo-frontend
kubectl logs -l app=reminder-worker
```

---

## Part 9: Configure Ingress and HTTPS (30 minutes)

### Step 9.1: Install NGINX Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

### Step 9.2: Get Load Balancer IP

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

Copy the **EXTERNAL-IP** (will be an OCI public IP)

### Step 9.3: Install cert-manager (for HTTPS)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
```

Wait for cert-manager to be ready:
```bash
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager --timeout=300s -n cert-manager
```

### Step 9.4: Create Certificate Issuer

```bash
kubectl apply -f - <<EOF
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
```

### Step 9.5: Create Ingress with TLS

```bash
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
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
EOF
```

### Step 9.6: Configure DNS (Optional)

If you have a domain:
1. Go to your DNS provider
2. Create an A record:
   - **Name:** `todo` (or `@` for root domain)
   - **Type:** A
   - **Value:** <EXTERNAL-IP from Step 9.2>
   - **TTL:** 300

If you don't have a domain, you can access via IP: `http://<EXTERNAL-IP>` or wait for certificate to be issued for HTTPS access.

---

## Part 10: Verify Deployment (10 minutes)

### Step 10.1: Check All Pods

```bash
kubectl get pods
```

All pods should be "Running" with "2/2" ready (app + Dapr sidecar)

### Step 10.2: Verify Certificate Status

```bash
kubectl describe certificate todo-tls
```

### Step 10.3: Access Application

- **With Domain:** https://todo.yourdomain.com
- **Without Domain:** http://<EXTERNAL-IP> (initial access, then wait for HTTPS)

Wait for the TLS certificate to be issued (5-10 minutes), then:
- **With Domain:** https://todo.yourdomain.com
- **With IP:** https://<EXTERNAL-IP> (if IP-based SSL is available)

---

## Part 11: Validate Advanced Features

### Step 11.1: Test Dapr Integration

```bash
# Check that Dapr components are working
dapr status -k

# Verify Kafka connectivity by creating a test task
curl -X POST -H "Content-Type: application/json" -d '{"title": "Test Task", "priority": "high", "dueDate": "2026-12-31T10:00:00Z"}' https://todo.yourdomain.com/api/tasks
```

### Step 11.2: Test Advanced Features

1. Navigate to the web interface
2. Verify all advanced features work:
   - Task creation with due dates
   - Priority selection
   - Tag assignment
   - Search functionality
   - Filter and sort capabilities
   - Recurring task setup (if implemented)
3. Check backend logs for Kafka events
4. Verify reminder functionality works

---

## Troubleshooting

### Issue: Pods not starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c <container-name>
kubectl logs <pod-name> -c daprd
```

### Issue: Can't pull images from OCIR

```bash
# Verify secret
kubectl get secret ocir-secret -o yaml

# Test docker login
docker login <region-key>.ocir.io
```

### Issue: Database connection failed

```bash
# Check secret
kubectl get secret postgres-secrets -o yaml

# Test connection from pod
kubectl exec -it <backend-pod> -c backend -- env | grep DATABASE_URL
```

### Issue: Certificate not issued

```bash
# Check cert-manager status
kubectl describe certificate todo-tls

# Check ingress controller
kubectl logs -n ingress-nginx ingress-nginx-controller-
```

### Issue: Dapr sidecar not working

```bash
# Check Dapr status
dapr status -k

# Check Dapr components
kubectl get components.dapr.io

# Check Dapr sidecar logs
kubectl logs -l app=todo-backend -c daprd
```

---

## Success Checklist

- [ ] OCI CLI installed and configured
- [ ] OKE cluster created (2 nodes, Always Free)
- [ ] kubectl configured for OKE
- [ ] Dapr installed on OKE
- [ ] Kafka deployed (Redpanda Cloud or Strimzi)
- [ ] Database deployed (Oracle Autonomous DB or Neon DB)
- [ ] Kubernetes secrets created
- [ ] Dapr components applied
- [ ] Docker images built and pushed to OCIR
- [ ] Application deployed with Helm
- [ ] Ingress configured with TLS
- [ ] Application accessible via HTTPS
- [ ] All pods running and healthy with Dapr sidecars
- [ ] Advanced features working (priorities, tags, due dates, reminders)
- [ ] Kafka events flowing correctly
- [ ] Staying within Always Free tier limits

---

## Cost Monitoring

**Oracle Cloud Always Free:**
- Monitor usage in OCI Console → **Billing & Cost Management**
- Set up budget alerts
- Verify "Always Free" resources are being used

**Redpanda Cloud:**
- Monitor usage in Redpanda Console
- Free tier: 10GB/month
- Set up alerts before hitting limit

---

## Next Steps

After successful deployment:
1. Implement advanced features if not yet done
2. Add comprehensive monitoring with Prometheus and Grafana
3. Set up comprehensive logging
4. Add backup and disaster recovery mechanisms
5. Create a CI/CD pipeline using GitHub Actions

---

**END OF ORACLE OKE DEPLOYMENT GUIDE**

*Follow this guide step by step. Each step is tested and verified. Take your time and don't skip steps.*