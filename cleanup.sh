#!/bin/bash

# SimpleWeb Operator - Cleanup Script
# This script removes all operator resources from the cluster

set -e  # Exit on error

echo "=========================================="
echo "SimpleWeb Operator Cleanup Script"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}⚠ This will delete all SimpleWeb resources and the operator.${NC}"
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""

# Step 1: Delete test applications
echo -e "${RED}[1/4] Deleting SimpleWeb resources...${NC}"
kubectl delete -f examples/test-app.yaml --ignore-not-found=true
kubectl delete simplewebs --all --all-namespaces --ignore-not-found=true
echo -e "${GREEN}✓ SimpleWeb resources deleted${NC}"
echo ""

# Step 2: Delete operator
echo -e "${RED}[2/4] Deleting operator deployment...${NC}"
kubectl delete -f manifests/03-operator.yaml --ignore-not-found=true
echo -e "${GREEN}✓ Operator deleted${NC}"
echo ""

# Step 3: Delete RBAC
echo -e "${RED}[3/4] Deleting RBAC configuration...${NC}"
kubectl delete -f manifests/02-rbac.yaml --ignore-not-found=true
echo -e "${GREEN}✓ RBAC deleted${NC}"
echo ""

# Step 4: Delete CRD
echo -e "${RED}[4/4] Deleting Custom Resource Definition...${NC}"
kubectl delete -f manifests/01-crd.yaml --ignore-not-found=true
echo -e "${GREEN}✓ CRD deleted${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}Cleanup Complete!${NC}"
echo "=========================================="
echo ""
echo "All SimpleWeb operator resources have been removed from the cluster."
echo ""
