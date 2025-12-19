# DigitalOcean Deployment Guide

This guide walks you through deploying the Plant Disease Detection API on DigitalOcean.

## Prerequisites

- DigitalOcean account
- Git repository with your code
- Model file (`models/best_model.keras`) in your repository
- Docker installed locally (for testing)

## Method 1: DigitalOcean App Platform (Recommended)

### Step 1: Prepare Your Repository

Ensure your repository has:
- [x] Dockerfile
- [x] .dockerignore
- [x] requirements.txt
- [x] models/best_model.keras
- [x] app/ directory with Python code
- [x] static/ directory with frontend

### Step 2: Create a New App

1. Log in to [DigitalOcean](https://cloud.digitalocean.com/)
2. Navigate to **Apps** in the left sidebar
3. Click **Create App**
4. Choose your source (GitHub, GitLab, or Docker Hub)
5. Select your repository and branch (e.g., `main`)

### Step 3: Configure Build Settings

1. **Source**: Your repository
2. **Branch**: main
3. **Type**: Docker
4. **Dockerfile Path**: `Dockerfile`
5. **HTTP Port**: 8080
6. **Health Check Path**: `/health`

### Step 4: Set Environment Variables (Optional)

If your model is in a different location:
- Key: `MODEL_PATH`
- Value: `path/to/your/model.keras`

### Step 5: Configure Resources

**Basic Plan (Recommended minimum)**:
- **Memory**: 1 GB
- **CPU**: 1 vCPU
- Estimated cost: $12/month

**Production Plan (Recommended)**:
- **Memory**: 2 GB
- **CPU**: 2 vCPU
- Estimated cost: $24/month

### Step 6: Deploy

1. Review your settings
2. Click **Create Resources**
3. Wait for the build to complete (5-10 minutes)
4. Once deployed, you'll receive a URL like: `https://your-app-name.ondigitalocean.app`

### Step 7: Test Your Deployment

```bash
# Test health endpoint
curl https://your-app-name.ondigitalocean.app/health

# Test prediction
curl -X POST https://your-app-name.ondigitalocean.app/predict \
  -F "file=@/path/to/test_image.jpg" \
  -F "gradcam=true"
```

## Method 2: DigitalOcean Droplet with Docker

### Step 1: Create a Droplet

1. Go to **Create** → **Droplets**
2. Choose an image: **Ubuntu 22.04 LTS**
3. Choose a plan:
   - **Basic**: $12/month (2GB RAM, 1 vCPU)
   - **Regular**: $24/month (4GB RAM, 2 vCPU) - Recommended
4. Choose a datacenter region (closest to your users)
5. Add SSH key for authentication
6. Create Droplet

### Step 2: Connect to Your Droplet

```bash
ssh root@your_droplet_ip
```

### Step 3: Install Docker

```bash
# Update package list
apt update

# Install Docker
apt install -y docker.io docker-compose

# Start Docker
systemctl start docker
systemctl enable docker
```

### Step 4: Clone Your Repository

```bash
# Install git if needed
apt install -y git

# Clone your repository
git clone https://github.com/yourusername/lead_api_2.git
cd lead_api_2
```

### Step 5: Build and Run

```bash
# Build the Docker image
docker build -t plant-disease-api .

# Run the container
docker run -d -p 8080:8080 --name plant-disease-api plant-disease-api

# Or use docker-compose
docker-compose up -d
```

### Step 6: Set Up Firewall

```bash
# Allow SSH
ufw allow 22

# Allow HTTP/HTTPS
ufw allow 80
ufw allow 443

# Allow your app port
ufw allow 8080

# Enable firewall
ufw enable
```

### Step 7: Set Up Reverse Proxy (Optional but Recommended)

Install Nginx as a reverse proxy:

```bash
# Install Nginx
apt install -y nginx

# Create Nginx config
cat > /etc/nginx/sites-available/plant-disease-api <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        client_max_body_size 10M;
    }
}
EOF

# Enable the site
ln -s /etc/nginx/sites-available/plant-disease-api /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Test and reload
nginx -t
systemctl reload nginx
```

### Step 8: Set Up SSL with Let's Encrypt (Recommended)

```bash
# Install certbot
apt install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

## Method 3: DigitalOcean Container Registry + Kubernetes

For production-scale deployments, consider using DigitalOcean's managed Kubernetes.

### Quick Setup

1. Create a Container Registry
2. Push your Docker image
3. Create a Kubernetes cluster
4. Deploy using kubectl

```bash
# Build and tag
docker build -t registry.digitalocean.com/your-registry/plant-disease-api:latest .

# Push to registry
docker push registry.digitalocean.com/your-registry/plant-disease-api:latest

# Deploy to Kubernetes
kubectl create deployment plant-disease-api \
  --image=registry.digitalocean.com/your-registry/plant-disease-api:latest

kubectl expose deployment plant-disease-api --type=LoadBalancer --port=80 --target-port=8080
```

## Monitoring and Maintenance

### Check Application Logs

**App Platform**:
- Go to your app in the DigitalOcean dashboard
- Click on **Runtime Logs**

**Droplet**:
```bash
# View logs
docker logs -f plant-disease-api

# Or with docker-compose
docker-compose logs -f
```

### Health Checks

Set up a monitoring service to ping your health endpoint:
```bash
curl https://your-app.com/health
```

Recommended tools:
- UptimeRobot
- Pingdom
- DigitalOcean's built-in monitoring

### Updating Your Application

**App Platform**:
1. Push changes to your Git repository
2. DigitalOcean will automatically rebuild and redeploy

**Droplet**:
```bash
# Pull latest changes
cd lead_api_2
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Scaling

**App Platform**:
- Go to your app settings
- Adjust the number of instances
- DigitalOcean handles load balancing automatically

**Kubernetes**:
```bash
# Scale to 3 replicas
kubectl scale deployment plant-disease-api --replicas=3
```

## Cost Estimation

### App Platform
- **Basic (1GB RAM)**: $12/month
- **Professional (2GB RAM)**: $24/month
- **Bandwidth**: 1TB included, then $0.01/GB

### Droplet
- **Basic (2GB RAM)**: $12/month
- **Regular (4GB RAM)**: $24/month
- **Bandwidth**: 2TB included, then $0.01/GB

### Additional Costs
- **Container Registry**: $20/month (500GB storage)
- **Load Balancer**: $12/month
- **Managed Database** (if needed): Starting at $15/month

## Troubleshooting

### Issue: Build Fails

**Solution**: Check your Dockerfile and ensure all files are present

```bash
# Test build locally
docker build -t test .
```

### Issue: Application Won't Start

**Solution**: Check logs for errors

```bash
docker logs plant-disease-api
```

Common issues:
- Missing model file
- Insufficient memory
- Port already in use

### Issue: Out of Memory

**Solution**: Upgrade your plan to at least 2GB RAM

TensorFlow and the model require significant memory.

### Issue: Slow Predictions

**Solution**:
1. Upgrade to 2 vCPU
2. Enable caching
3. Consider adding a GPU droplet for better performance

## Security Best Practices

1. **Use HTTPS**: Always use SSL/TLS in production
2. **Environment Variables**: Store sensitive data in environment variables
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Authentication**: Add API key authentication for production
5. **Regular Updates**: Keep dependencies updated
6. **Firewall**: Only expose necessary ports
7. **Backups**: Regular backups of your model and data

## n8n Integration on DigitalOcean

To integrate with n8n:

1. Deploy your API on DigitalOcean (Method 1 or 2)
2. Get your app URL
3. In n8n, add HTTP Request node:
   - Method: POST
   - URL: `https://your-app.ondigitalocean.app/predict`
   - Body: Form-Data
   - File field: `file`
   - Optional fields: `gradcam`, `gradcam_plus_plus`

## Support

For DigitalOcean-specific issues:
- [DigitalOcean Community](https://www.digitalocean.com/community)
- [DigitalOcean Documentation](https://docs.digitalocean.com/)

For application issues:
- Check application logs
- Review the README.md
- Create an issue in the repository
