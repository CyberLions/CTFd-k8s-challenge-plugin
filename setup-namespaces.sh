#!/bin/bash

# Setup script for CTFd Kubernetes Challenge Plugin with nginx-ingress
# This script creates the required namespaces and sets up initial configuration

echo "Setting up CTFd Kubernetes Challenge Plugin with nginx-ingress..."

# Create required namespaces
echo "Creating namespaces..."
kubectl create namespace ctfd-challenges --dry-run=client -o yaml | kubectl apply -f -

# Create a secret for the registry authentication
echo "Creating registry authentication secret..."
kubectl create secret docker-registry registry-auth \
  --docker-server=registry.psuccso.org \
  --docker-username=robot\$rancher \
  --docker-password=g1TqDg5SqhTuDCVn7N8uIKsS64xpPQ2z \
  --namespace=ctfd-challenges \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Namespaces and secrets created successfully!"
echo ""
echo "Next steps:"
echo "1. The config.yaml file has been updated with your specific values"
<<<<<<< Updated upstream
echo "2. Git credentials will be entered manually through CTFd web interface"
=======
<<<<<<< HEAD
echo "2. Git credentials will be entered manually through CTFd web interface"
=======
echo "2. Git credentials are configured: 23younesm"
>>>>>>> d8d7ab8 (Cursor)
>>>>>>> Stashed changes
echo "3. Registry is configured: registry.psuccso.org"
echo "4. Restart CTFd to deploy the plugin resources"
echo ""
echo "Note: Your nginx-ingress controller is properly configured"
echo "and can handle the wildcard domain *.ctf.psuccso.org"
echo ""
echo "Storage class 'longhorn' will be used for persistent volumes"
<<<<<<< Updated upstream
echo ""
echo "IMPORTANT: After restarting CTFd, go to /admin/kubernetes"
echo "and update the Git credentials in the web interface"
=======
<<<<<<< HEAD
echo ""
echo "IMPORTANT: After restarting CTFd, go to /admin/kubernetes"
echo "and update the Git credentials in the web interface"
=======
>>>>>>> d8d7ab8 (Cursor)
>>>>>>> Stashed changes
