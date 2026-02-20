# Cloud Deploy

Deploy Todo AI Chatbot to cloud Kubernetes (AKS/GKE).

## Usage
```
/cloud-deploy [provider] [environment]
```

## Arguments
- `provider`: Cloud provider (azure/gcp/aws). Default: prompts for selection
- `environment`: Environment (dev/staging/prod). Default: dev

## What it does
1. Creates cloud Kubernetes cluster
2. Configures kubectl context
3. Sets up ingress with HTTPS
4. Configures DNS records
5. Deploys application with Helm
6. Sets up monitoring and logging
7. Configures auto-scaling
8. Runs smoke tests

## Providers

### Azure (AKS)
- Creates AKS cluster
- Configures Azure Container Registry
- Sets up Application Gateway
- Integrates with Azure Monitor

### Google Cloud (GKE)
- Creates GKE cluster
- Configures Google Container Registry
- Sets up Cloud Load Balancer
- Integrates with Cloud Monitoring

### AWS (EKS)
- Creates EKS cluster
- Configures ECR
- Sets up ALB/NLB
- Integrates with CloudWatch

## Features
- SSL/TLS certificates (Let's Encrypt)
- Custom domain configuration
- Secret management (cloud native)
- Database (managed PostgreSQL)
- Redis cache (managed)
- Kafka (managed or self-hosted)

## Example
```
/cloud-deploy azure dev
/cloud-deploy gcp prod
/cloud-deploy aws staging
```
