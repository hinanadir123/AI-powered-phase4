# Phase 4 Deployment Plan
## Local Kubernetes Deployment of Todo AI Chatbot on Minikube

**Version:** v1.0
**Date:** 2026-02-08
**Based on:** constitution.md v4.0 and phase4-spec.md

## Overview
The goal is to perform an agentic deployment of the Phase 3 Todo Chatbot to Minikube using Helm, Docker, and AI tools (Gordon, kubectl-ai, kagent). This plan outlines the systematic approach to containerize the application, package it with Helm charts, deploy it to a local Kubernetes cluster, and validate the deployment.

## Prerequisites Checklist
- [ ] Minikube & Docker Desktop installed and running
- [ ] Helm CLI installed
- [ ] Agents ready: docker-engineer, helm-chart-engineer, minikube-deployer, aiops-troubleshooter, infra-spec-writer, deployment-tester
- [ ] Docker images built: todo-backend:latest, todo-frontend:latest
- [ ] OPENAI_API_KEY and other required environment variables configured
- [ ] Phase 3 codebase available and unchanged from previous phase
- [ ] Kubectl CLI installed and configured

## Step-by-Step Execution Plan

### Step 1: Containerization
- **Agent:** docker-engineer
- **Output:** Dockerfiles, .dockerignore, build/run commands
- **Estimated time:** 20–30 minutes
- **Dependency:** Phase 3 backend & frontend code
- **Tasks:**
  - Generate Dockerfile for backend (FastAPI application)
  - Generate Dockerfile for frontend (Next.js ChatKit UI)
  - Create .dockerignore files for both services
  - Build Docker images using Gordon (Docker AI)
  - Tag images as todo-backend:latest and todo-frontend:latest

### Step 2: Helm Chart Generation
- **Agent:** helm-chart-engineer
- **Output:** charts/todo-backend/ and charts/todo-frontend/
- **Estimated time:** 30–45 minutes
- **Dependency:** Docker images built
- **Tasks:**
  - Create Helm chart templates for backend service
  - Create Helm chart templates for frontend service
  - Define deployments with replica counts ≥ 2
  - Configure services (ClusterIP) for internal communication
  - Set up liveness and readiness probes
  - Configure environment variables as secrets/configmaps
  - Validate Helm chart structure and dependencies

### Step 3: Minikube Cluster Setup & Deployment
- **Agent:** minikube-deployer
- **Commands:** minikube start, helm install, port-forward
- **Estimated time:** 15–25 minutes
- **Dependency:** Helm charts ready
- **Tasks:**
  - Start Minikube cluster with appropriate resources
  - Apply namespace configuration if needed
  - Install Helm charts using helm install command
  - Verify pod creation and status
  - Set up port-forwarding for local access (port 8000 and 3000)
  - Confirm service accessibility within cluster

### Step 4: Validation & Testing
- **Agent:** deployment-tester
- **Tests:** pods ready, API/UI responsive, todo CRUD via chat
- **Estimated time:** 15–20 minutes
- **Dependency:** Deployment successful
- **Tasks:**
  - Verify all pods are Running/Ready status
  - Test backend API endpoints (localhost:8000)
  - Confirm frontend UI loads correctly (localhost:3000)
  - Execute todo management commands via chat interface
  - Validate Better Auth integration
  - Confirm database connectivity and persistence
  - Test scalability features (kubectl scale)

### Step 5: Troubleshooting & Optimization (if needed)
- **Agent:** aiops-troubleshooter
- **Commands:** logs, describe, kubectl-ai, kagent analysis
- **Estimated time:** 10–30 minutes (reactive)
- **Dependency:** Issues identified during testing
- **Tasks:**
  - Analyze pod logs for errors
  - Describe problematic resources
  - Generate optimization recommendations
  - Apply fixes based on kubectl-ai suggestions
  - Perform health checks using kagent
  - Re-run validation after fixes

### Step 6: Final Documentation & Cleanup
- **Agent:** infra-spec-writer (update if needed)
- **Update:** README-phase4.md with steps & demo screenshots
- **Estimated time:** 10–15 minutes
- **Dependency:** All previous steps completed successfully
- **Tasks:**
  - Document deployment steps and commands
  - Add troubleshooting tips from aiops-troubleshooter
  - Include sample output and expected results
  - Take screenshots of deployed UI and cluster status
  - Update any necessary references in documentation
  - Verify cleanup of temporary files if any

## Timeline Summary

| Step | Estimated Time | Dependency | Status |
|------|----------------|------------|--------|
| 1. Containerization | 20–30 min | Phase 3 code | Pending |
| 2. Helm Charts | 30–45 min | Docker images | Pending |
| 3. Deployment | 15–25 min | Helm charts | Pending |
| 4. Testing | 15–20 min | Deployment | Pending |
| 5. Troubleshooting | 10–30 min | As needed | Pending |
| 6. Documentation | 10–15 min | All previous | Pending |
| **Total** | **~1.5–3 hours** | **-** | **-** |

## Risks & Contingencies

| Risk | Probability | Mitigation / Agent |
|------|-------------|---------------------|
| Image pull error | Medium | minikube ssh docker images check, docker-engineer |
| Pod crash / OOM | High | aiops-troubleshooter + kubectl-ai analysis |
| Port conflicts | Medium | Dynamic port selection, minikube-deployer |
| Resource constraints | Medium | Adjust resource limits in Helm charts |
| Network connectivity | Low | Verify service networking, check DNS |
| Missing dependencies | Low | Pre-flight checks, docker-engineer validation |

## Success Metrics
- [ ] Minikube cluster operational
- [ ] Both deployments showing ≥2 replicas Ready
- [ ] Backend API responding on localhost:8000
- [ ] Frontend UI loading on localhost:3000
- [ ] Todo CRUD operations functional via chat
- [ ] All health checks passing
- [ ] Documentation complete and accurate