# Todo AI Chatbot - Phase 4: Kubernetes Deployment

An AI-powered task management application with natural language processing capabilities, deployed on Kubernetes using Minikube and Helm.

## Overview

This project is a full-stack application that allows users to manage tasks through a conversational AI interface. Phase 4 focuses on containerization and Kubernetes deployment.

**Key Components:**
- **Frontend**: Next.js 14 application with Material-UI components
- **Backend**: FastAPI application with AI-powered task management
- **Database**: PostgreSQL for data persistence
- **Deployment**: Kubernetes (Minikube) with Helm charts

## Features

- 🤖 AI-powered task creation and management through natural language
- 💬 Interactive chat interface for task operations
- ✅ Task completion tracking
- 🔐 User authentication and authorization
- 📱 Responsive web interface
- ☸️ Containerized deployment with Kubernetes
- 📦 Helm charts for easy deployment management

## Technology Stack

### Frontend
- Next.js 14
- React 18
- TypeScript
- Material-UI (MUI)
- Axios for API calls

### Backend
- FastAPI
- Python 3.11
- SQLModel (SQLAlchemy + Pydantic)
- PostgreSQL
- OpenAI/Anthropic API integration
- JWT authentication

### DevOps
- Docker
- Kubernetes (Minikube)
- Helm 3
- PostgreSQL 15

## Quick Start

### Prerequisites

- Docker Desktop
- Minikube
- Helm 3.x
- kubectl
- 4GB+ RAM available for Minikube

### Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

**Quick deployment:**

```bash
# 1. Build Docker images
cd backend && docker build -t todo-backend:latest .
cd ../frontend && docker build -t todo-frontend:latest .

# 2. Start Minikube
minikube start

# 3. Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# 4. Deploy PostgreSQL
kubectl apply -f helm/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres --timeout=60s

# 5. Deploy backend and frontend
helm install todo-backend helm/todo-backend
helm install todo-frontend helm/todo-frontend

# 6. Access services
minikube service todo-frontend --url
minikube service todo-backend --url
```

## Project Structure

```
phase-4/
├── backend/                 # FastAPI backend application
│   ── routes/             # API route handlers
│   ├── models/             # Database models
│   ├── schemas.py          # Pydantic schemas
│   ├── dependencies.py     # JWT authentication
│   ├── main.py             # Application entry point
│   ├── Dockerfile          # Backend container image
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Next.js frontend application
│   ├── app/               # Next.js app directory
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   └── types/         # TypeScript type definitions
│   ├── Dockerfile         # Frontend container image
│   └── package.json       # Node.js dependencies
│
├── helm/                   # Kubernetes Helm charts
│   ├── postgres.yaml      # PostgreSQL deployment
│   ├── todo-backend/      # Backend Helm chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   └── todo-frontend/     # Frontend Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── DEPLOYMENT.md          # Detailed deployment guide
└── README.md              # This file
```

## Configuration

### Backend Configuration

Edit `helm/todo-backend/values.yaml`:

```yaml
env:
  DATABASE_URL: "postgresql://postgres:postgres@postgres:5432/todo_db"
  ANTHROPIC_API_KEY: ""  # Add your API key here
  CORS_ORIGINS: "http://localhost:3000,http://localhost:30300"
```

### Frontend Configuration

Edit `helm/todo-frontend/values.yaml`:

```yaml
env:
  NEXT_PUBLIC_BACKEND_URL: "http://localhost:30800"
  NEXT_PUBLIC_BACKEND_API_URL: "http://localhost:30800/api"
```

## Accessing the Application

After deployment, use Minikube service tunnels to access the application:

```bash
# Frontend (keep terminal open)
minikube service todo-frontend --url
# Output: http://127.0.0.1:xxxxx

# Backend (in another terminal)
minikube service todo-backend --url
# Output: http://127.0.0.1:xxxxx
```

Open the frontend URL in your browser to use the application.

## API Endpoints

### Backend API

- `GET /health` - Health check endpoint
- `POST /api/{user_id}/chat` - Send chat message
- `GET /api/{user_id}/tasks` - Get user tasks
- `POST /api/{user_id}/tasks` - Create new task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task
- `POST /api/{user_id}/tasks/{task_id}/complete` - Mark task as complete

## Monitoring

View application logs:

```bash
# Backend logs
kubectl logs -l app=todo-backend -f

# Frontend logs
kubectl logs -l app=todo-frontend -f

# Database logs
kubectl logs -l app=postgres -f
```

Check pod status:

```bash
kubectl get pods,svc
```

## Troubleshooting

Common issues and solutions are documented in [DEPLOYMENT.md](./DEPLOYMENT.md#troubleshooting).

**Quick fixes:**

- **Backend crashes**: Check logs with `kubectl logs -l app=todo-backend`, verify dependencies
- **Frontend not loading**: Verify backend URL configuration in values.yaml
- **Database connection issues**: Ensure PostgreSQL pod is running
- **Service not accessible**: Use `minikube service <name> --url` to create tunnels

## Updating Deployments

### Update Backend

```bash
cd backend
docker build -t todo-backend:latest .
minikube image rm docker.io/library/todo-backend:latest
minikube image load todo-backend:latest
kubectl rollout restart deployment/todo-backend
```

### Update Frontend

```bash
cd frontend
docker build -t todo-frontend:latest .
minikube image rm docker.io/library/todo-frontend:latest
minikube image load todo-frontend:latest
kubectl rollout restart deployment/todo-frontend
```

## Cleanup

```bash
# Uninstall Helm releases
helm uninstall todo-backend
helm uninstall todo-frontend

# Delete PostgreSQL
kubectl delete -f helm/postgres.yaml

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Development

### Local Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Local Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Security Considerations

⚠️ **Important**: This deployment is configured for local development. For production:

1. Store secrets in Kubernetes Secrets or external secret managers
2. Use TLS/SSL certificates for HTTPS
3. Implement proper network policies
4. Use private container registries
5. Enable RBAC and pod security policies
6. Regular security updates and vulnerability scanning

## Architecture Decisions

### Why Minikube?

Minikube provides a local Kubernetes environment that closely mimics production clusters, making it ideal for development and testing.

### Why Helm?

Helm simplifies Kubernetes deployments by:
- Templating Kubernetes manifests
- Managing application versions
- Simplifying updates and rollbacks
- Providing a package management system

### Why NodePort Services?

For local development with Minikube, NodePort services provide easy access without requiring ingress controllers.

## Phase 4 Completion

✅ **All deployment tasks completed successfully:**

1. ✅ Setup Phase 4 Project Structure
2. ✅ Initialize Minikube and Verify Prerequisites
3. ✅ Containerize Backend Service with Docker
4. ✅ Containerize Frontend Service with Docker
5. ✅ Generate Helm Chart for Backend Service
6. ✅ Generate Helm Chart for Frontend Service
7. ✅ Deploy Application to Minikube
8. ✅ Validate Deployment and Test Functionality
9. ✅ Troubleshoot and Optimize Deployment
10. ✅ Document Deployment Process and Create README

## Support

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

For issues or questions:
- Check the troubleshooting section in DEPLOYMENT.md
- Review application logs using kubectl
- Verify all prerequisites are installed correctly

---

**Built with Claude Code** | **Hackathon Phase 4 Submission**
