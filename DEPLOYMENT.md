# Deployment Guide - AWS Lightsail

## Prerequisites
- AWS account
- Your Airtable credentials (token and base ID)

## Option 1: Single Instance (Recommended - Simplest)

### Step 1: Create Lightsail Instance

1. Go to [AWS Lightsail Console](https://lightsail.aws.amazon.com/)
2. Click "Create instance"
3. Select:
   - **Platform**: Linux/Unix
   - **Blueprint**: OS Only → Ubuntu 22.04 LTS
   - **Plan**: $3.50/month (512 MB RAM, 1 vCPU) or $5/month (1 GB RAM)
   - **Instance name**: ml-rpa-poc
4. Click "Create instance"

### Step 2: Configure Instance

1. Wait for instance to start (1-2 minutes)
2. Click on instance name → "Connect using SSH"
3. Run setup commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv nginx -y

# Install Git
sudo apt install git -y

# Clone your repository (or upload files)
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/ml-rpa-poc.git
cd ml-rpa-poc

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
```

4. Add to `.env`:
```
AIRTABLE_TOKEN=your_token_here
AIRTABLE_BASE_ID=your_base_id_here
```
Press `Ctrl+X`, then `Y`, then `Enter` to save.

### Step 3: Setup Backend Service

Create systemd service:

```bash
sudo nano /etc/systemd/system/ml-rpa.service
```

Add this content:

```ini
[Unit]
Description=ML RPA FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ml-rpa-poc/backend
Environment="PATH=/home/ubuntu/ml-rpa-poc/venv/bin"
EnvironmentFile=/home/ubuntu/ml-rpa-poc/.env
ExecStart=/home/ubuntu/ml-rpa-poc/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

Save and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ml-rpa
sudo systemctl start ml-rpa
sudo systemctl status ml-rpa
```

### Step 4: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/ml-rpa
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /home/ubuntu/ml-rpa-poc/frontend;
        index index.html;
        try_files $uri $uri/ /pages/index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/ml-rpa /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: Update Frontend API URL

```bash
nano /home/ubuntu/ml-rpa-poc/frontend/js/api.js
```

Change API_URL to:
```javascript
const API_URL = '/api';
```

### Step 6: Configure Firewall

In Lightsail console:
1. Go to your instance → "Networking" tab
2. Under "IPv4 Firewall", ensure these rules exist:
   - HTTP (TCP 80)
   - SSH (TCP 22)

### Step 7: Access Your App

Get your instance's public IP from Lightsail console:
- **Frontend**: http://YOUR_IP/pages/index.html
- **API Docs**: http://YOUR_IP/docs

## Option 2: Static IP + Domain (Optional)

### Attach Static IP

1. In Lightsail console → "Networking" tab
2. Click "Create static IP"
3. Attach to your instance
4. Note the static IP address

### Add Custom Domain

1. In Lightsail → "Networking" → "DNS zones"
2. Create DNS zone for your domain
3. Add A record pointing to your static IP
4. Update nameservers at your domain registrar

### Enable HTTPS (Free SSL)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

## Pricing

- **$3.50/month**: 512 MB RAM, 20 GB SSD, 1 TB transfer
- **$5/month**: 1 GB RAM, 40 GB SSD, 2 TB transfer
- **Static IP**: Free when attached to running instance
- **First 3 months**: Often free with AWS Free Tier

## Maintenance Commands

```bash
# View backend logs
sudo journalctl -u ml-rpa -f

# Restart backend
sudo systemctl restart ml-rpa

# Restart nginx
sudo systemctl restart nginx

# Update code
cd /home/ubuntu/ml-rpa-poc
git pull
sudo systemctl restart ml-rpa

# Check disk space
df -h

# Check memory
free -h
```

## Backup & Snapshots

1. In Lightsail console → Your instance
2. Click "Snapshots" tab
3. Click "Create snapshot"
4. Snapshots cost $0.05/GB/month

## Troubleshooting

**Backend not running:**
```bash
sudo systemctl status ml-rpa
sudo journalctl -u ml-rpa -n 50
```

**Nginx errors:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

**Port already in use:**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
sudo systemctl restart ml-rpa
```

**Permission issues:**
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/ml-rpa-poc
```

## Scaling Options

If you need more resources:
1. Create snapshot of current instance
2. Create new larger instance from snapshot
3. Update DNS to point to new instance
4. Delete old instance

## Alternative: Container Deployment

For easier updates, use Lightsail Container Service:
- $7/month for nano (512 MB RAM)
- Automatic deployments from Docker images
- Built-in load balancing
- See AWS Lightsail Containers documentation
