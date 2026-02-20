# Certificate Management

Manage TLS/SSL certificates for the Todo AI Chatbot.

## Usage
```
/cert [operation] [domain]
```

## Arguments
- `operation`: Operation (create/renew/list/delete/verify)
- `domain` (optional): Domain name for certificate

## What it does
1. **create**: Creates new TLS certificate (Let's Encrypt/cert-manager)
2. **renew**: Renews expiring certificates
3. **list**: Lists all certificates and expiry dates
4. **delete**: Removes certificate
5. **verify**: Verifies certificate validity

## Example
```
/cert create todo.example.com
/cert list
/cert renew todo.example.com
/cert verify
```
