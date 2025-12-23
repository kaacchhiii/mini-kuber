# Kubernetes Operator with Kopf

A production-ready Kubernetes Operator built with Python and `kopf` that manages `SimpleWeb` custom resources.

## Overview

This operator automatically creates and manages Kubernetes Deployments and Services based on `SimpleWeb` custom resource definitions.

## Project Structure

```
simpleweb-operator/
├── src/
│   └── operator.py
├── manifests/
│   ├── 01-crd.yaml
│   ├── 02-rbac.yaml
│   └── 03-operator.yaml
├── examples/
│   └── test-app.yaml
├── Dockerfile
├── requirements.txt
├── deploy.sh
├── cleanup.sh
└── README.md
```

## Quick Start

### Automated Deployment

```bash
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

```bash
docker build -t simpleweb-operator:latest .
minikube image load simpleweb-operator:latest
kubectl apply -f manifests/01-crd.yaml
kubectl apply -f manifests/02-rbac.yaml
kubectl apply -f manifests/03-operator.yaml
```

### Deploy Test Application

```bash
kubectl apply -f examples/test-app.yaml
```

### Verify

```bash
kubectl get simpleweb
kubectl get deployment test-app
kubectl get service test-app
kubectl get pods -l app=test-app
kubectl logs -f deployment/simpleweb-operator
```

## Custom Resource Specification

```yaml
apiVersion: ops.example.com/v1
kind: SimpleWeb
metadata:
  name: my-app
spec:
  image: nginx:latest
  port: 80
  replicas: 2
```

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `image` | string | Container image to deploy | Yes |
| `port` | integer | Container port (1-65535) | Yes |
| `replicas` | integer | Number of replicas (min: 1) | Yes |

## Features

- **Create Handler**: Auto-creates Deployment + Service
- **Update Handler**: Patches resources when spec changes
- **Delete Handler**: Automatic cleanup via owner references
- **RBAC**: Minimal required permissions
- **Security**: Non-root containers, resource limits
- **Logging**: Structured logging with clear indicators

## Common Commands

### Update Application

```bash
kubectl apply -f examples/test-app.yaml
```

### Scale Application

```bash
kubectl patch simpleweb test-app --type='merge' -p '{"spec":{"replicas":5}}'
```

### Delete Application

```bash
kubectl delete -f examples/test-app.yaml
```

### View Logs

```bash
kubectl logs -f deployment/simpleweb-operator
```

## Cleanup

### Automated

```bash
chmod +x cleanup.sh
./cleanup.sh
```

### Manual

```bash
kubectl delete -f examples/test-app.yaml
kubectl delete -f manifests/03-operator.yaml
kubectl delete -f manifests/02-rbac.yaml
kubectl delete -f manifests/01-crd.yaml
```

## Troubleshooting

### Operator Not Starting

```bash
kubectl get pods -l app=simpleweb-operator
kubectl logs deployment/simpleweb-operator
kubectl describe pod -l app=simpleweb-operator
```

### Resources Not Created

```bash
kubectl get crd simplewebs.ops.example.com
kubectl logs -f deployment/simpleweb-operator
kubectl get simpleweb -o yaml
```

### RBAC Issues

```bash
kubectl auth can-i create deployments --as=system:serviceaccount:default:simpleweb-operator
kubectl auth can-i create services --as=system:serviceaccount:default:simpleweb-operator
```

### Image Pull Errors

```bash
minikube image ls | grep simpleweb-operator
minikube image load simpleweb-operator:latest
```

## Development

### Local Testing

```bash
pip install -r requirements.txt
kopf run src/operator.py --verbose
```

### Rebuild and Update

```bash
docker build -t simpleweb-operator:v2 .
minikube image load simpleweb-operator:v2
kubectl set image deployment/simpleweb-operator operator=simpleweb-operator:v2
```

## Production Recommendations

1. Push images to a private registry
2. Add resource requests/limits to operator Deployment
3. Run multiple operator replicas with leader election
4. Add Prometheus metrics via kopf
5. Integrate with centralized logging
6. Add webhook validation for SimpleWeb resources
7. Implement unit and integration tests

## License

MIT
