# SimpleWeb Operator - Quick Reference Guide

## 🚀 Quick Commands

### Deployment
```bash
# Automated (recommended)
./deploy.sh

# Manual
docker build -t simpleweb-operator:latest .
minikube image load simpleweb-operator:latest
kubectl apply -f manifests/01-crd.yaml
kubectl apply -f manifests/02-rbac.yaml
kubectl apply -f manifests/03-operator.yaml
```

### Create a SimpleWeb App
```bash
kubectl apply -f examples/test-app.yaml
```

### Check Status
```bash
# List all SimpleWeb resources
kubectl get simpleweb
kubectl get sw  # short name

# Detailed view
kubectl describe simpleweb test-app

# Check created resources
kubectl get deployment test-app
kubectl get service test-app
kubectl get pods -l app=test-app

# View operator logs
kubectl logs -f deployment/simpleweb-operator
```

### Update a SimpleWeb App
```bash
# Edit the YAML file
vim examples/test-app.yaml

# Apply changes
kubectl apply -f examples/test-app.yaml

# Watch reconciliation
kubectl logs -f deployment/simpleweb-operator
```

### Delete a SimpleWeb App
```bash
kubectl delete -f examples/test-app.yaml
# Child resources (Deployment, Service) are automatically deleted
```

### Cleanup Everything
```bash
# Automated
./cleanup.sh

# Manual
kubectl delete -f examples/test-app.yaml
kubectl delete -f manifests/03-operator.yaml
kubectl delete -f manifests/02-rbac.yaml
kubectl delete -f manifests/01-crd.yaml
```

## 📝 SimpleWeb Resource Template

```yaml
apiVersion: ops.example.com/v1
kind: SimpleWeb
metadata:
  name: my-app
  namespace: default
spec:
  image: nginx:latest      # Container image
  port: 80                 # Container port (1-65535)
  replicas: 2              # Number of replicas (min: 1)
```

## 🔍 Troubleshooting

### Operator Not Starting
```bash
# Check operator pod status
kubectl get pods -l app=simpleweb-operator

# View logs
kubectl logs deployment/simpleweb-operator

# Describe pod for events
kubectl describe pod -l app=simpleweb-operator
```

### Resources Not Created
```bash
# Check if CRD exists
kubectl get crd simplewebs.ops.example.com

# Check operator logs for errors
kubectl logs -f deployment/simpleweb-operator

# Verify SimpleWeb resource
kubectl get simpleweb -o yaml
```

### RBAC Issues
```bash
# Test permissions
kubectl auth can-i create deployments --as=system:serviceaccount:default:simpleweb-operator
kubectl auth can-i create services --as=system:serviceaccount:default:simpleweb-operator

# View role bindings
kubectl get clusterrolebinding simpleweb-operator-binding -o yaml
```

### Image Pull Errors
```bash
# For Minikube
minikube image ls | grep simpleweb-operator

# Reload image if needed
minikube image load simpleweb-operator:latest

# For Kind
kind load docker-image simpleweb-operator:latest
```

## 🧪 Testing Scenarios

### Scenario 1: Basic Deployment
```bash
kubectl apply -f examples/test-app.yaml
kubectl wait --for=condition=ready pod -l app=test-app --timeout=60s
kubectl get all -l app=test-app
```

### Scenario 2: Scale Up
```bash
# Edit test-app.yaml: replicas: 2 → 5
kubectl apply -f examples/test-app.yaml
kubectl get pods -l app=test-app -w
```

### Scenario 3: Image Update
```bash
# Edit test-app.yaml: image: nginx:latest → nginx:alpine
kubectl apply -f examples/test-app.yaml
kubectl rollout status deployment/test-app
```

### Scenario 4: Port Change
```bash
# Edit test-app.yaml: port: 80 → 8080
kubectl apply -f examples/test-app.yaml
kubectl get service test-app -o yaml | grep port
```

### Scenario 5: Garbage Collection
```bash
kubectl apply -f examples/test-app.yaml
kubectl get deployment test-app
kubectl delete simpleweb test-app
sleep 5
kubectl get deployment test-app  # Should be gone
```

## 📊 Monitoring

### Watch Operator Activity
```bash
# Follow logs in real-time
kubectl logs -f deployment/simpleweb-operator

# View recent events
kubectl get events --sort-by='.lastTimestamp' | grep simpleweb
```

### Resource Usage
```bash
# Operator resource usage
kubectl top pod -l app=simpleweb-operator

# Managed app resource usage
kubectl top pod -l app=test-app
```

### Health Checks
```bash
# Check operator pod health
kubectl get pod -l app=simpleweb-operator -o jsonpath='{.items[0].status.conditions}'

# Check deployment status
kubectl get deployment simpleweb-operator -o jsonpath='{.status.conditions}'
```

## 🛠️ Development

### Local Development (Outside Cluster)
```bash
# Install dependencies
pip install -r requirements.txt

# Run operator locally
export KUBECONFIG=~/.kube/config
kopf run src/operator.py --verbose

# In another terminal, test
kubectl apply -f examples/test-app.yaml
```

### Debug Mode
```bash
# Run with maximum verbosity
kopf run src/operator.py --verbose --debug
```

### Code Changes
```bash
# After editing src/operator.py
docker build -t simpleweb-operator:latest .
minikube image load simpleweb-operator:latest
kubectl rollout restart deployment/simpleweb-operator
kubectl logs -f deployment/simpleweb-operator
```

## 📚 Common Use Cases

### Deploy Multiple Apps
```bash
# Create multiple SimpleWeb resources
kubectl apply -f - <<EOF
apiVersion: ops.example.com/v1
kind: SimpleWeb
metadata:
  name: frontend
spec:
  image: nginx:alpine
  port: 80
  replicas: 3
---
apiVersion: ops.example.com/v1
kind: SimpleWeb
metadata:
  name: backend
spec:
  image: httpd:alpine
  port: 8080
  replicas: 2
EOF

# List all
kubectl get simpleweb
```

### Different Namespaces
```bash
# Create namespace
kubectl create namespace dev

# Deploy to namespace
kubectl apply -f examples/test-app.yaml -n dev

# View resources
kubectl get simpleweb -n dev
kubectl get deployment -n dev
```

### Custom Image
```bash
kubectl apply -f - <<EOF
apiVersion: ops.example.com/v1
kind: SimpleWeb
metadata:
  name: custom-app
spec:
  image: your-registry/your-app:v1.0.0
  port: 3000
  replicas: 4
EOF
```

## 🔐 Security Best Practices

### Review RBAC Permissions
```bash
kubectl get clusterrole simpleweb-operator-role -o yaml
```

### Check Security Context
```bash
kubectl get pod -l app=simpleweb-operator -o jsonpath='{.items[0].spec.securityContext}'
```

### Audit Events
```bash
kubectl get events --field-selector involvedObject.kind=SimpleWeb
```

## 📖 Additional Resources

- **Full Documentation**: See README.md
- **Project Summary**: See PROJECT_SUMMARY.md
- **Source Code**: src/operator.py
- **Manifests**: manifests/
- **Examples**: examples/

---

**Last Updated**: 2025-12-22  
**Version**: 1.0.0  
**Status**: Production-Ready ✅
