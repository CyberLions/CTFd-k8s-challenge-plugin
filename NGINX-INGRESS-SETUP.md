# CTFd Kubernetes Challenge Plugin - nginx-ingress Setup

This document explains how to set up the CTFd Kubernetes Challenge Plugin to work with **nginx-ingress** instead of Istio.

## Changes Made

The plugin has been modified to work with nginx-ingress by:

1. **Removed Istio dependencies**: Eliminated Istio Gateway, VirtualService, and DestinationRule configurations
2. **Updated templates**: Modified all challenge templates to use nginx-ingress Ingress resources
3. **Simplified configuration**: Removed Istio-specific configuration options
4. **Updated database schema**: Removed Istio-related database columns

## Prerequisites

- Kubernetes cluster with nginx-ingress controller
- Calico networking (already configured in your setup)
- CTFd running in the `ctfd` namespace
- Access to create namespaces and secrets

## Setup Steps

### 1. Create Required Namespaces

Run the setup script to create the necessary namespaces:

**Linux/Mac:**
```bash
chmod +x setup-namespaces.sh
./setup-namespaces.sh
```

**Windows PowerShell:**
```powershell
.\setup-namespaces.ps1
```

### 2. Update Configuration

The `config.yaml` file has been updated with nginx-ingress compatible settings:

```yaml
git_username: user
git_credential: env
registry_password: env
registry_namespace: registry
challenge_namespace: challenges
tcp_domain_name: ctf.psuccso.org
https_domain_name: https://ctf.psuccso.org/
external_tcp_port: 80
external_https_port: 443
expire_interval: 3600
ctfd_url: https://ctf.psuccso.org/
```

### 3. Set Environment Variables

In your CTFd deployment, set these environment variables:

```yaml
env:
- name: GIT_USERNAME
  value: "your-git-username"
- name: GIT_CREDENTIAL
  value: "your-git-password-or-token"
- name: REGISTRY_PASSWORD
  value: "your-registry-password"
```

### 4. Update Registry Secret

Update the registry secret with your actual password:

```bash
kubectl create secret docker-registry registry-auth \
  --docker-server=chal-registry.ctf.psuccso.org \
  --docker-username=ctfd \
  --docker-password=YOUR_ACTUAL_PASSWORD \
  --namespace=challenges \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 5. Restart CTFd

Restart your CTFd deployment to apply the plugin changes:

```bash
kubectl rollout restart deployment/ctfd -n ctfd
```

## How It Works Now

### Web Challenges
- Use standard nginx-ingress Ingress resources
- Automatically get SSL certificates (if configured)
- Accessible via `challenge-name.ctf.psuccso.org`

### TCP Challenges
- Use nginx-ingress with TCP backend protocol
- SSL passthrough enabled for secure connections
- Accessible via `challenge-name.ctf.psuccso.org`

### Random Port Challenges
- Use NodePort services
- Ports are automatically assigned by Kubernetes

## DNS Configuration

Ensure your DNS is configured to point `*.ctf.psuccso.org` to your nginx-ingress controller's external IP.

## Troubleshooting

### Check Namespaces
```bash
kubectl get namespaces | grep -E "(registry|challenges)"
```

### Check Registry
```bash
kubectl get pods -n registry
kubectl get svc -n registry
```

### Check Challenges
```bash
kubectl get pods -n challenges
kubectl get ingress -n challenges
```

### View Logs
```bash
kubectl logs -n ctfd deployment/ctfd
```

## Benefits of nginx-ingress

1. **Simpler configuration**: No need for complex Istio Gateway/VirtualService setup
2. **Better compatibility**: Works with standard Kubernetes resources
3. **Easier troubleshooting**: Standard nginx-ingress debugging tools
4. **Automatic SSL**: Let's Encrypt integration (if configured)
5. **Performance**: Lightweight compared to Istio

## Notes

- The plugin will automatically create Ingress resources for each challenge
- SSL certificates are handled by nginx-ingress (no separate cert-manager needed)
- Port management is automatic (no manual port patching required)
- All challenges use the same domain pattern for consistency
