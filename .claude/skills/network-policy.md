# Network Policy

Configure network policies for the Todo AI Chatbot.

## Usage
```
/network-policy [operation]
```

## Arguments
- `operation`: Operation (create/list/update/delete/test)

## What it does
1. **create**: Creates network policy for pod communication
2. **list**: Shows all network policies
3. **update**: Updates existing policy
4. **delete**: Removes network policy
5. **test**: Tests network connectivity between pods

Includes:
- Ingress rules (incoming traffic)
- Egress rules (outgoing traffic)
- Pod selector labels
- Namespace isolation

## Example
```
/network-policy create
/network-policy list
/network-policy test
```
