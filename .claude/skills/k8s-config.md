# Generate Kubernetes Config

Create or modify Kubernetes configurations, Helm charts, or GitHub Actions workflows.

## Usage
```
/k8s-config [type]
```

## Arguments
- `type` (optional): Configuration type (deployment/service/ingress/helm/cicd). Default: prompts for selection

## What it does
Uses the k8s-config-generator agent to:
1. Generate deployment manifests
2. Create Helm charts
3. Setup CI/CD pipelines
4. Configure services and ingresses
5. Create infrastructure-as-code YAML files

## Example
```
/k8s-config
/k8s-config helm
/k8s-config cicd
```
