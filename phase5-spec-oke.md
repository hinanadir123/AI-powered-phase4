# Phase 5 Specification: Cloud Deployment with Kafka and Dapr
## Todo AI Chatbot - Oracle OKE Always Free Deployment

**Version:** v1.0
**Date:** 2026-02-16
**Based on:** constitution.md v5.0
**Status:** Active

---

## 1. Objective

Deploy the Todo AI Chatbot to production using Oracle Cloud Infrastructure (OCI) Always Free tier with event-driven architecture powered by Kafka and Dapr.

### Primary Goals
1. **Local Development**: Deploy on Minikube with Dapr + Kafka for testing
2. **Cloud Production**: Deploy to Oracle OKE (Always Free tier) for permanent hosting
3. **Event-Driven Architecture**: Use Kafka for async messaging via Dapr Pub/Sub
4. **Zero Cost**: Utilize only free-tier resources (Oracle Always Free, Redpanda Cloud free tier)
5. **CI/CD**: Automated deployment with GitHub Actions

---

## 2. Scope & Assumptions

### In-Scope

**Part B - Local Deployment:**
- Minikube cluster with Dapr runtime
- Kafka (Redpanda Docker or Strimzi operator)
- PostgreSQL database (local or Neon DB free tier)
- Dapr components (Pub/Sub, State, Bindings, Secrets, Service Invocation)
- Application deployment with Helm

**Part C - Cloud Deployment:**
- Oracle OKE cluster (Always Free: 4 OCPUs, 24GB RAM)
- Kafka (Redpanda Cloud free tier or self-hosted Strimzi)
- PostgreSQL (Oracle Autonomous Database free tier or Neon DB)
- Dapr components configured for cloud
- HTTPS ingress with TLS
- CI/CD with GitHub Actions

**Infrastructure:**
- Kafka topics: task-events, reminders, task-updates
- Dapr Pub/Sub for event publishing/consuming
- Dapr State Store for caching
- Dapr Bindings for cron jobs (reminders)
- Dapr Secrets for credentials
- Dapr Service Invocation for frontend-backend communication

### Out-of-Scope
- Azure AKS or Google GKE (use Oracle OKE only)
- Alternative Pub/Sub systems (unless Kafka access issues)
- Advanced features (priorities, tags, search) - focus on core deployment
- Multi-tenancy and user authentication

### Assumptions
1. Phase 4 local Minikube deployment exists
2. Oracle Cloud account created (Always Free tier)
3. Redpanda Cloud free tier account or ability to self-host Kafka
4. GitHub repository for CI/CD
5. Docker Desktop installed locally
6. Basic Kubernetes knowledge

---

## 3. Functional Requirements

### 3.1 Local Minikube Deployment

**Prerequisites:**
- Minikube 1.32+
- kubectl 1.28+
- Helm 3.12+
- Docker Desktop
- 6-8GB RAM allocated to Docker

**Components:**
1. **Dapr Runtime**
   - Install via Helm: `helm install dapr dapr/dapr --namespace dapr-system`
   - Version: 1.12+

2. **Kafka (Redpanda)**
   - Deploy via Helm: `helm install redpanda redpanda/redpanda`
   - Single replica for development
   - Topics: task-events (3 partitions), reminders (3 partitions), task-updates (3 partitions)

3. **PostgreSQL**
   - Deploy via Helm: `helm install postgres bitnami/postgresql`
   - Database: tododb
   - User: todouser
   - Connection: `postgresql://todouser:todopass@postgres-postgresql:5432/tododb?sslmode=disable`

4. **Dapr Components**
   - Pub/Sub (Kafka): For event messaging
   - State Store (PostgreSQL): For caching (optional)
   - Bindings (Cron): For scheduled reminders
   - Secrets (Kubernetes): For credentials
   - Service Invocation: For frontend-backend calls

5. **Application Services**
   - Backend: FastAPI with Dapr sidecar
   - Frontend: Next.js with Dapr sidecar
   - Worker: Reminder processor with Dapr sidecar

**Deployment Steps:**
1. Start Minikube with 6GB memory
2. Install Dapr runtime
3. Deploy Kafka (Redpanda)
4. Deploy PostgreSQL
5. Create Kubernetes secrets
6. Apply Dapr components
7. Deploy application with Helm
8. Port-forward for local access

### 3.2 Oracle OKE Cloud Deployment

**Oracle Cloud Always Free Resources:**
- **Compute**: 4 OCPUs (ARM-based Ampere A1)
- **Memory**: 24GB RAM
- **Storage**: 200GB block storage
- **Network**: 10TB outbound data transfer/month
- **Load Balancer**: 1 flexible load balancer

**OKE Cluster Configuration:**
- **Node Pool**: 2 nodes (2 OCPUs, 12GB RAM each)
- **Kubernetes Version**: Latest stable
- **Network**: VCN with public subnet
- **Shape**: VM.Standard.A1.Flex (ARM-based, free tier)

**Components:**
1. **Dapr Runtime**
   - Install via Helm on OKE cluster
   - Configure for production (resource limits, replicas)

2. **Kafka**
   - Option A: Redpanda Cloud free tier (10GB/month)
   - Option B: Self-hosted Strimzi on OKE (uses free compute)
   - Topics: task-events, reminders, task-updates

3. **PostgreSQL**
   - Option A: Oracle Autonomous Database (Always Free: 20GB)
   - Option B: Neon DB free tier (10GB)
   - Connection via Kubernetes secret

4. **Dapr Components**
   - Update broker endpoints for cloud Kafka
   - Update database connection strings
   - Configure secrets for production

5. **Application Services**
   - Build Docker images and push to OCIR (Oracle Container Registry - free)
   - Deploy with Helm charts
   - Configure resource limits for free tier

6. **Ingress & TLS**
   - NGINX Ingress Controller
   - cert-manager for Let's Encrypt certificates
   - Custom domain or OCI-provided domain

**Deployment Steps:**
1. Create OKE cluster via OCI Console or Terraform
2. Configure kubectl with OKE credentials
3. Install Dapr runtime
4. Deploy Kafka (Redpanda Cloud or Strimzi)
5. Create Oracle Autonomous Database or use Neon DB
6. Create Kubernetes secrets for credentials
7. Apply Dapr components with cloud endpoints
8. Build and push Docker images to OCIR
9. Deploy application with Helm
10. Configure ingress and DNS
11. Verify HTTPS access

### 3.3 Kafka Event Architecture

**Topics:**
1. **task-events** (3 partitions)
   - Events: task.created, task.updated, task.deleted, task.completed
   - Producers: Backend API
   - Consumers: Reminder worker, analytics service

2. **reminders** (3 partitions)
   - Events: reminder.scheduled, reminder.triggered
   - Producers: Reminder worker
   - Consumers: Notification service

3. **task-updates** (3 partitions)
   - Events: task.sync (real-time updates)
   - Producers: Backend API
   - Consumers: Frontend (via WebSocket or polling)

**Event Schema (CloudEvents v1.0):**
```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "todo-backend",
  "id": "uuid",
  "time": "2026-02-16T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": "123",
    "title": "Task title",
    "status": "pending"
  }
}
```

**Dapr Pub/Sub Integration:**
- Backend publishes via: `POST http://localhost:3500/v1.0/publish/pubsub-kafka/task-events`
- Worker subscribes via: Dapr subscription endpoint
- No direct Kafka SDK imports required

---

## 4. Non-Functional Requirements

### 4.1 Event-Driven Decoupling
- All async operations use Kafka via Dapr Pub/Sub
- Services communicate via events, not direct HTTP calls
- Loose coupling enables independent scaling

### 4.2 Scalability
- OKE: Horizontal pod autoscaling (HPA) based on CPU
- Kafka: 3 partitions per topic for parallel processing
- Stateless services for easy replication

### 4.3 Resilience
- Liveness and readiness probes for all pods
- Automatic pod restart on failure
- Kafka consumer groups for fault tolerance
- Retry policies with exponential backoff

### 4.4 Observability
- **Logging**: kubectl logs or OCI Logging (free tier)
- **Metrics**: Prometheus + Grafana (optional)
- **Monitoring**: OCI Monitoring (free tier)
- **Alerting**: OCI Notifications (free tier)

### 4.5 Security
- HTTPS only (TLS via Let's Encrypt)
- Secrets stored in Kubernetes Secrets
- Dapr Secret Store for API keys
- OKE RBAC for access control
- Network policies for pod-to-pod communication

### 4.6 Cost Optimization
- Use Oracle Always Free tier (no expiration)
- Use Redpanda Cloud free tier (10GB/month)
- Use Neon DB free tier (10GB)
- Set resource limits to stay within free quotas
- Monitor usage via OCI Console

---

## 5. Architecture Overview

### 5.1 Local Minikube Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser (localhost)                  │
└────────────────────────────┬────────────────────────────────┘
                             │ Port-forward
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Minikube Cluster                          │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ Frontend Pod     │         │ Backend Pod      │          │
│  │ ┌──────────────┐ │         │ ┌──────────────┐ │          │
│  │ │ Next.js      │ │         │ │ FastAPI      │ │          │
│  │ └──────┬───────┘ │         │ └──────┬───────┘ │          │
│  │ ┌──────▼───────┐ │         │ ┌──────▼───────┐ │          │
│  │ │ Dapr Sidecar │◄┼─────────┼─┤ Dapr Sidecar │ │          │
│  │ └──────────────┘ │         │ └──────┬───────┘ │          │
│  └──────────────────┘         └────────┼─────────┘          │
│                                         │                    │
│                                         ▼                    │
│                    ┌────────────────────────────┐            │
│                    │ Kafka (Redpanda)           │            │
│                    │ Topics:                    │            │
│                    │ - task-events              │            │
│                    │ - reminders                │            │
│                    │ - task-updates             │            │
│                    └────────────┬───────────────┘            │
│                                 │                            │
│                                 ▼                            │
│                    ┌────────────────────────────┐            │
│                    │ Worker Pod                 │            │
│                    │ ┌────────────────────────┐ │            │
│                    │ │ Reminder Processor     │ │            │
│                    │ └──────┬─────────────────┘ │            │
│                    │ ┌──────▼─────────────────┐ │            │
│                    │ │ Dapr Sidecar           │ │            │
│                    │ └────────────────────────┘ │            │
│                    └────────────┬───────────────┘            │
│                                 │                            │
│                                 ▼                            │
│                    ┌────────────────────────────┐            │
│                    │ PostgreSQL                 │            │
│                    │ Database: tododb           │            │
│                    └────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Oracle OKE Cloud Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet Users                            │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    OCI Load Balancer (Free)                  │
│                    TLS Termination                           │
└────────────────────────────┬────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                    Oracle OKE Cluster                        │
│                    (4 OCPUs, 24GB RAM - Always Free)         │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ Frontend Pod     │         │ Backend Pod      │          │
│  │ ┌──────────────┐ │         │ ┌──────────────┐ │          │
│  │ │ Next.js      │ │         │ │ FastAPI      │ │          │
│  │ └──────┬───────┘ │         │ └──────┬───────┘ │          │
│  │ ┌──────▼───────┐ │         │ ┌──────▼───────┐ │          │
│  │ │ Dapr Sidecar │◄┼─────────┼─┤ Dapr Sidecar │ │          │
│  │ └──────────────┘ │         │ └──────┬───────┘ │          │
│  └──────────────────┘         └────────┼─────────┘          │
│                                         │                    │
└─────────────────────────────────────────┼────────────────────┘
                                          │
                                          ▼
                    ┌────────────────────────────────┐
                    │ Redpanda Cloud (Free Tier)     │
                    │ or Strimzi on OKE              │
                    │ Topics: task-events, reminders │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────┐
                    │ Oracle Autonomous DB (Free)    │
                    │ or Neon DB (Free Tier)         │
                    │ 20GB / 10GB storage            │
                    └────────────────────────────────┘
```

---

## 6. Dapr Components Configuration

### 6.1 Pub/Sub Component (pubsub-kafka.yaml)

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
  # Kafka brokers (update for cloud)
  - name: brokers
    value: "redpanda-0.redpanda.default.svc.cluster.local:9092"  # Local
    # value: "your-cluster.redpanda.cloud:9092"  # Cloud
  - name: consumerGroup
    value: "todo-backend-group"
  - name: clientId
    value: "todo-backend"
  - name: authType
    value: "none"  # or "password" for cloud
  - name: consumeRetryInterval
    value: "200ms"
  - name: initialOffset
    value: "newest"
scopes:
- todo-backend
- todo-worker
```

### 6.2 State Store Component (statestore-postgresql.yaml)

**Note:** This component is OPTIONAL. Only use if you need Dapr state management. For basic deployment, skip this component.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-postgresql
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secrets
      key: connection-string
  - name: tableName
    value: "dapr_state"
scopes:
- todo-backend
```

### 6.3 Bindings Component (bindings-cron.yaml)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: bindings-cron-reminder-check
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "*/5 * * * *"  # Every 5 minutes
  - name: direction
    value: "input"
scopes:
- todo-worker
```

### 6.4 Secret Store Component (secretstore-kubernetes.yaml)

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

---

## 7. CI/CD Pipeline

### 7.1 GitHub Actions Workflow

**File:** `.github/workflows/deploy-oke.yml`

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Jobs:**
1. **Build**: Build Docker images and push to OCIR
2. **Test**: Run unit and integration tests
3. **Deploy**: Deploy to OKE with Helm

**Secrets Required:**
- `OCI_CLI_USER`: OCI user OCID
- `OCI_CLI_TENANCY`: OCI tenancy OCID
- `OCI_CLI_FINGERPRINT`: API key fingerprint
- `OCI_CLI_KEY_CONTENT`: Private key content
- `OCI_CLI_REGION`: OCI region (e.g., us-ashburn-1)
- `KUBECONFIG_OKE`: OKE cluster kubeconfig

### 7.2 Deployment Process

1. **Build Phase**:
   - Build backend Docker image
   - Build frontend Docker image
   - Build worker Docker image
   - Tag with git SHA
   - Push to OCIR

2. **Test Phase**:
   - Run unit tests
   - Run integration tests
   - Generate coverage report

3. **Deploy Phase**:
   - Update Helm values with new image tags
   - Deploy to OKE with `helm upgrade --install`
   - Run smoke tests
   - Verify health endpoints

---

## 8. Monitoring & Logging

### 8.1 Local Minikube

**Logging:**
- `kubectl logs <pod-name> -c <container-name>`
- `kubectl logs <pod-name> -c daprd` (Dapr sidecar logs)

**Monitoring:**
- `kubectl top pods` (resource usage)
- `kubectl get pods` (pod status)
- Dapr dashboard: `dapr dashboard -k`

### 8.2 Oracle OKE Cloud

**Logging:**
- OCI Logging (free tier: 10GB/month)
- kubectl logs (via OKE API)

**Monitoring:**
- OCI Monitoring (free tier: 500M data points/month)
- Metrics: CPU, memory, network, disk
- Custom metrics via Prometheus (optional)

**Alerting:**
- OCI Notifications (free tier: 1M notifications/month)
- Alert on pod failures, high CPU, high memory

---

## 9. Deployment Checklist

### 9.1 Local Minikube Deployment

- [ ] Minikube started with 6GB memory
- [ ] Dapr runtime installed
- [ ] Kafka (Redpanda) deployed
- [ ] PostgreSQL deployed
- [ ] Kubernetes secrets created
- [ ] Dapr components applied (Pub/Sub, Bindings, Secrets only)
- [ ] Backend deployed with correct DATABASE_URL
- [ ] Frontend deployed
- [ ] Worker deployed (optional)
- [ ] Port-forward configured
- [ ] Application accessible at localhost
- [ ] Health endpoints responding
- [ ] Kafka events flowing

### 9.2 Oracle OKE Cloud Deployment

- [ ] Oracle Cloud account created (Always Free)
- [ ] OKE cluster created (2 nodes, 2 OCPUs each)
- [ ] kubectl configured with OKE credentials
- [ ] Dapr runtime installed on OKE
- [ ] Kafka deployed (Redpanda Cloud or Strimzi)
- [ ] Database deployed (Oracle Autonomous DB or Neon DB)
- [ ] Kubernetes secrets created
- [ ] Dapr components applied with cloud endpoints
- [ ] Docker images built and pushed to OCIR
- [ ] Application deployed with Helm
- [ ] Ingress configured with TLS
- [ ] DNS configured
- [ ] HTTPS access verified
- [ ] CI/CD pipeline configured
- [ ] Monitoring and logging enabled

---

## 10. Troubleshooting

### 10.1 Common Issues

**Issue: Dapr sidecar crashing**
- Check Dapr component configuration
- Verify Kafka broker endpoints
- Check database connection strings
- Remove optional components (State Store) if not needed

**Issue: Backend can't connect to database**
- Verify DATABASE_URL environment variable
- Check `sslmode=disable` for local PostgreSQL
- Verify Kubernetes secret exists
- Check network policies

**Issue: Kafka connection failed**
- Verify Kafka broker endpoints
- Check Kafka pod status
- Verify Dapr Pub/Sub component configuration
- Check network connectivity

**Issue: OKE deployment failed**
- Verify OCI credentials
- Check OKE cluster status
- Verify OCIR image push succeeded
- Check Helm chart values

### 10.2 Debug Commands

```bash
# Check pod status
kubectl get pods

# Check pod logs
kubectl logs <pod-name> -c <container-name>
kubectl logs <pod-name> -c daprd

# Check Dapr components
kubectl get components

# Check Dapr component details
kubectl describe component <component-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods
kubectl top nodes

# Port-forward for debugging
kubectl port-forward svc/todo-backend 8000:8000
kubectl port-forward svc/todo-frontend 3000:3000
```

---

## 11. Success Criteria

Phase 5 deployment is considered **SUCCESSFUL** when:

### Local Minikube
- ✅ All pods running and healthy
- ✅ Application accessible via port-forward
- ✅ Backend API responding
- ✅ Frontend UI loading
- ✅ Database connection working
- ✅ Kafka events publishing and consuming
- ✅ Dapr sidecars healthy

### Oracle OKE Cloud
- ✅ OKE cluster created and running
- ✅ All pods running and healthy
- ✅ Application accessible via HTTPS
- ✅ Custom domain configured (optional)
- ✅ Database connection working
- ✅ Kafka events flowing
- ✅ CI/CD pipeline deploying successfully
- ✅ Monitoring and logging enabled
- ✅ Zero cost (using only free tiers)

---

## 12. Free Tier Resources

### 12.1 Oracle Cloud Always Free

**Compute:**
- 4 OCPUs (ARM-based Ampere A1)
- 24GB RAM
- 2 VM instances

**Storage:**
- 200GB block storage
- 10GB object storage

**Network:**
- 1 flexible load balancer
- 10TB outbound data transfer/month

**Database:**
- 2 Oracle Autonomous Databases
- 20GB storage each

**Monitoring:**
- 500M data points/month
- 1M notifications/month

**Sign-up:** https://www.oracle.com/cloud/free/

### 12.2 Redpanda Cloud Free Tier

- 10GB storage/month
- 10M messages/month
- 3 topics
- 3 partitions per topic

**Sign-up:** https://redpanda.com/try-redpanda

### 12.3 Neon DB Free Tier

- 10GB storage
- 1 project
- Unlimited databases
- Serverless PostgreSQL

**Sign-up:** https://neon.tech/

---

## 13. Next Steps

After successful Phase 5 deployment:

1. **Add Advanced Features** (Phase 6):
   - Priorities, tags, search, filter, sort
   - Recurring tasks
   - Due dates and reminders

2. **Enhance Monitoring**:
   - Add Prometheus and Grafana
   - Create custom dashboards
   - Set up alerting rules

3. **Improve CI/CD**:
   - Add automated testing
   - Add staging environment
   - Add rollback capabilities

4. **Scale Application**:
   - Add horizontal pod autoscaling
   - Optimize resource usage
   - Add caching layer

---

**END OF PHASE 5 SPECIFICATION v1.0**

*This specification provides a practical, cost-free approach to deploying the Todo AI Chatbot with event-driven architecture using Oracle Cloud Always Free tier.*
