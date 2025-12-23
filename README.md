# Kubernetes Operator with Kopf

A production-ready Kubernetes Operator built with Python and `kopf` that manages `SimpleWeb` custom resources.

## Overview

This operator automatically creates and manages Kubernetes Deployments and Services based on `SimpleWeb` custom resource definitions. When you create a `SimpleWeb` resource, the operator reconciles the state by:
- Creating a Deployment with the specified image, replicas, and port
- Creating a Service to expose the Deployment
- Automatically updating resources when the CR changes
- Cleaning up resources when the CR is deleted (via owner references)

## Architecture

```
SimpleWeb CR → Operator (kopf) → Deployment + Service
```

## Project Structure

```
simpleweb-operator/
├── src/
│   └── operator.py              # Core operator logic
├── manifests/
│   ├── 01-crd.yaml              # Custom Resource Definition
│   ├── 02-rbac.yaml             # RBAC (ServiceAccount, ClusterRole, Binding)
│   └── 03-operator.yaml         # Operator Deployment
├── examples/
│   └── test-app.yaml            # Sample SimpleWeb resource
├── Dockerfile                   # Container image for the operator
├── requirements.txt             # Python dependencies
├── deploy.sh                    # Automated deployment script
├── cleanup.sh                   # Automated cleanup script
├── .gitignore                   # Git exclusions
└── README.md                    # This file
```

## Prerequisites

- Kubernetes cluster (Minikube, Kind, or any K8s cluster)
- Docker
- kubectl configured to access your cluster

## Quick Start

### Option A: Automated Deployment (Recommended)

```bash
# Make the script executable
chmod +x deploy.sh

# Run the automated deployment
./deploy.sh
```

The script will automatically:
1. Build the Docker image
2. Load it into your cluster (Minikube/Kind)
3. Apply all manifests in the correct order
4. Wait for the operator to be ready

### Option B: Manual Deployment

### 1. Build the Docker Image

```bash
docker build -t simpleweb-operator:latest .
```

### 2. Load the Image into Your Cluster

**For Minikube:**
```bash
minikube image load simpleweb-operator:latest
```

**For Kind:**
```bash
kind load docker-image simpleweb-operator:latest
```

**For Remote Cluster:**
```bash
# Tag and push to your registry
docker tag simpleweb-operator:latest your-registry/simpleweb-operator:latest
docker push your-registry/simpleweb-operator:latest

# Update operator-manifests.yaml with your image path
```

### 3. Deploy the CRD

```bash
kubectl apply -f manifests/01-crd.yaml
```

Verify the CRD is created:
```bash
kubectl get crd simplewebs.ops.example.com
```

### 4. Deploy RBAC and Operator

```bash
kubectl apply -f manifests/02-rbac.yaml
kubectl apply -f manifests/03-operator.yaml
```

Verify the operator is running:
```bash
kubectl get pods -n default
kubectl logs -f deployment/simpleweb-operator
```

### 5. Create a SimpleWeb Resource

```bash
kubectl apply -f examples/test-app.yaml
```

### 6. Verify the Resources

Check that the operator created the Deployment and Service:

```bash
# Check the SimpleWeb resource
kubectl get simpleweb

# Check the created Deployment
kubectl get deployment test-app

# Check the created Service
kubectl get service test-app

# Check the pods
kubectl get pods -l app=test-app

# View operator logs
kubectl logs -f deployment/simpleweb-operator
```

## Testing Updates

Modify the `examples/test-app.yaml` to change replicas or image:

```bash
# Edit the file to change replicas from 2 to 3
kubectl apply -f examples/test-app.yaml

# Watch the operator reconcile
kubectl logs -f deployment/simpleweb-operator
```

## Testing Deletion

```bash
# Delete the SimpleWeb resource
kubectl delete -f examples/test-app.yaml

# Verify that the Deployment and Service are also deleted (garbage collection)
kubectl get deployment test-app
kubectl get service test-app
```

## Custom Resource Specification

The `SimpleWeb` CRD accepts the following spec fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `image` | string | Container image to deploy | Yes |
| `port` | integer | Container port to expose | Yes |
| `replicas` | integer | Number of pod replicas | Yes |

Example:

```yaml
apiVersion: ops.example.com/v1
kind: SimpleWeb
metadata:
  name: my-webapp
spec:
  image: nginx:latest
  port: 80
  replicas: 2
```

## Operator Features

### Create Handler
- Automatically creates a Deployment and Service when a SimpleWeb resource is created
- Sets owner references for automatic garbage collection
- Logs all creation events

### Update Handler
- Detects changes to `image` and `replicas` fields
- Patches the existing Deployment with new values
- Logs all update events

### Delete Handler
- Kubernetes automatically deletes child resources (Deployment, Service) via owner references
- No manual cleanup required

### Resiliency
- Uses `kopf.append_owner_reference` for proper resource ownership
- Implements proper error handling and logging
- Supports idempotent operations

## Troubleshooting

### Operator Pod Not Starting

```bash
# Check operator logs
kubectl logs deployment/simpleweb-operator

# Check RBAC permissions
kubectl auth can-i create deployments --as=system:serviceaccount:default:simpleweb-operator
kubectl auth can-i create services --as=system:serviceaccount:default:simpleweb-operator
```

### Image Pull Errors

If using local images, ensure `imagePullPolicy: Never` or `IfNotPresent` is set in `operator-manifests.yaml`.

### CRD Not Found

```bash
# Verify CRD exists
kubectl get crd simplewebs.ops.example.com

# Re-apply if needed
kubectl apply -f crd.yaml
```

### Resources Not Created

```bash
# Check operator logs for errors
kubectl logs -f deployment/simpleweb-operator

# Verify the SimpleWeb resource was created
kubectl get simpleweb -o yaml
```

## Development

### Local Testing (Outside Cluster)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the operator locally (requires kubeconfig)
kopf run src/operator.py --verbose
```

### Modifying the Operator

1. Edit `src/operator.py`
2. Rebuild the Docker image
3. Reload into cluster
4. Restart the operator pod:
   ```bash
   kubectl rollout restart deployment/simpleweb-operator
   ```

## Cleanup

### Option A: Automated Cleanup (Recommended)

```bash
# Make the script executable
chmod +x cleanup.sh

# Run the cleanup script
./cleanup.sh
```

### Option B: Manual Cleanup

Remove all resources:

```bash
# Delete SimpleWeb resources
kubectl delete -f examples/test-app.yaml

# Delete operator
kubectl delete -f manifests/03-operator.yaml
kubectl delete -f manifests/02-rbac.yaml

# Delete CRD (this will delete all SimpleWeb resources)
kubectl delete -f manifests/01-crd.yaml
```

## Security Considerations

- The operator runs with a ServiceAccount with minimal required permissions
- RBAC is scoped to only necessary resources
- Consider using namespace-scoped roles instead of ClusterRole for production
- Implement network policies to restrict operator communication

## Production Recommendations

1. **Image Registry**: Push images to a private registry
2. **Resource Limits**: Add resource requests/limits to operator Deployment
3. **High Availability**: Run multiple operator replicas with leader election
4. **Monitoring**: Add Prometheus metrics via kopf
5. **Logging**: Integrate with centralized logging (ELK, Loki)
6. **Validation**: Add webhook validation for SimpleWeb resources
7. **Testing**: Implement unit and integration tests

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
