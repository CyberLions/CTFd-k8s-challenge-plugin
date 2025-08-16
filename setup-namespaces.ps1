# Setup script for CTFd Kubernetes Challenge Plugin with nginx-ingress
# This script creates the required namespaces and sets up initial configuration

Write-Host "Setting up CTFd Kubernetes Challenge Plugin with nginx-ingress..." -ForegroundColor Green

# Create required namespaces
Write-Host "Creating namespaces..." -ForegroundColor Yellow
kubectl create namespace ctfd-challenges --dry-run=client -o yaml | kubectl apply -f -

# Create a secret for the registry authentication
Write-Host "Creating registry authentication secret..." -ForegroundColor Yellow
kubectl create secret docker-registry registry-auth `
  --docker-server=registry.psuccso.org `
  --docker-username=robot`$rancher `
  --docker-password=g1TqDg5SqhTuDCVn7N8uIKsS64xpPQ2z `
  --namespace=ctfd-challenges `
  --dry-run=client -o yaml | kubectl apply -f -

Write-Host "Namespaces and secrets created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. The config.yaml file has been updated with your specific values" -ForegroundColor White
<<<<<<< Updated upstream
Write-Host "2. Git credentials will be entered manually through CTFd web interface" -ForegroundColor White
=======
<<<<<<< HEAD
Write-Host "2. Git credentials will be entered manually through CTFd web interface" -ForegroundColor White
=======
Write-Host "2. Git credentials are configured: 23younesm" -ForegroundColor White
>>>>>>> d8d7ab8 (Cursor)
>>>>>>> Stashed changes
Write-Host "3. Registry is configured: registry.psuccso.org" -ForegroundColor White
Write-Host "4. Restart CTFd to deploy the plugin resources" -ForegroundColor White
Write-Host ""
Write-Host "Note: Your nginx-ingress controller is properly configured" -ForegroundColor Yellow
Write-Host "and can handle the wildcard domain *.ctf.psuccso.org" -ForegroundColor Yellow
Write-Host ""
Write-Host "Storage class 'longhorn' will be used for persistent volumes" -ForegroundColor Yellow
<<<<<<< Updated upstream
Write-Host ""
Write-Host "IMPORTANT: After restarting CTFd, go to /admin/kubernetes" -ForegroundColor Yellow
Write-Host "and update the Git credentials in the web interface" -ForegroundColor Yellow
=======
<<<<<<< HEAD
Write-Host ""
Write-Host "IMPORTANT: After restarting CTFd, go to /admin/kubernetes" -ForegroundColor Yellow
Write-Host "and update the Git credentials in the web interface" -ForegroundColor Yellow
=======
>>>>>>> d8d7ab8 (Cursor)
>>>>>>> Stashed changes
