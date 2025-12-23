#!/bin/bash

# SimpleWeb Operator - Complete Deployment Script
# This script automates the entire deployment process

set -e  # Exit on error

echo "=========================================="
echo "SimpleWeb Operator Deployment Script"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Build Docker Image
echo -e "${BLUE}[1/6] Building Docker image...${NC}"
docker build -t simpleweb-operator:latest .
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Step 2: Load image into cluster
echo -e "${BLUE}[2/6] Loading image into cluster...${NC}"
# Detect cluster type
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "Detected Minikube cluster"
    minikube image load simpleweb-operator:latest
elif command -v kind &> /dev/null && kind get clusters &> /dev/null; then
    echo "Detected Kind cluster"
    kind load docker-image simpleweb-operator:latest
else
    echo -e "${YELLOW}⚠ Could not detect Minikube or Kind. Skipping image load.${NC}"
    echo "If using a remote cluster, push the image to your registry."
fi
echo -e "${GREEN}✓ Image loaded into cluster${NC}"
echo ""

# Step 3: Apply CRD
echo -e "${BLUE}[3/6] Applying Custom Resource Definition...${NC}"
kubectl apply -f manifests/01-crd.yaml
echo -e "${GREEN}✓ CRD applied${NC}"
echo ""

# Step 4: Apply RBAC
echo -e "${BLUE}[4/6] Applying RBAC configuration...${NC}"
kubectl apply -f manifests/02-rbac.yaml
echo -e "${GREEN}✓ RBAC applied${NC}"
echo ""

# Step 5: Deploy Operator
echo -e "${BLUE}[5/6] Deploying operator...${NC}"
kubectl apply -f manifests/03-operator.yaml
echo -e "${GREEN}✓ Operator deployed${NC}"
echo ""

# Step 6: Wait for operator to be ready
echo -e "${BLUE}[6/6] Waiting for operator to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=simpleweb-operator --timeout=60s
echo -e "${GREEN}✓ Operator is ready!${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Deploy a test application:"
echo "     kubectl apply -f examples/test-app.yaml"
echo ""
echo "  2. Check the operator logs:"
echo "     kubectl logs -f deployment/simpleweb-operator"
echo ""
echo "  3. Verify resources were created:"
echo "     kubectl get simpleweb"
echo "     kubectl get deployment test-app"
echo "     kubectl get service test-app"
echo ""
