# Deployment Guide - Forecast System

Panduan lengkap untuk deployment Forecast System ke server internal.

## 📋 Server Requirements

### Minimum Specifications

- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB (SSD recommended)
- **Network**: Internal network access

### Recommended Specifications (untuk 10+ users)

- **CPU**: 8 cores
- **RAM**: 16 GB
- **Storage**: 100 GB SSD
- **Network**: Gigabit Ethernet

## 🔧 Pre-Installation Setup

### 1. Install Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
```

### 2. Install Docker Compose

```bash
# Download latest version
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose --version
```

### 3. Install Git (jika belum ada)

```bash
sudo apt update
sudo apt install git -y
```

## 📥 Installation Steps

### Step 1: Clone Repository

```bash
# Pilih direktori untuk aplikasi
cd /opt  # atau /home/youruser/apps

# Clone repository
git clone <repository-url> forecast-system
cd forecast-system
```

### Step 2: Setup Environment Variables

```bash
# Copy template environment
cp .env.example .env

# Edit environment variables
nano .env
```

Edit `.env`:
```bash
# Ganti password default!
DB_PASSWORD=your_secure_password_here_min_16_chars

# Optional: Customize API URL untuk production
REACT_APP_API_URL=http://your-server-ip:8000
```

### Step 3: Build Docker Images

```bash
# Build semua images (akan memakan waktu 5-10 menit pertama kali)
docker-compose build

# Jika ada error, coba dengan:
docker-compose build --no-cache
```

### Step 4: Start Services

```bash
# Start semua services dalam background
docker-compose up -d

# Monitor logs
docker-compose logs -f

# Tunggu sampai semua service healthy (sekitar 30-60 detik)
docker-compose ps
```

Expected output:
```
NAME                    STATUS              PORTS
forecast_backend        Up 30 seconds       0.0.0.0:8000->8000/tcp
forecast_celery_worker  Up 30 seconds
forecast_frontend       Up 30 seconds       0.0.0.0:80->80/tcp
forecast_postgres       Up 30 seconds       0.0.0.0:5432->5432/tcp
forecast_redis          Up 30 seconds       0.0.0.0:6379->6379/tcp
```

### Step 5: Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"ok","timestamp":"...","database":"ok","celery":"ok","version":"1.0.0"}

# Test frontend
curl http://localhost/

# Test dari browser
# Buka http://server-ip atau http://localhost
```

## ✅ Post-Installation Configuration

### 1. Firewall Setup (Optional - untuk security)

```bash
# Ubuntu UFW
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp  # Jika API perlu diakses langsung
sudo ufw enable

# CentOS/RHEL firewalld
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 2. Setup Auto-Start on Boot

```bash
# Docker Compose akan auto-restart containers
# Tapi pastikan Docker service auto-start

sudo systemctl enable docker
sudo systemctl enable containerd
```

### 3. Setup Log Rotation

Create `/etc/logrotate.d/forecast-system`:

```bash
sudo nano /etc/logrotate.d/forecast-system
```

Content:
```
/opt/forecast-system/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
}
```

## 🔄 Maintenance Operations

### Update Application

```bash
cd /opt/forecast-system

# Pull latest changes
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose down
docker-compose up -d

# Verify
docker-compose ps
```

### Restart Services

```bash
# Restart semua
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart celery_worker
docker-compose restart frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Database Backup

```bash
# Create backup directory
mkdir -p backups

# Backup database
docker exec forecast_postgres pg_dump -U forecast_user forecast_db > backups/forecast_db_$(date +%Y%m%d_%H%M%S).sql

# Compress old backups
gzip backups/*.sql

# Auto backup script (optional)
sudo nano /usr/local/bin/forecast-backup.sh
```

Backup script:
```bash
#!/bin/bash
BACKUP_DIR="/opt/forecast-system/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker exec forecast_postgres pg_dump -U forecast_user forecast_db > "$BACKUP_DIR/db_$DATE.sql"

# Files backup
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" -C /opt/forecast-system/backend models uploads outputs

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and add to crontab:
```bash
sudo chmod +x /usr/local/bin/forecast-backup.sh

# Run daily at 2 AM
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/forecast-backup.sh >> /var/log/forecast-backup.log 2>&1
```

### Restore from Backup

```bash
# Stop services
docker-compose down

# Restore database
cat backups/forecast_db_20251014.sql | docker exec -i forecast_postgres psql -U forecast_user forecast_db

# Restore files
tar -xzf backups/files_20251014.tar.gz -C backend/

# Start services
docker-compose up -d
```

## 📊 Monitoring

### Check Resource Usage

```bash
# Overall
docker stats

# Disk usage
docker system df

# Check specific container
docker stats forecast_backend
```

### Monitor Database

```bash
# Connect to PostgreSQL
docker exec -it forecast_postgres psql -U forecast_user forecast_db

# Check connections
SELECT count(*) FROM pg_stat_activity;

# Check database size
SELECT pg_size_pretty(pg_database_size('forecast_db'));

# Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) 
FROM pg_catalog.pg_statio_user_tables 
ORDER BY pg_total_relation_size(relid) DESC;
```

### Monitor Redis

```bash
# Connect to Redis
docker exec -it forecast_redis redis-cli

# Check info
INFO

# Check memory
INFO memory

# Check keys
KEYS *

# Monitor real-time
MONITOR
```

## 🔐 Security Hardening

### 1. Change Default Passwords

```bash
# Edit .env dan ganti DB_PASSWORD
nano .env

# Restart services
docker-compose down
docker-compose up -d
```

### 2. Restrict Network Access

```bash
# Hanya allow dari internal network
sudo iptables -A INPUT -p tcp --dport 80 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j DROP

# Save rules
sudo netfilter-persistent save
```

### 3. Setup HTTPS (Optional - untuk production)

Install Nginx reverse proxy di host:

```bash
sudo apt install nginx certbot python3-certbot-nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/forecast
```

Nginx config:
```nginx
server {
    listen 443 ssl;
    server_name forecast.your-company.com;

    ssl_certificate /etc/letsencrypt/live/forecast.your-company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forecast.your-company.com/privkey.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Port already in use
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# 2. Permission denied
sudo chown -R $USER:$USER /opt/forecast-system

# 3. Out of disk space
df -h
docker system prune -a
```

### Database connection errors

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify password in .env
cat .env | grep DB_PASSWORD

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### High CPU/Memory usage

```bash
# Check which container
docker stats

# If Celery worker high:
# Reduce concurrency in docker-compose.yml
# --concurrency=2 instead of 4

# If backend high:
# Reduce workers in docker-compose.yml
# --workers 1 instead of 2
```

### Forecast jobs stuck in PROCESSING

```bash
# Check Celery worker logs
docker-compose logs celery_worker

# Restart Celery
docker-compose restart celery_worker

# If needed, clear Redis queue
docker exec -it forecast_redis redis-cli FLUSHALL
```

## 📞 Support Checklist

Jika ada masalah, kumpulkan informasi berikut:

```bash
# System info
uname -a
docker --version
docker-compose --version

# Container status
docker-compose ps

# Recent logs
docker-compose logs --tail=50 backend > backend.log
docker-compose logs --tail=50 celery_worker > celery.log

# Resource usage
docker stats --no-stream > stats.txt

# Disk space
df -h > disk.txt
```

## ✅ Deployment Checklist

- [ ] Server meets minimum requirements
- [ ] Docker & Docker Compose installed
- [ ] Repository cloned
- [ ] Environment variables configured
- [ ] Images built successfully
- [ ] All services running (docker-compose ps)
- [ ] Health check passes
- [ ] Frontend accessible
- [ ] Test forecast job completed
- [ ] Backup script configured
- [ ] Auto-start on boot enabled
- [ ] Firewall configured (if needed)
- [ ] Monitoring setup
- [ ] Documentation shared with team

## 🎉 Success!

Jika semua checklist terpenuhi, sistem siap digunakan!

Akses: http://your-server-ip

API Docs: http://your-server-ip:8000/api/docs

