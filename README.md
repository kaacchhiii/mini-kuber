# Kubernetes Operator with Kopf

A production-ready Kubernetes Operator built with Python and `kopf` that manages `SimpleWeb` custom resources.

## Overview

This operator automatically creates and manages Kubernetes Deployments and Services based on `SimpleWeb` custom resource definitions.

## What I Learnt

- **Kubernetes Controller Logic**: Learned the Observe-Diff-Act reconciliation loop.
- **Python-Based Ops**: Used `kopf` to bridge app logic and infrastructure.
- **CRDs**: Extended Kubernetes API with custom application types.
- **Events & Garbage Collection**: Managed async updates and auto-cleanup.

## What It Can Do

- **Automated Provisioning**: Generates Deployment and Service from a simple spec.
- **Smart Updates**: Detects and applies changes (e.g., image, replicas) instantly.
- **Self-Healing & Wiring**: Maintains state and routes traffic automatically.

## What You Can Use It For

- **Developer Platforms**: Simplify app deployment interfaces.
- **Standardization**: Enforce best practices automatically.
- **Education & Prototyping**: Learn operators or quickly spin up services.

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

## How to Run

**Option 1: Automated (Recommended)**
```bash
chmod +x deploy.sh && ./deploy.sh
```

**Option 2: Manual**
```bash
# Build & Load
docker build -t simpleweb-operator:latest .
minikube image load simpleweb-operator:latest

# Apply Manifests
kubectl apply -f manifests/
```

**Verify**
```bash
kubectl apply -f examples/test-app.yaml
kubectl get simpleweb,deployment,service
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



## Cheat Sheet

```bash
# Apply/Update
kubectl apply -f examples/test-app.yaml

# Scale (Patch)
kubectl patch simpleweb test-app --type='merge' -p '{"spec":{"replicas":5}}'

# Delete App
kubectl delete -f examples/test-app.yaml

# View Operator Logs
kubectl logs -f deployment/simpleweb-operator
```

## Cleanup

```bash
./cleanup.sh
# OR manually:
kubectl delete -f examples/test-app.yaml
kubectl delete -f manifests/
```

## Debugging

```bash
# Check Operator Status
kubectl get pods -l app=simpleweb-operator
kubectl describe pod -l app=simpleweb-operator

# Check Logs
kubectl logs deployment/simpleweb-operator

# Verify CRD & Resource
kubectl get crd simplewebs.ops.example.com
kubectl get simpleweb -o yaml

# Check Permissions
kubectl auth can-i create deployments --as=system:serviceaccount:default:simpleweb-operator
```

## Development

```bash
# Local Run
pip install -r requirements.txt
kopf run src/operator.py --verbose

# Rebuild
docker build -t simpleweb-operator:v2 . && minikube image load simpleweb-operator:v2
```

## Production Tips
1. Use private registry & version tags.
2. Set resource requests/limits.
3. Enable leader election & metrics.
4. Add centralized logging & tests.

## License

MIT
