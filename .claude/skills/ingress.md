# Configure Ingress

Configure ingress and routing for the Todo AI Chatbot.

## Usage
```
/ingress [operation]
```

## Arguments
- `operation` (optional): Operation (setup/update/tls/status). Default: setup

## What it does
1. **setup**: Creates ingress configuration with routing rules
2. **update**: Updates existing ingress rules
3. **tls**: Configures TLS/SSL certificates
4. **status**: Shows ingress status and endpoints

Includes:
- Nginx/Traefik ingress controller setup
- Path-based routing
- Host-based routing
- TLS certificate management
- Rate limiting and CORS

## Example
```
/ingress setup
/ingress tls
/ingress status
```
