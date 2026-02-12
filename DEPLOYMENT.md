# Phase 4: Kubernetes Deployment with Minikube

This document describes the deployment of the Todo AI Chatbot application to Kubernetes using Minikube and Helm.

## Architecture

The application consists of three main components:
- **Frontend**: Next.js application (NodePort service on port 30300)
- **Backend**: FastAPI application (NodePort service on port 30800)
- **Database**: PostgreSQL 15 (ClusterIP service)

## Prerequisites

- Docker Desktop installed and running
- Minikube installed
- Helm 3.x installed
- kubectl installed
- 4GB+ RAM available for Minikube

## Project Structure

```
phase-4/
├── backend/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   └── next.config.js
└── helm/
    ├── postgres.yaml
    ├── todo-backend/
    │   ├── Chart.yaml
    │   ├── values.yaml
    │   └── templates/
    │       ├── deployment.yaml
    │       ├── service.yaml
    │       └── secret.yaml
    └── todo-frontend/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── deployment.yaml
            └── service.yaml
```

## Deployment Steps

### 1. Build Docker Images

```bash
# Build backend image
cd backend
docker build -t todo-backend:latest .

# Build frontend image
cd ../frontend
docker build -t todo-frontend:latest .
```

### 2. Start Minikube

```bash
minikube start
```

### 3. Load Images into Minikube

```bash
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### 4. Deploy PostgreSQL

```bash
kubectl apply -f helm/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres --timeout=60s
```

### 5. Deploy Backend with Helm

```bash
helm install todo-backend helm/todo-backend
```

### 6. Deploy Frontend with Helm

```bash
helm install todo-frontend helm/todo-frontend
```

### 7. Verify Deployment

```bash
kubectl get pods,svc
```

All pods should show `Running` status.

## Accessing the Application

### Using Minikube Service Tunnels

```bash
# Access backend (in one terminal)
minikube service todo-backend --url

# Access frontend (in another terminal)
minikube service todo-frontend --url
```

The commands will output local URLs (e.g., http://127.0.0.1:xxxxx) that you can use to access the services.

### Using NodePort (Alternative)

Get the Minikube IP:
```bash
minikube ip
```

Access services at:
- Frontend: http://<minikube-ip>:30300
- Backend: http://<minikube-ip>:30800

## Configuration

### Backend Configuration

Edit `helm/todo-backend/values.yaml`:
- `env.DATABASE_URL`: PostgreSQL connection string
- `env.ANTHROPIC_API_KEY`: Your Anthropic API key (required for AI features)
- `env.CORS_ORIGINS`: Allowed CORS origins

### Frontend Configuration

Edit `helm/todo-frontend/values.yaml`:
- `env.NEXT_PUBLIC_BACKEND_URL`: Backend service URL
- `env.NEXT_PUBLIC_BACKEND_API_URL`: Backend API URL

## Troubleshooting

### Backend Pod CrashLoopBackOff

**Issue**: Missing Python dependencies (e.g., PyJWT)

**Solution**:
1. Update `backend/requirements.txt` with missing packages
2. Rebuild the Docker image
3. Delete old image from Minikube: `minikube image rm docker.io/library/todo-backend:latest`
4. Reload updated image: `minikube image load todo-backend:latest`
5. Restart deployment: `kubectl rollout restart deployment/todo-backend`

### Frontend Build Failures

**Issue**: TypeScript type mismatches or missing dependencies

**Solution**:
1. Ensure all type definitions are consistent across the codebase
2. Check that `next.config.js` has `output: 'standalone'` for Docker
3. Verify all imports use correct paths

### Minikube Not Starting

**Issue**: Docker Desktop not running or resource constraints

**Solution**:
1. Ensure Docker Desktop is running
2. Restart Docker Desktop if experiencing performance issues
3. Allocate more resources to Docker in Docker Desktop settings

### Cannot Access Services

**Issue**: Minikube service tunnels not working

**Solution**:
1. Use `minikube service <service-name> --url` to create tunnels
2. Keep the terminal window open while accessing services
3. Alternatively, use port-forwarding: `kubectl port-forward svc/todo-backend 8000:8000`

## Updating Deployments

### Update Backend

```bash
# Rebuild image
cd backend
docker build -t todo-backend:latest .

# Reload into Minikube
minikube image rm docker.io/library/todo-backend:latest
minikube image load todo-backend:latest

# Restart deployment
kubectl rollout restart deployment/todo-backend
```

### Update Frontend

```bash
# Rebuild image
cd frontend
docker build -t todo-frontend:latest .

# Reload into Minikube
minikube image rm docker.io/library/todo-frontend:latest
minikube image load todo-frontend:latest

# Restart deployment
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

## Health Checks

### Backend Health

```bash
curl http://<backend-url>/health
# Expected: {"status":"healthy"}
```

### Frontend Health

```bash
curl -I http://<frontend-url>
# Expected: HTTP/1.1 200 OK
```

## Monitoring

View logs:
```bash
# Backend logs
kubectl logs -l app=todo-backend --tail=50

# Frontend logs
kubectl logs -l app=todo-frontend --tail=50

# PostgreSQL logs
kubectl logs -l app=postgres --tail=50
```

## Known Issues

1. **Docker Desktop Performance**: On Windows, Docker Desktop may experience slow performance. Restarting the service can help.

2. **Image Caching**: Minikube caches images. Always remove old images before loading updated ones to ensure changes take effect.

3. **Service Tunnels**: The `minikube service --url` command requires keeping the terminal open. Consider using `kubectl port-forward` for persistent access.

## Production Considerations

This deployment is configured for local development with Minikube. For production:

1. Use a managed Kubernetes service (EKS, GKE, AKS)
2. Configure proper secrets management (not plaintext in values.yaml)
3. Set up persistent volumes for PostgreSQL
4. Configure ingress controllers instead of NodePort
5. Implement proper monitoring and logging
6. Set up CI/CD pipelines for automated deployments
7. Configure resource limits and autoscaling
8. Use production-grade PostgreSQL (managed service or StatefulSet)

## Support

For issues or questions, refer to:
- Minikube documentation: https://minikube.sigs.k8s.io/docs/
- Helm documentation: https://helm.sh/docs/
- Kubernetes documentation: https://kubernetes.io/docs/
