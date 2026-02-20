# Phase 5: Advanced Cloud Deployment
## Todo AI Chatbot - Event-Driven Microservices with Kafka and Dapr

**Version:** 5.0
**Date:** 2026-02-15
**Status:** Production Ready

---

## Overview

Phase 5 represents the complete evolution of the Todo AI Chatbot into a production-ready, cloud-native application with advanced features, event-driven architecture, and comprehensive observability. This phase introduces recurring tasks, reminders, priorities, tags, search/filter/sort capabilities, and full Kafka + Dapr integration for scalable, resilient microservices deployment.

### What's New in Phase 5

- **Advanced Features**: Recurring tasks with flexible scheduling, due dates with automated reminders
- **Intermediate Features**: Task priorities, multi-tag categorization, full-text search, advanced filtering and sorting
- **Event-Driven Architecture**: Kafka-based messaging for asynchronous operations and real-time updates
- **Full Dapr Integration**: Complete abstraction of infrastructure concerns (Pub/Sub, State, Jobs, Secrets)
- **Cloud Deployment**: Production-ready deployment on Azure AKS or Google GKE with HTTPS and DNS
- **CI/CD Automation**: GitHub Actions pipeline for continuous deployment with automated testing
- **Comprehensive Monitoring**: Prometheus metrics, Grafana dashboards, centralized logging, and alerting

---

## Features

### Intermediate Features

#### Priorities
Assign priority levels to tasks for better organization and focus:
- **Low**: Nice-to-have tasks
- **Medium**: Standard priority tasks
- **High**: Important tasks requiring attention
- **Urgent**: Critical tasks needing immediate action

Visual indicators with color coding help identify task urgency at a glance.

#### Tags
Categorize tasks with multiple tags for flexible organization:
- Add unlimited tags to any task
- Filter tasks by one or more tags
- Autocomplete suggestions for existing tags
- Tag chips with easy removal

#### Search
Full-text search across task titles and descriptions:
- Case-insensitive keyword search
- Relevance-ranked results
- Real-time search results
- Highlighted matches in results

#### Filter
Multi-criteria filtering for precise task lists:
- Filter by status (pending, in-progress, completed)
- Filter by priority level
- Filter by tags (AND logic)
- Filter by due date range
- Combine multiple filters simultaneously

#### Sort
Flexible sorting options for task organization:
- Sort by due date (ascending/descending)
- Sort by priority (urgent to low or reverse)
- Sort by created date (newest/oldest)
- Sort by title (alphabetical)

### Advanced Features

#### Recurring Tasks
Automate repetitive tasks with flexible recurrence patterns:
- **Daily**: Every day at specified time
- **Weekly**: Every week on specified day(s)
- **Monthly**: Every month on specified date
- **Custom**: Advanced cron expression support

When a recurring task is completed, a new instance is automatically created based on the recurrence pattern.

#### Due Dates & Reminders
Never miss a deadline with automated reminders:
- Set due dates on any task
- Configure reminder notifications (1 hour, 1 day, 1 week before)
- Multiple notification channels (email, push, in-app)
- Visual indicators for overdue tasks (red highlighting)
- Automated reminder scheduling via Dapr Jobs API

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Ingress (NGINX)                    │
│                    TLS Termination (Let's Encrypt)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│   Frontend Pod            │   │   Backend Pod             │
│   ┌─────────────────┐     │   │   ┌─────────────────┐     │
│   │ React/Next.js   │     │   │   │ FastAPI/Node.js │     │
│   │ App             │     │   │   │ REST API        │     │
│   └────────┬────────┘     │   │   └────────┬────────┘     │
│            │              │   │            │              │
│   ┌────────▼────────┐     │   │   ┌────────▼────────┐     │
│   │ Dapr Sidecar    │◄────┼───┼───┤ Dapr Sidecar    │     │
│   │ (Service Invoke)│     │   │   │ (Pub/Sub/State) │     │
│   └─────────────────┘     │   │   └────────┬────────┘     │
└───────────────────────────┘   └────────────┼──────────────┘
                                             │
                                             ▼
                        ┌────────────────────────────────┐
                        │   Kafka Cluster (Redpanda)     │
                        │   Topics:                      │
                        │   - task-events                │
                        │   - reminders                  │
                        │   - task-updates               │
                        └────────────┬───────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────────┐
                        │   Reminder Worker Pod          │
                        │   ┌─────────────────┐          │
                        │   │ Event Processor │          │
                        │   │ (Subscriber)    │          │
                        │   └────────┬────────┘          │
                        │            │                   │
                        │   ┌────────▼────────┐          │
                        │   │ Dapr Sidecar    │          │
                        │   │ (Pub/Sub/Jobs)  │          │
                        │   └────────┬────────┘          │
                        └────────────┼───────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────────┐
                        │   PostgreSQL Database          │
                        │   (Neon DB or Cloud SQL)       │
                        │   - Tasks table                │
                        │   - Dapr state table           │
                        └────────────────────────────────┘
```

### Event Flow

```
User Action (Create Task with Reminder)
    │
    ▼
Frontend → Dapr Service Invocation → Backend API
    │
    ▼
Backend saves task to PostgreSQL
    │
    ▼
Backend publishes event to Kafka (task-events topic)
    │
    ├─→ Event: { type: "task.created", task_id: "123", due_date: "2026-02-20T10:00:00Z" }
    │
    ▼
Kafka distributes to subscribers
    │
    ▼
Reminder Worker (Dapr Pub/Sub subscriber)
    │
    ▼
Worker schedules job via Dapr Jobs API
    │
    ├─→ Job: { name: "reminder-123", schedule: "2026-02-20T09:00:00Z" }
    │
    ▼
Dapr Jobs API stores job in PostgreSQL
    │
    ▼
At scheduled time, Dapr triggers job
    │
    ▼
Worker publishes notification event to Kafka (reminders topic)
    │
    ├─→ Event: { type: "reminder.triggered", task_id: "123", message: "Task due in 1 hour" }
    │
    ▼
Notification Service sends notification (email/push)
    │
    ▼
Frontend receives update via WebSocket or polling
```

### Component Descriptions

| Component | Technology | Purpose | Dapr Integration |
|-----------|-----------|---------|------------------|
| **Backend API** | FastAPI/Node.js | REST API, business logic | Dapr sidecar for Pub/Sub, State, Jobs |
| **Frontend** | React/Next.js | User interface | Dapr sidecar for Service Invocation |
| **Reminder Worker** | Node.js/Python | Processes reminder events | Dapr sidecar for Pub/Sub, Jobs |
| **Database** | PostgreSQL (Neon DB) | Persistent storage | Dapr State Store component |
| **Message Broker** | Kafka (Redpanda) | Event streaming | Dapr Pub/Sub component |
| **State Store** | PostgreSQL | Dapr state management | Dapr State Store component |
| **Secrets** | Kubernetes Secrets | Credentials, API keys | Dapr Secret Store component |

### Technology Stack

- **Orchestration**: Kubernetes (Minikube local, AKS/GKE cloud)
- **Package Manager**: Helm 3.x
- **Service Mesh**: Dapr 1.12+
- **Messaging**: Kafka (Redpanda Cloud/Confluent Cloud or Strimzi)
- **Database**: PostgreSQL (Neon DB or cloud-managed)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki or cloud-native logging
- **Ingress**: NGINX Ingress Controller
- **Certificates**: Let's Encrypt (cert-manager)

---

## Prerequisites

### Local Development

- **Minikube** 1.32+ - Local Kubernetes cluster
- **Docker Desktop** - Container runtime
- **kubectl** 1.28+ - Kubernetes CLI
- **Helm** 3.12+ - Kubernetes package manager
- **Dapr CLI** 1.12+ - Dapr command-line tool

### Cloud Deployment

Choose one of the following cloud platforms:

#### Azure AKS (Recommended)
- Azure account with $200 free credits
- Azure CLI 2.55+
- Sign up: https://azure.microsoft.com/free/

#### Google GKE
- Google Cloud account with $300 free credits
- gcloud CLI 460+
- Sign up: https://cloud.google.com/free

#### Oracle OKE (Always Free)
- Oracle Cloud account (Always Free tier)
- OCI CLI
- Sign up: https://www.oracle.com/cloud/free/

### Managed Services (Optional)

- **Redpanda Cloud**: Free tier (10GB/month) - https://redpanda.com/try-redpanda
- **Confluent Cloud**: Free tier - https://www.confluent.io/confluent-cloud/tryfree/
- **Neon DB**: Free tier (10GB) - https://neon.tech/

---

## Quick Start

### Local Deployment (Minikube)

1. **Start Minikube**
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

2. **Install Dapr**
```bash
dapr init -k
```

3. **Deploy Kafka (Redpanda)**
```bash
helm repo add redpanda https://charts.redpanda.com/
helm install redpanda redpanda/redpanda --namespace kafka --create-namespace
```

4. **Deploy PostgreSQL**
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql --namespace database --create-namespace
```

5. **Apply Dapr Components**
```bash
kubectl apply -f dapr-components/
```

6. **Deploy Application**
```bash
# Backend
helm install backend charts/todo-backend/ --namespace todo-app --create-namespace

# Frontend
helm install frontend charts/todo-frontend/ --namespace todo-app

# Reminder Worker
helm install worker charts/reminder-worker/ --namespace todo-app
```

7. **Access Application**
```bash
kubectl port-forward -n todo-app svc/frontend 3000:3000
```

Open http://localhost:3000 in your browser.

### Cloud Deployment (Azure AKS)

1. **Create Resource Group**
```bash
az group create --name todo-rg --location eastus
```

2. **Create AKS Cluster**
```bash
az aks create \
  --name todo-cluster \
  --resource-group todo-rg \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys
```

3. **Get Credentials**
```bash
az aks get-credentials --name todo-cluster --resource-group todo-rg
```

4. **Install Dapr**
```bash
dapr init -k
```

5. **Deploy Kafka (Redpanda Cloud or Strimzi)**

Option A: Redpanda Cloud (Recommended)
- Sign up at https://redpanda.com/try-redpanda
- Create cluster and get connection details
- Update `dapr-components/pubsub-kafka.yaml` with broker URLs

Option B: Strimzi (Self-hosted)
```bash
helm repo add strimzi https://strimzi.io/charts/
helm install strimzi strimzi/strimzi-kafka-operator --namespace kafka --create-namespace
kubectl apply -f k8s/kafka-cluster.yaml -n kafka
```

6. **Deploy PostgreSQL**

Option A: Azure Database for PostgreSQL
```bash
az postgres flexible-server create \
  --name todo-db \
  --resource-group todo-rg \
  --location eastus \
  --admin-user todoadmin \
  --admin-password <YOUR_PASSWORD> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32
```

Option B: Neon DB (Serverless)
- Sign up at https://neon.tech/
- Create database and get connection string

7. **Create Secrets**
```bash
kubectl create secret generic db-credentials \
  --from-literal=connectionString="<YOUR_DB_CONNECTION_STRING>" \
  -n todo-app

kubectl create secret generic kafka-credentials \
  --from-literal=brokers="<YOUR_KAFKA_BROKERS>" \
  -n todo-app
```

8. **Apply Dapr Components**
```bash
kubectl apply -f dapr-components/
```

9. **Deploy Application**
```bash
# Build and push Docker images
docker build -t <YOUR_REGISTRY>/todo-backend:latest ./backend
docker push <YOUR_REGISTRY>/todo-backend:latest

docker build -t <YOUR_REGISTRY>/todo-frontend:latest ./frontend
docker push <YOUR_REGISTRY>/todo-frontend:latest

docker build -t <YOUR_REGISTRY>/reminder-worker:latest ./worker
docker push <YOUR_REGISTRY>/reminder-worker:latest

# Deploy with Helm
helm install backend charts/todo-backend/ \
  --set image.repository=<YOUR_REGISTRY>/todo-backend \
  --set image.tag=latest \
  -n todo-app --create-namespace

helm install frontend charts/todo-frontend/ \
  --set image.repository=<YOUR_REGISTRY>/todo-frontend \
  --set image.tag=latest \
  -n todo-app

helm install worker charts/reminder-worker/ \
  --set image.repository=<YOUR_REGISTRY>/reminder-worker \
  --set image.tag=latest \
  -n todo-app
```

10. **Setup Ingress with HTTPS**
```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace

# Install cert-manager for Let's Encrypt
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Apply ingress configuration
kubectl apply -f k8s/ingress.yaml -n todo-app
```

11. **Configure DNS**
```bash
# Get ingress IP
kubectl get ingress -n todo-app

# Point your domain to the ingress IP
# Example: todo.yourdomain.com → <INGRESS_IP>
```

12. **Verify Deployment**
```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Test public URL
curl https://todo.yourdomain.com/health
```

### Cloud Deployment (Google GKE)

1. **Create GKE Cluster**
```bash
gcloud container clusters create todo-cluster \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --zone=us-central1-a
```

2. **Get Credentials**
```bash
gcloud container clusters get-credentials todo-cluster --zone=us-central1-a
```

3. **Follow steps 4-12 from Azure AKS deployment** (same process)

For GKE-specific options:
- Use Cloud SQL for PostgreSQL
- Use GKE Ingress with Google-managed SSL certificates
- Use GKE Logging and Monitoring

---

## Usage Examples

### API Endpoints

#### Create Task with Priority and Tags
```bash
curl -X POST https://todo.yourdomain.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive README and setup guides",
    "priority": "high",
    "tags": ["documentation", "project"],
    "due_date": "2026-02-20T17:00:00Z"
  }'
```

#### Create Recurring Task
```bash
curl -X POST https://todo.yourdomain.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly team meeting",
    "description": "Discuss project progress and blockers",
    "priority": "medium",
    "tags": ["meeting", "team"],
    "recurrence": {
      "enabled": true,
      "interval": "weekly",
      "frequency": 1,
      "days": ["monday"],
      "end_date": "2026-12-31"
    }
  }'
```

#### Set Reminder
```bash
curl -X PUT https://todo.yourdomain.com/api/tasks/123/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "time_before": "1h",
    "channels": ["email", "push"]
  }'
```

#### Search Tasks
```bash
curl "https://todo.yourdomain.com/api/tasks?search=meeting"
```

#### Filter Tasks
```bash
curl "https://todo.yourdomain.com/api/tasks?status=pending&priority=high&tags=work"
```

#### Sort Tasks
```bash
curl "https://todo.yourdomain.com/api/tasks?sort=due_date:asc"
```

### Event Publishing Example

```python
# Backend publishes task event to Kafka via Dapr
import requests

def publish_task_event(task_id, event_type, task_data):
    dapr_url = "http://localhost:3500/v1.0/publish/pubsub-kafka/task-events"
    event = {
        "type": event_type,
        "task_id": task_id,
        "timestamp": datetime.utcnow().isoformat(),
        "data": task_data
    }
    response = requests.post(dapr_url, json=event)
    return response.status_code == 200
```

---

## Configuration

### Environment Variables

#### Backend
```bash
DATABASE_URL=postgresql://user:password@host:5432/tododb
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
LOG_LEVEL=info
```

#### Frontend
```bash
NEXT_PUBLIC_API_URL=https://todo.yourdomain.com/api
NEXT_PUBLIC_WS_URL=wss://todo.yourdomain.com/ws
```

#### Reminder Worker
```bash
DAPR_HTTP_PORT=3500
KAFKA_CONSUMER_GROUP=worker-group
LOG_LEVEL=info
```

### Dapr Components Configuration

All Dapr components are defined in `dapr-components/` directory:

- `pubsub-kafka.yaml` - Kafka Pub/Sub component
- `statestore-postgresql.yaml` - PostgreSQL State Store
- `jobs-scheduler.yaml` - Jobs API component
- `secretstore-kubernetes.yaml` - Kubernetes Secret Store
- `bindings-cron.yaml` - Cron bindings for scheduled tasks

### Kafka Topics Configuration

| Topic | Partitions | Replication | Purpose |
|-------|-----------|-------------|---------|
| `task-events` | 3 | 3 | Task CRUD operations |
| `reminders` | 3 | 3 | Reminder notifications |
| `task-updates` | 3 | 3 | Real-time task updates |
| `task-events-dlq` | 1 | 3 | Dead letter queue for task-events |
| `reminders-dlq` | 1 | 3 | Dead letter queue for reminders |

---

## Monitoring and Observability

### Prometheus Metrics

The application exposes the following metrics:

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - HTTP request latency
- `http_requests_errors_total` - Total HTTP errors
- `kafka_messages_published_total` - Total Kafka messages published
- `kafka_messages_consumed_total` - Total Kafka messages consumed
- `kafka_consumer_lag` - Kafka consumer lag
- `dapr_component_health` - Dapr component health status
- `task_operations_total` - Total task operations (create, update, delete)

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (local) or `https://grafana.yourdomain.com` (cloud).

Available dashboards:
1. **Application Dashboard** - Request rate, latency, error rate
2. **Infrastructure Dashboard** - CPU, memory, disk, network usage
3. **Kafka Dashboard** - Throughput, lag, partition distribution
4. **Dapr Dashboard** - Sidecar health, component status

### Loki Logs

Query logs using LogQL:

```logql
# All backend logs
{app="backend"}

# Error logs only
{app="backend"} |= "ERROR"

# Logs for specific task
{app="backend"} |= "task_id=123"

# Kafka consumer logs
{app="worker"} |= "kafka"
```

### Alerting

Alert rules are configured in `monitoring/prometheus/alerts.yaml`:

- Error rate > 5% for 5 minutes
- Response time p95 > 1000ms for 5 minutes
- CPU usage > 80% for 10 minutes
- Memory usage > 90% for 5 minutes
- Kafka consumer lag > 1000 messages

Alerts are sent to configured channels (email, Slack, Discord).

---

## CI/CD

### GitHub Actions Workflow

The CI/CD pipeline is defined in `.github/workflows/deploy.yml`:

#### Triggers
- Push to `main` branch
- Pull request to `main` branch
- Manual workflow dispatch

#### Jobs

1. **Build**
   - Checkout code
   - Install dependencies
   - Run linters (ESLint, Prettier)
   - Build Docker images
   - Push to container registry

2. **Test**
   - Run unit tests
   - Run integration tests
   - Run E2E tests
   - Generate code coverage report
   - Upload coverage to Codecov

3. **Deploy to Staging**
   - Deploy to staging cluster
   - Run smoke tests
   - Validate health endpoints

4. **Deploy to Production** (manual approval)
   - Deploy to production cluster
   - Run smoke tests
   - Monitor for errors (5-minute window)
   - Rollback on failure

### Deployment Process

```bash
# Trigger deployment
git push origin main

# Monitor deployment
kubectl get pods -n todo-app -w

# Check deployment status
kubectl rollout status deployment/backend -n todo-app

# Rollback if needed
kubectl rollout undo deployment/backend -n todo-app
```

---

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Check pod logs
kubectl logs <POD_NAME> -n todo-app

# Check pod events
kubectl describe pod <POD_NAME> -n todo-app

# Check Dapr sidecar logs
kubectl logs <POD_NAME> -c daprd -n todo-app
```

#### Dapr Components Not Loading

```bash
# List Dapr components
dapr components -k -n todo-app

# Check component configuration
kubectl get component -n todo-app

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

#### Kafka Connection Issues

```bash
# Check Kafka pods
kubectl get pods -n kafka

# Test Kafka connectivity
kubectl run kafka-test --rm -it --image=confluentinc/cp-kafka:latest -- bash
kafka-topics --list --bootstrap-server <KAFKA_BROKER>

# Check Kafka logs
kubectl logs <KAFKA_POD> -n kafka
```

#### Database Connection Issues

```bash
# Test database connectivity
kubectl run postgres-test --rm -it --image=postgres:15 -- bash
psql -h <DB_HOST> -U <DB_USER> -d <DB_NAME>

# Check database logs
kubectl logs <POSTGRES_POD> -n database
```

#### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n todo-app

# Check ingress controller logs
kubectl logs -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx

# Check certificate status
kubectl get certificate -n todo-app
kubectl describe certificate <CERT_NAME> -n todo-app
```

### Debug Commands

```bash
# Port-forward to backend
kubectl port-forward -n todo-app svc/backend 8000:8000

# Port-forward to Kafka UI
kubectl port-forward -n kafka svc/redpanda-console 8080:8080

# Port-forward to Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Execute command in pod
kubectl exec -it <POD_NAME> -n todo-app -- bash

# View all resources
kubectl get all -n todo-app
```

### Log Locations

- **Application logs**: `kubectl logs <POD_NAME> -n todo-app`
- **Dapr sidecar logs**: `kubectl logs <POD_NAME> -c daprd -n todo-app`
- **Ingress logs**: `kubectl logs -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx`
- **Kafka logs**: `kubectl logs <KAFKA_POD> -n kafka`

---

## Testing

### Running Unit Tests

```bash
# Backend tests
cd backend
npm test
# or
pytest

# Frontend tests
cd frontend
npm test

# Worker tests
cd worker
npm test
```

### Running Integration Tests

```bash
# All integration tests
npm run test:integration

# Specific integration test
npm run test:integration -- kafka-pubsub.test.js
```

### Running E2E Tests

```bash
# All E2E tests
npm run test:e2e

# Specific E2E test
npm run test:e2e -- task-creation.spec.js

# E2E tests with UI
npm run test:e2e:ui
```

### Test Coverage

```bash
# Generate coverage report
npm run test:coverage

# View coverage report
open coverage/index.html
```

---

## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`npm test`)
5. Run linters (`npm run lint`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards

- Follow ESLint configuration for JavaScript/TypeScript
- Follow PEP 8 for Python code
- Write unit tests for all new features
- Maintain test coverage above 80%
- Document all public APIs
- Use meaningful commit messages

### Pull Request Process

1. Update README.md with details of changes
2. Update documentation if needed
3. Ensure all tests pass
4. Request review from maintainers
5. Address review comments
6. Merge after approval

---

## License and Credits

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Credits

- **Phase 5 Implementation**: Claude Opus 4.6 (1M context)
- **Architecture Design**: Event-driven microservices with Kafka and Dapr
- **Cloud Deployment**: Azure AKS and Google GKE
- **Monitoring**: Prometheus, Grafana, Loki
- **CI/CD**: GitHub Actions

### Acknowledgments

- Dapr community for excellent documentation and support
- Redpanda for providing free tier Kafka service
- Neon DB for serverless PostgreSQL
- Azure and Google Cloud for free credits
- Open source community for amazing tools and libraries

---

## Additional Resources

### Documentation

- [Local Setup Guide](docs/setup-local.md) - Detailed Minikube setup instructions
- [Azure AKS Setup Guide](docs/setup-azure.md) - Complete Azure deployment guide
- [Google GKE Setup Guide](docs/setup-gke.md) - Complete GKE deployment guide
- [Free Credits Guide](docs/free-credits.md) - How to sign up for free cloud credits

### External Links

- [Dapr Documentation](https://docs.dapr.io/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Join our Discord community
- Email: support@todo-ai-chatbot.com

---

**Phase 5 Status**: Production Ready ✅

**Public URL**: https://todo.yourdomain.com (replace with your actual domain)

**Last Updated**: 2026-02-15

---

*Generated by Claude Opus 4.6 following constitution.md v5.0 and phase5-spec.md v1.0*
