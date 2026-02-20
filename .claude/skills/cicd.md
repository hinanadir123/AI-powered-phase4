# CI/CD Pipeline

Manage CI/CD pipelines for the Todo AI Chatbot.

## Usage
```
/cicd [operation] [pipeline]
```

## Arguments
- `operation`: Operation (create/run/status/logs/cancel)
- `pipeline` (optional): Pipeline name (build/test/deploy/release)

## What it does

### create
- Creates GitHub Actions workflow
- Configures pipeline stages
- Sets up secrets and variables

### run
- Triggers pipeline manually
- Runs specific workflow
- Passes custom parameters

### status
- Shows pipeline status
- Displays recent runs
- Shows success/failure rates

### logs
- Shows pipeline logs
- Filters by stage
- Downloads artifacts

### cancel
- Cancels running pipeline
- Cleans up resources

## Pipeline Stages

### Build
1. Checkout code
2. Install dependencies
3. Run linters
4. Build Docker images
5. Push to registry

### Test
1. Unit tests
2. Integration tests
3. E2E tests
4. Security scans
5. Code coverage

### Deploy
1. Update Helm values
2. Deploy to cluster
3. Run smoke tests
4. Health checks
5. Notify team

### Release
1. Create release tag
2. Generate changelog
3. Build artifacts
4. Deploy to production
5. Post-deployment tests

## Example
```
/cicd status
/cicd run build
/cicd logs deploy --stage=test
/cicd create --template=nodejs
```
