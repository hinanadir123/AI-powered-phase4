# Todo AI Chatbot - Step 4: Local Deployment (Minikube + Dapr + Kafka)

## Overview
This guide covers deploying the complete Todo AI Chatbot application with event-driven architecture using Minikube, Dapr, and Kafka.

## Architecture Components
- **Backend API**: FastAPI application with Dapr integration
- **Frontend UI**: React/Next.js application
- **Reminder Worker**: Background service for task reminders
- **PostgreSQL**: Database for persistent storage
- **Kafka (Strimzi)**: Message broker for event-driven communication
- **Dapr**: Distributed Application Runtime for microservice building blocks

## Deployment Steps

### 1. Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux) - **must be running**
- Minikube v1.32+
- kubectl v1.28+
- Helm v3.12+
- Dapr CLI v1.12+
- Git

### 2. Verify Prerequisites
```bash
docker --version
minikube version
kubectl version --client
helm version
dapr --version
```

### 3. Local Development Setup
To set up and run the application locally (not the Minikube deployment):

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

### 4. Deployment to Minikube (Complete Event-Driven Setup)

This script automatically handles the complete deployment:

1. Creates Minikube cluster with adequate resources
2. Installs Dapr runtime
3. Deploys Kafka using Strimzi operator
4. Creates required Kafka topics
5. Deploys PostgreSQL database
6. Applies Dapr components
7. Builds and deploys application services with Dapr sidecars
8. Sets up ingress for service access

To run the automated deployment:

```bash
# Make script executable (on Unix-like systems)
chmod +x ./setup-minikube-dapr-kafka.sh

# Run the deployment script
./setup-minikube-dapr-kafka.sh
```

> **Important**: Ensure Docker Desktop is running before executing the script!

> **Note**: If you're on Windows, you might need to run the script in PowerShell:
> ```powershell
> .\setup-minikube-dapr-kafka.ps1
> ```

### 5. Manual Deployment Steps (Alternative)

If you prefer manual deployment, follow these steps:

#### A. Start Minikube
```bash
minikube start --cpus=4 --memory=6144 --disk-size=20g --driver=docker
```

#### B. Install Dapr
```bash
dapr init -k
```

#### C. Install Strimzi Kafka Operator
```bash
helm repo add strimzi https://strimzi.io/charts/
helm install strimzi strimzi/strimzi-kafka-operator
```

#### D. Install PostgreSQL
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql --set auth.postgresPassword=postgres
```

#### E. Create Kafka Cluster and Topics
Create the Kafka cluster resource and required topics as in the script.

#### F. Apply Dapr Components
```bash
kubectl apply -f dapr-components/
```

#### G. Build Container Images and Deploy Application

Create Docker images, load them to Minikube and deploy all services.

### 6. Verification
After deployment, verify all components are healthy:

```bash
# Check Minikube status
minikube status

# Check Dapr status
dapr status -k

# Check Dapr components
dapr components -k

# Check Kafka pods
kubectl get pods -l strimzi.io/name=todo-kafka-cluster-kafka

# Check application pods
kubectl get pods

# Check Kafka topics
kubectl get kafkatopics

# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd
```

### 7. Accessing Services

Once deployed:
- All Kafka topics should be created and accessible
- All Dapr components should be loaded
- Application services should display healthy via their health endpoints
- Reminder worker should be processing tasks

### 8. Troubleshooting

**If Minikube fails with memory errors:**
```bash
# Try with lower memory
minikube start --cpus=2 --memory=6g --disk-size=10g --driver=docker
```

**If Docker connection errors occur:**
- Verify Docker Desktop is running
- On Windows, ensure WSL2 backend is enabled for Docker Desktop
- Try `docker context ls` and ensure proper context

**If Dapr components fail to load:**
- Verify Dapr runtime is installed: `dapr status -k`
- Check Dapr system pods: `kubectl get pods -n dapr-system`

### 9. Local Development Commands

When developing locally without Minikube:

```bash
# Run backend with Dapr
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --app-protocol http python -m uvicorn main:app --reload

# Run reminder worker with Dapr
dapr run --app-id reminder-worker --app-port 8080 --app-protocol http -- python reminder_worker.py
```

### 10. Environment Variables

Required for local development:
- `DATABASE_URL` (PostgreSQL connection string)
- Connection details for Kafka (handled by Dapr)

---

## Kafka Topics Used

- `task-events`: Task lifecycle events (created, updated, deleted, completed)
- `reminders`: Reminder scheduling and notifications
- `task-updates`: Real-time task synchronization for frontend
- `task-events-dlq`: Dead letter queue for failed task events
- `reminders-dlq`: Dead letter queue for failed reminders
- `task-updates-dlq`: Dead letter queue for failed updates

## Dapr Components Used

- `pubsub-kafka`: Kafka messaging pub/sub
- `statestore-postgresql`: PostgreSQL state management
- `dapr-jobs`: Jobs API for scheduled tasks
- `kubernetes-secret-store`: Kubernetes secrets access

For a full production deployment guide, see the cloud deployment section in Phase 5.

## Success Criteria

The deployment is successful when:
- ✅ All pods are running and healthy
- ✅ Dapr sidecars injected successfully
- ✅ All Kafka topics created and accessible
- ✅ Dapr components loaded and healthy
- ✅ Reminder worker connected to message queues
- ✅ All advanced and intermediate features working
- ✅ Event-driven architecture functioning properly