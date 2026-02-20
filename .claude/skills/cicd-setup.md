# Setup CI/CD

Setup continuous integration and deployment pipeline.

## Usage
```
/cicd-setup [platform]
```

## Arguments
- `platform` (optional): CI/CD platform (github-actions/gitlab-ci/jenkins). Default: github-actions

## What it does
1. Creates CI/CD workflow files
2. Configures build and test stages
3. Sets up deployment automation
4. Configures secrets and environment variables
5. Adds quality gates and checks

## Example
```
/cicd-setup
/cicd-setup github-actions
```
