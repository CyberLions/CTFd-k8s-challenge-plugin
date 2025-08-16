# CTFd Kubernetes Challenge Plugin - Final Setup Guide

## Your Configuration

✅ **Git Credentials**: Will be entered manually through CTFd web interface  
✅ **Registry**: `registry.psuccso.org` with  
✅ **Storage**: `longhorn` storage class  
✅ **Wildcard DNS**: `*.ctf.psuccso.org` already configured  
✅ **nginx-ingress**: Using `nginx` ingress class  
✅ **Namespace**: `ctfd-challenges`  

## Setup Steps

### 1. Run the Setup Script

**Linux/Mac:**
```bash
chmod +x setup-namespaces.sh
./setup-namespaces.sh
```

**Windows PowerShell:**
```powershell
.\setup-namespaces.ps1
```

This will:
- Create the `ctfd-challenges` namespace
- Create the registry authentication secret

### 2. Verify Setup

Check that everything was created:
```bash
# Check namespace
kubectl get namespace ctfd-challenges

# Check secrets
kubectl get secrets -n ctfd-challenges

# Check registry secret
kubectl describe secret registry-auth -n ctfd-challenges
```

### 3. Restart CTFd

Restart your CTFd deployment to apply the plugin changes:
```bash
kubectl rollout restart deployment/ctfd -n ctfd
```

### 4. Configure Git Credentials

After CTFd restarts:
1. Go to CTFd admin panel
2. Navigate to `/admin/kubernetes`
3. Update the Git credentials in the web interface:
   - **Git Username**: `23younesm`
4. Click Submit to save

### 5. Monitor Deployment

Watch the CTFd deployment and check for any errors:
```bash
# Watch the rollout
kubectl rollout status deployment/ctfd -n ctfd

# Check CTFd logs
kubectl logs -n ctfd deployment/ctfd -f

# Check if the plugin loaded
kubectl logs -n ctfd deployment/ctfd | grep "ctfd-k8s-challenge"
```

## How It Works

### Challenge Creation
1. **Git Access**: Plugin uses Git credentials from CTFd configuration
2. **Image Building**: Kaniko builds images and pushes to `registry.psuccso.org`
3. **Deployment**: Challenges are deployed to `ctfd-challenges` namespace
4. **Ingress**: nginx-ingress creates routes like `challenge-name.ctf.psuccso.org`

### Challenge Types
- **Web Challenges**: Accessible via `https://challenge-name.ctf.psuccso.org`
- **TCP Challenges**: Accessible via `challenge-name.ctf.psuccso.org:80`
- **Random Port**: Uses NodePort services with automatic port assignment

## Security Features

✅ **Git Credentials**: Stored in CTFd database (encrypted)  
✅ **Registry Credentials**: Stored as Kubernetes secrets  
✅ **Web Interface**: Secure configuration through CTFd admin panel  
✅ **Namespace Isolation**: Challenges run in separate namespace  

## Testing

### 1. Create a Test Challenge
1. Go to CTFd admin panel
2. Navigate to `/admin/kubernetes`
3. Verify your Git credentials are set correctly
4. Create a simple challenge to test

### 2. Check Resources
```bash
# Check challenges namespace
kubectl get all -n ctfd-challenges

# Check ingress resources
kubectl get ingress -n ctfd-challenges

# Check pods
kubectl get pods -n ctfd-challenges
```

## Troubleshooting

### Common Issues

**1. Git Credentials Not Working**
- Go to `/admin/kubernetes` in CTFd
- Verify Git username and credential are set correctly
- Check if the GitHub token is still valid
- Ensure the token has access to the repositories

**2. Registry Authentication Failed**
```bash
# Check the secret
kubectl get secret registry-auth -n ctfd-challenges -o yaml

# Verify credentials
kubectl describe secret registry-auth -n ctfd-challenges
```

**3. Git Access Issues**
- Verify your GitHub token has the correct permissions
- Check if the token is expired
- Ensure the token can access the repositories you want to use
- Verify credentials are saved in CTFd admin panel

**4. Ingress Not Working**
```bash
# Check nginx-ingress controller
kubectl get pods -A | grep nginx-ingress

# Check ingress status
kubectl describe ingress -n ctfd-challenges
```

**5. Storage Issues**
```bash
# Check longhorn storage
kubectl get pvc -n ctfd-challenges
kubectl get pv
```

## Configuration Files

### config.yaml
```yaml
git_username: 23younesm
registry_namespace: ctfd-challenges
challenge_namespace: ctfd-challenges
tcp_domain_name: ctf.psuccso.org
https_domain_name: https://ctf.psuccso.org/
external_tcp_port: 80
external_https_port: 443
expire_interval: 3600
ctfd_url: https://ctf.psuccso.org/
```

### CTFd Admin Panel
- **Git Username**: Set to `23younesm`

## Next Steps

1. **Test with a simple challenge** to ensure everything works
2. **Monitor resource usage** in the `ctfd-challenges` namespace
3. **Set up monitoring** for the challenge instances
4. **Configure backup** for challenge data if needed

## Support

If you encounter issues:
1. Check the CTFd logs for error messages
2. Verify all secrets and namespaces exist
3. Ensure nginx-ingress controller is working
4. Check that DNS resolves correctly
5. Verify Git credentials are set in CTFd admin panel

Your setup is now configured to use:
- **Manual Git credentials** through CTFd web interface
- External registry: `registry.psuccso.org`
- nginx-ingress for routing
- Longhorn for storage
- Simple configuration approach
