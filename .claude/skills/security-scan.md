# Security Scan

Run security scans on the Todo AI Chatbot.

## Usage
```
/security-scan [scan-type]
```

## Arguments
- `scan-type` (optional): Scan type (all/images/code/dependencies/secrets/network). Default: all

## What it does

### images
- Scans Docker images for vulnerabilities
- Uses Trivy or similar tools
- Reports CVEs and severity
- Suggests fixes

### code
- Static code analysis
- Identifies security issues
- Checks for common vulnerabilities
- OWASP Top 10 compliance

### dependencies
- Scans npm/pip packages
- Identifies vulnerable dependencies
- Suggests updates
- Checks for known exploits

### secrets
- Scans for exposed secrets
- Checks for hardcoded credentials
- Validates secret management
- Reviews access controls

### network
- Tests network policies
- Validates TLS configuration
- Checks for open ports
- Reviews firewall rules

## Security Checks

### Application
- SQL injection
- XSS vulnerabilities
- CSRF protection
- Authentication/Authorization
- Input validation

### Infrastructure
- Container security
- Kubernetes RBAC
- Network segmentation
- Secret encryption
- TLS/SSL configuration

### Compliance
- OWASP Top 10
- CIS Benchmarks
- PCI DSS (if applicable)
- GDPR compliance

## Example
```
/security-scan
/security-scan images
/security-scan dependencies --fix
/security-scan secrets --report
```
