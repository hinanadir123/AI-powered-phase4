# Phase 5 Specification: Advanced Features and Cloud Deployment
## Todo AI Chatbot - Event-Driven Architecture with Kafka and Dapr

**Version:** v1.0
**Date:** 2026-02-15
**Based on:** constitution.md v5.0, phase4-spec.md
**Status:** Active

---

## 1. Objective

Implement advanced and intermediate features for the Todo AI Chatbot with event-driven architecture, full Dapr integration, and production-ready cloud deployment.

### Primary Goals
1. **Advanced Features**: Recurring tasks, due dates, and reminders
2. **Intermediate Features**: Priorities, tags, search, filter, and sort capabilities
3. **Event-Driven Architecture**: Kafka-based messaging for async operations
4. **Dapr Integration**: Full Dapr sidecar pattern for all infrastructure
5. **Local Deployment**: Minikube with Dapr + Kafka (Redpanda/Strimzi)
6. **Cloud Deployment**: Azure AKS or Google GKE with CI/CD and monitoring

---

## 2. Scope & Assumptions

### In-Scope
- **Part A - Features**:
  - Intermediate: Priorities (low/medium/high/urgent), Tags (categories), Search (keyword), Filter (status/priority/tag/date), Sort (due date/priority/created)
  - Advanced: Recurring Tasks (daily/weekly/monthly intervals), Due Dates & Reminders (scheduled notifications)

- **Part B - Local Deployment**:
  - Minikube cluster with Dapr runtime
  - Kafka messaging (Redpanda Docker or Strimzi operator)
  - PostgreSQL database (local or Neon DB)
  - Dapr components (Pub/Sub, State, Jobs, Secrets)

- **Part C - Cloud Deployment**:
  - Azure AKS or Google GKE cluster
  - Managed Kafka (Redpanda Cloud/Confluent Cloud) or self-hosted Strimzi
  - CI/CD pipeline (GitHub Actions)
  - Monitoring & logging (Prometheus/Grafana or cloud-native)
  - HTTPS ingress with TLS certificates

### Out-of-Scope
- Alternative Pub/Sub systems (unless Kafka access issues arise)
- Multi-tenancy and user authentication (future phase)
- Mobile applications (web-only for Phase 5)
- Advanced analytics and reporting

### Assumptions
1. Phase 4 local Minikube deployment is functional
2. Free cloud credits available:
   - Azure: $200 credits (30 days)
   - Google Cloud: $300 credits (90 days)
   - Oracle Cloud: Always Free tier
3. Existing Phase 4 codebase (FastAPI backend, React/Next.js frontend)
4. Docker Desktop and Kubernetes tools installed locally
5. GitHub repository for version control and CI/CD

---

## 3. Functional Requirements (Part A - Features)

### 3.1 Intermediate Features

#### 3.1.1 Priorities
- **Description**: Assign priority levels to tasks
- **Priority Levels**: Low, Medium, High, Urgent
- **Implementation**:
  - Add `priority` enum field to Task model
  - API endpoint: `GET /tasks?priority=high`
  - UI: Dropdown selector with color coding
  - Kafka: Publish priority changes to `task-events` topic
- **Acceptance Criteria**:
  - Tasks can be created with priority
  - Tasks can be filtered by priority
  - Tasks can be sorted by priority
  - UI displays priority with visual indicators (colors/badges)

#### 3.1.2 Tags
- **Description**: Categorize tasks with multiple tags
- **Implementation**:
  - Add `tags` array field to Task model (many-to-many relationship)
  - API endpoint: `GET /tasks?tags=work,urgent`
  - UI: Tag chips input with autocomplete
  - Kafka: Publish tag changes to `task-events` topic
- **Acceptance Criteria**:
  - Tasks can have multiple tags
  - Tags can be created dynamically
  - Tasks can be filtered by one or more tags
  - UI displays tags as chips with remove functionality

#### 3.1.3 Search
- **Description**: Full-text search across task title and description
- **Implementation**:
  - PostgreSQL full-text search or Elasticsearch integration
  - API endpoint: `GET /tasks?search=meeting`
  - UI: Search bar with real-time results
  - Kafka: Publish search queries to `task-updates` topic for analytics
- **Acceptance Criteria**:
  - Search returns relevant results from title and description
  - Search is case-insensitive
  - Search results are ranked by relevance
  - UI shows search results with highlighted matches

#### 3.1.4 Filter
- **Description**: Filter tasks by multiple criteria
- **Filter Options**:
  - Status: pending, in-progress, completed
  - Priority: low, medium, high, urgent
  - Tags: one or more tags
  - Due date range: from/to dates
- **Implementation**:
  - API endpoint: `GET /tasks?status=pending&priority=high&tags=work&due_from=2026-02-15&due_to=2026-02-20`
  - UI: Filter panel with checkboxes and date pickers
  - Kafka: Publish filter selections to `task-updates` topic
- **Acceptance Criteria**:
  - Multiple filters can be applied simultaneously
  - Filters are combinable (AND logic)
  - UI shows active filters with clear/reset option
  - Filter state persists in URL query params

#### 3.1.5 Sort
- **Description**: Sort tasks by various fields
- **Sort Options**:
  - Due date (ascending/descending)
  - Priority (urgent → low or low → urgent)
  - Created date (newest/oldest)
  - Title (alphabetical)
- **Implementation**:
  - API endpoint: `GET /tasks?sort=due_date:asc` or `?sort=priority:desc`
  - UI: Sort dropdown with direction toggle
  - Kafka: Publish sort selections to `task-updates` topic
- **Acceptance Criteria**:
  - Tasks can be sorted by any supported field
  - Sort direction can be toggled
  - UI shows current sort field and direction
  - Sort state persists in URL query params

### 3.2 Advanced Features

#### 3.2.1 Recurring Tasks
- **Description**: Tasks that automatically create new instances on completion
- **Recurrence Intervals**:
  - Daily: Every day at specified time
  - Weekly: Every week on specified day(s)
  - Monthly: Every month on specified date
  - Custom: Cron expression support
- **Implementation**:
  - Add `recurrence` object to Task model:
    ```json
    {
      "enabled": true,
      "interval": "weekly",
      "frequency": 1,
      "days": ["monday", "wednesday"],
      "end_date": "2026-12-31"
    }
    ```
  - On task completion, publish event to `task-events` topic
  - Reminder worker subscribes and creates next instance via Dapr Jobs API
  - API endpoints:
    - `POST /tasks` with recurrence object
    - `PUT /tasks/{id}/recurrence` to update recurrence
    - `DELETE /tasks/{id}/recurrence` to stop recurrence
  - UI: Recurrence configuration modal with interval selector
- **Acceptance Criteria**:
  - Recurring tasks create new instances automatically
  - Recurrence can be configured with various intervals
  - Recurrence can be paused or stopped
  - UI shows recurrence status and next occurrence date
  - Kafka events are published for each new instance

#### 3.2.2 Due Dates & Reminders
- **Description**: Set due dates and receive notifications before deadline
- **Implementation**:
  - Add `due_date` datetime field to Task model
  - Add `reminder` object to Task model:
    ```json
    {
      "enabled": true,
      "time_before": "1h",
      "channels": ["email", "push"]
    }
    ```
  - On due date set, publish event to `reminders` topic
  - Reminder worker subscribes and schedules job via Dapr Jobs API
  - Dapr Jobs API triggers notification at scheduled time
  - Notification service publishes to `reminders` topic
  - API endpoints:
    - `PUT /tasks/{id}/due_date` to set due date
    - `PUT /tasks/{id}/reminder` to configure reminder
  - UI: Date/time picker for due date, reminder configuration modal
- **Acceptance Criteria**:
  - Tasks can have due dates
  - Reminders are sent at configured time before due date
  - Multiple reminder channels supported (email, push, in-app)
  - UI shows due date with visual indicators (overdue in red)
  - Kafka events are published for reminder scheduling and delivery

---

## 4. Architecture Overview

### 4.1 System Architecture Diagram

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

### 4.2 Event Flow Diagram

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

### 4.3 Dapr Components

All Dapr components are defined in `dapr-components/` directory:

1. **pubsub-kafka.yaml**: Kafka Pub/Sub component
2. **statestore-postgresql.yaml**: PostgreSQL State Store
3. **jobs-scheduler.yaml**: Jobs API component
4. **secretstore-kubernetes.yaml**: Kubernetes Secret Store
5. **bindings-cron.yaml**: Cron bindings for scheduled tasks

---

## 5. Non-Functional Requirements

### 5.1 Event-Driven Decoupling
- All async operations use Kafka Pub/Sub via Dapr
- Services communicate via events, not direct HTTP calls
- Loose coupling enables independent scaling and deployment

### 5.2 Scalability
- Horizontal pod autoscaling (HPA) based on CPU/memory
- Kafka partitioning for parallel event processing
- Stateless services for easy replication

### 5.3 Resilience
- Liveness and readiness probes for all pods
- Automatic pod restart on failure
- Dead letter queues (DLQ) for failed events
- Retry policies with exponential backoff

### 5.4 Observability
- **Logging**: Structured logs to stdout (kubectl logs)
- **Metrics**: Prometheus metrics for request rate, latency, errors
- **Tracing**: Dapr distributed tracing (Zipkin/Jaeger)
- **Monitoring**: Grafana dashboards for visualization
- **Alerting**: Alert rules for error rate, latency, resource usage

### 5.5 Security
- HTTPS only (TLS certificates via Let's Encrypt or cloud-managed)
- Secrets stored in Kubernetes Secrets (encrypted at rest)
- Dapr Secret Store for API keys and credentials
- No root containers (run as non-root user)
- RBAC for Kubernetes service accounts
- Network policies for pod-to-pod communication

### 5.6 Performance
- Response time p95 < 500ms for API calls
- Event processing latency < 1 second
- Support 100+ concurrent users
- Database query optimization with indexes

---

## 6. Tools & Agents Mapping

| Agent | Responsibility | Input | Output |
|-------|---------------|-------|--------|
| **kafka-dapr-engineer** | Generate Kafka topics and Dapr component YAML files | constitution.md, phase5-spec.md | dapr-components/*.yaml, kafka-topics.md |
| **advanced-features-agent** | Implement advanced features (recurring tasks, reminders) | phase5-spec.md, existing codebase | backend/features/*.py, frontend/components/*.tsx |
| **intermediate-features-agent** | Implement intermediate features (priorities, tags, search, filter, sort) | phase5-spec.md, existing codebase | backend/api/*.py, frontend/components/*.tsx |
| **cloud-deploy-engineer** | Setup cloud infrastructure (AKS/GKE) and deploy | constitution.md, Helm charts | docs/setup-azure.md, docs/setup-gke.md, deployed cluster |
| **cicd-monitoring-agent** | Create CI/CD pipeline and monitoring setup | phase5-spec.md, GitHub repo | .github/workflows/deploy.yml, monitoring/prometheus/*.yaml |
| **k8s-config-generator** | Generate Kubernetes manifests and Helm charts | phase5-spec.md, existing charts | charts/backend/*, charts/frontend/*, k8s/*.yaml |
| **dapr-pubsub-generator** | Generate Kafka publisher/subscriber code | phase5-spec.md, Dapr components | backend/events/*.py, worker/subscribers/*.py |
| **phase5-deployment-tester** | Validate deployment and run tests | deployed cluster, test cases | test reports, validation results |

---

## 7. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Kafka access issues** | High | Low | Use alternative Pub/Sub (RabbitMQ, Redis Streams) via Dapr component swap |
| **Cloud credit expiration** | Medium | Medium | Use Oracle Cloud Always Free tier (OKE) as backup |
| **Dapr learning curve** | Medium | Medium | Provide comprehensive documentation and examples |
| **Event ordering issues** | High | Low | Use Kafka partitioning with task_id as key for ordering |
| **Database performance** | Medium | Medium | Implement caching with Dapr State Store, optimize queries |
| **CI/CD pipeline failures** | Medium | Low | Implement automated rollback, comprehensive testing |
| **Monitoring overhead** | Low | Low | Use sampling for tracing, aggregate metrics |
| **Security vulnerabilities** | High | Low | Regular security scans, follow OWASP best practices |

---

## 8. Timeline & Task Breakdown

| Task ID | Task Description | Agent | Estimated Effort | Dependencies |
|---------|-----------------|-------|------------------|--------------|
| **T5.1** | **Setup Phase 5 Infrastructure** | | | |
| T5.1.1 | Generate Kafka topics configuration | kafka-dapr-engineer | 2h | constitution.md |
| T5.1.2 | Generate Dapr component YAML files | kafka-dapr-engineer | 3h | T5.1.1 |
| T5.1.3 | Deploy Kafka (Redpanda) to Minikube | k8s-config-generator | 2h | T5.1.1 |
| T5.1.4 | Deploy Dapr components to Minikube | k8s-config-generator | 2h | T5.1.2 |
| **T5.2** | **Implement Intermediate Features** | | | |
| T5.2.1 | Add priorities to Task model and API | intermediate-features-agent | 4h | T5.1.4 |
| T5.2.2 | Add tags to Task model and API | intermediate-features-agent | 4h | T5.1.4 |
| T5.2.3 | Implement search functionality | intermediate-features-agent | 6h | T5.2.2 |
| T5.2.4 | Implement filter functionality | intermediate-features-agent | 6h | T5.2.3 |
| T5.2.5 | Implement sort functionality | intermediate-features-agent | 4h | T5.2.4 |
| T5.2.6 | Create UI components (priority dropdown, tag chips, search bar, filter panel, sort select) | intermediate-features-agent | 8h | T5.2.5 |
| **T5.3** | **Implement Advanced Features** | | | |
| T5.3.1 | Add recurring tasks to Task model | advanced-features-agent | 6h | T5.2.6 |
| T5.3.2 | Implement Kafka publisher for task events | dapr-pubsub-generator | 4h | T5.3.1 |
| T5.3.3 | Implement reminder worker (Kafka subscriber) | dapr-pubsub-generator | 6h | T5.3.2 |
| T5.3.4 | Integrate Dapr Jobs API for scheduling | advanced-features-agent | 6h | T5.3.3 |
| T5.3.5 | Add due dates and reminders to Task model | advanced-features-agent | 4h | T5.3.4 |
| T5.3.6 | Create UI components (recurrence modal, due date picker, reminder config) | advanced-features-agent | 8h | T5.3.5 |
| **T5.4** | **Testing & Validation** | | | |
| T5.4.1 | Write unit tests for all features | intermediate-features-agent, advanced-features-agent | 8h | T5.3.6 |
| T5.4.2 | Write integration tests for Kafka/Dapr | dapr-pubsub-generator | 6h | T5.4.1 |
| T5.4.3 | Write E2E tests for user flows | phase5-deployment-tester | 8h | T5.4.2 |
| T5.4.4 | Validate local deployment on Minikube | phase5-deployment-tester | 4h | T5.4.3 |
| **T5.5** | **Cloud Deployment** | | | |
| T5.5.1 | Create AKS/GKE cluster | cloud-deploy-engineer | 3h | T5.4.4 |
| T5.5.2 | Deploy Kafka to cloud (Redpanda Cloud or Strimzi) | cloud-deploy-engineer | 4h | T5.5.1 |
| T5.5.3 | Deploy application to cloud with Helm | cloud-deploy-engineer | 4h | T5.5.2 |
| T5.5.4 | Setup ingress with HTTPS | cloud-deploy-engineer | 3h | T5.5.3 |
| T5.5.5 | Configure DNS and verify public URL | cloud-deploy-engineer | 2h | T5.5.4 |
| **T5.6** | **CI/CD & Monitoring** | | | |
| T5.6.1 | Create GitHub Actions workflow | cicd-monitoring-agent | 6h | T5.5.5 |
| T5.6.2 | Setup Prometheus and Grafana | cicd-monitoring-agent | 4h | T5.6.1 |
| T5.6.3 | Configure logging (Loki or cloud logging) | cicd-monitoring-agent | 4h | T5.6.2 |
| T5.6.4 | Setup alerting rules | cicd-monitoring-agent | 3h | T5.6.3 |
| **T5.7** | **Documentation** | | | |
| T5.7.1 | Generate README-phase5.md | cloud-deploy-engineer | 4h | T5.6.4 |
| T5.7.2 | Generate setup guides (local, Azure, GKE) | cloud-deploy-engineer | 6h | T5.7.1 |
| T5.7.3 | Generate free credits signup guide | cloud-deploy-engineer | 2h | T5.7.2 |

**Total Estimated Effort**: ~150 hours (agent-generated, not manual)

---

## 9. Acceptance Criteria

### 9.1 Intermediate Features
- [ ] Tasks can be assigned priorities (low/medium/high/urgent)
- [ ] Tasks can be tagged with multiple categories
- [ ] Search returns relevant results from title and description
- [ ] Filter works for status, priority, tags, and due date range
- [ ] Sort works for due date, priority, and created date
- [ ] UI displays all intermediate features with proper styling

### 9.2 Advanced Features
- [ ] Recurring tasks create new instances automatically
- [ ] Recurrence can be configured with daily/weekly/monthly intervals
- [ ] Due dates can be set on tasks
- [ ] Reminders are scheduled and triggered via Dapr Jobs API
- [ ] Notifications are sent at configured time before due date
- [ ] UI displays recurrence status and due date indicators

### 9.3 Event-Driven Architecture
- [ ] All async operations use Kafka Pub/Sub via Dapr
- [ ] Kafka topics (task-events, reminders, task-updates) are created
- [ ] Events are published for task CRUD, reminders, and updates
- [ ] Reminder worker subscribes to events and processes them
- [ ] Dead letter queues handle failed events

### 9.4 Local Deployment
- [ ] Minikube cluster is running with Dapr installed
- [ ] Kafka (Redpanda or Strimzi) is deployed and accessible
- [ ] PostgreSQL database is deployed and accessible
- [ ] All Dapr components are loaded and healthy
- [ ] Backend, frontend, and worker pods are running
- [ ] Application is accessible via port-forward
- [ ] All features work correctly on local deployment

### 9.5 Cloud Deployment
- [ ] AKS or GKE cluster is created and configured
- [ ] Kafka is deployed (Redpanda Cloud or Strimzi)
- [ ] PostgreSQL is deployed (Azure Database or Cloud SQL or Neon DB)
- [ ] All services are deployed via Helm charts
- [ ] Ingress is configured with HTTPS (TLS certificates)
- [ ] DNS is configured and public URL is accessible
- [ ] All features work correctly on cloud deployment

### 9.6 CI/CD & Monitoring
- [ ] GitHub Actions workflow is created and functional
- [ ] Pipeline runs on push to main branch
- [ ] All tests pass in CI/CD pipeline
- [ ] Deployment to staging and production works
- [ ] Prometheus is collecting metrics
- [ ] Grafana dashboards are displaying metrics
- [ ] Logging is configured (Loki or cloud logging)
- [ ] Alert rules are configured and functional

### 9.7 Documentation
- [ ] README-phase5.md is complete and accurate
- [ ] Local setup guide is available
- [ ] Azure AKS deployment guide is available
- [ ] Google GKE deployment guide is available
- [ ] Free credits signup guide is available
- [ ] All documentation is clear and easy to follow

### 9.8 Quality & Performance
- [ ] All code is generated by agents (no manual coding)
- [ ] All code passes linters (ESLint, Prettier, Pylint)
- [ ] Unit test coverage > 80%
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] API response time p95 < 500ms
- [ ] Event processing latency < 1 second
- [ ] No security vulnerabilities detected

---

## 10. Success Metrics

Phase 5 is considered **SUCCESSFUL** when:

1. ✅ All acceptance criteria are met
2. ✅ Public URL is live and accessible with HTTPS
3. ✅ All advanced and intermediate features work as specified
4. ✅ CI/CD pipeline deploys successfully on every push to main
5. ✅ Monitoring dashboards show healthy metrics (no errors, low latency)
6. ✅ Documentation is complete and accurate
7. ✅ Free tier resources are used (no unexpected costs)
8. ✅ All deliverables in constitution.md Section 8 are marked as "✅ Complete"

---

## 11. References

- **Constitution v5.0**: D:/4-phases of hackathon/phase-4/constitution.md
- **Phase 4 Spec**: D:/4-phases of hackathon/phase-4/phase4-spec.md (if exists)
- **Dapr Documentation**: https://docs.dapr.io/
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **Redpanda Documentation**: https://docs.redpanda.com/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **GitHub Actions Documentation**: https://docs.github.com/en/actions

---

**END OF PHASE 5 SPECIFICATION v1.0**

*This specification is the detailed technical blueprint for Phase 5 implementation. All agents must reference this document along with constitution.md v5.0 before generating any code, configuration, or documentation.*
