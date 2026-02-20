# Deploy Application

Deploy the Todo AI Chatbot to Kubernetes using Helm.

## Usage
```
/deploy [environment]
```

## Arguments
- `environment` (optional): Target environment (dev/staging/prod). Default: dev

## What it does
1. Checks current Kubernetes context
2. Deploys backend and frontend using Helm charts
3. Verifies deployment status
4. Shows service endpoints

## Example
```
/deploy
/deploy prod
```
