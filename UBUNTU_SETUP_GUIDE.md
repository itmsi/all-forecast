# 🚀 Panduan Setup di Server Internal Ubuntu

Dokumentasi lengkap untuk instalasi dan konfigurasi Sistem Forecast di server internal Ubuntu.

---

## 📋 Daftar Isi

1. [Persiapan Server](#1-persiapan-server)
2. [Instalasi Dependencies](#2-instalasi-dependencies)
3. [Setup Aplikasi](#3-setup-aplikasi)
4. [Konfigurasi](#4-konfigurasi)
5. [Menjalankan Aplikasi](#5-menjalankan-aplikasi)
6. [Verifikasi](#6-verifikasi)
7. [Konfigurasi Lanjutan](#7-konfigurasi-lanjutan)
8. [Maintenance](#8-maintenance)
9. [Troubleshooting](#9-troubleshooting)

---

## 🔌 Port Configuration

Aplikasi ini menggunakan port berikut:
- **PostgreSQL Database**: 9573
- **Redis**: 9574
- **Backend API**: 9571
- **Frontend UI**: 9572

---

## 1. Persiapan Server

### 1.1 Spesifikasi Server

**Minimum Requirements:**
- OS: Ubuntu 20.04 LTS atau lebih baru (22.04 LTS recommended)
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB (SSD recommended)
- Network: Akses ke internal network

**Recommended untuk Production:**
- OS: Ubuntu 22.04 LTS
- CPU: 8 cores
- RAM: 16 GB
- Storage: 100 GB SSD
- Network: Gigabit Ethernet

### 1.2 Akses Server

```bash
# Login ke server via SSH
ssh username@server-ip-address

# Update sistem operasi
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y

# Restart jika ada kernel update
sudo reboot
```

### 1.3 Setup User dan Permissions

```bash
# Buat user khusus untuk aplikasi (optional tapi recommended)
sudo adduser forecast
sudo usermod -aG sudo forecast

# Login sebagai user baru
su - forecast

# Atau login ulang via SSH
ssh forecast@server-ip-address
```

---

## 2. Instalasi Dependencies

### 2.1 Install Docker

```bash
# Remove old versions jika ada
sudo apt remove docker docker-engine docker.io containerd runc

# Install prerequisites
sudo apt update
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Setup repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
```

**Expected output:**
```
Docker version 24.0.x, build xxxxx
```

### 2.2 Configure Docker Permissions

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Test docker without sudo
docker run hello-world
```

**Expected output:**
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

### 2.3 Install Docker Compose

```bash
# Docker Compose plugin biasanya sudah terinstall dengan Docker
docker compose version

# Jika belum ada, install manual:
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 2.4 Install Git

```bash
# Install Git
sudo apt install -y git

# Configure Git (optional)
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"

# Verify
git --version
```

### 2.5 Install Additional Tools

```bash
# Install useful utilities
sudo apt install -y \
    htop \
    ncdu \
    vim \
    nano \
    curl \
    wget \
    net-tools \
    ufw

# Verify
htop --version
```

---

## 3. Setup Aplikasi

### 3.1 Pilih Lokasi Instalasi

```bash
# Option 1: Install di /opt (recommended untuk production)
cd /opt
sudo mkdir -p forecast
sudo chown -R $USER:$USER forecast
cd forecast

# Option 2: Install di home directory (untuk development/testing)
cd ~
mkdir -p apps
cd apps
```

Untuk panduan ini, kita gunakan `/opt/forecast`:

```bash
cd /opt
sudo mkdir -p forecast
sudo chown -R $USER:$USER forecast
cd forecast
```

### 3.2 Clone Repository

**Option A: Clone dari Git Repository**

```bash
# Jika repository sudah ada di Git server internal
git clone https://your-git-server.com/forecast.git .

# Atau dari GitHub
git clone https://github.com/your-org/forecast.git .
```

**Option B: Upload Manual dari Local Machine**

Dari komputer lokal Anda:

```bash
# Compress folder project
cd /path/to/forecast
tar -czf forecast.tar.gz .

# Upload ke server via SCP
scp forecast.tar.gz username@server-ip:/opt/forecast/

# Di server, extract
cd /opt/forecast
tar -xzf forecast.tar.gz
rm forecast.tar.gz
```

**Option C: Upload via SFTP**

Gunakan aplikasi seperti FileZilla atau WinSCP untuk upload folder project ke `/opt/forecast/`

### 3.3 Verify File Structure

```bash
cd /opt/forecast
ls -la

# Expected output:
# backend/
# frontend/
# real_data/
# docker-compose.yml
# README.md
# ... other files
```

---

## 4. Konfigurasi

### 4.1 Setup Environment Variables

```bash
cd /opt/forecast

# Buat file .env (copy dari template jika ada)
nano .env
```

Isi file `.env`:

```bash
# Database Configuration
DB_PASSWORD=GantiDenganPasswordKuat2024!@#$
POSTGRES_DB=forecast_db
POSTGRES_USER=forecast_user

# Redis Configuration
REDIS_PASSWORD=GantiDenganPasswordRedis2024!

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration (ganti dengan IP server Anda)
REACT_APP_API_URL=http://192.168.1.100:9571

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Application Settings
MAX_UPLOAD_SIZE=104857600
MAX_FORECAST_ITEMS=100000
```

**Penting:**
- Ganti `DB_PASSWORD` dengan password yang kuat (minimal 16 karakter)
- Ganti `REDIS_PASSWORD` dengan password yang berbeda
- Ganti `REACT_APP_API_URL` dengan IP address server Anda
- Simpan file ini dengan aman, jangan commit ke Git

### 4.2 Setup Folder Permissions

```bash
cd /opt/forecast

# Create necessary directories
mkdir -p backend/uploads
mkdir -p backend/outputs
mkdir -p backend/models
mkdir -p logs
mkdir -p backups

# Set permissions
chmod -R 755 backend/uploads
chmod -R 755 backend/outputs
chmod -R 755 backend/models
chmod -R 755 logs
chmod -R 755 backups

# Verify
ls -la backend/
```

### 4.3 Configure Docker Compose (Optional)

Jika perlu customize ports atau resources:

```bash
nano docker-compose.yml
```

**Ubah ports jika sudah terpakai:**

```yaml
# Frontend port (default 9572)
frontend:
  ports:
    - "8080:80"  # Ubah 9572 ke 8080

# Backend API port (default 9571)
backend:
  ports:
    - "8000:8000"  # Ubah 9571 ke 8000
```

**Ubah resources jika server limited:**

```yaml
# Kurangi Celery concurrency
celery_worker:
  command: celery -A app.celery_app worker --loglevel=info --concurrency=2  # Ubah dari 4 ke 2

# Kurangi backend workers
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1  # Ubah dari 2 ke 1
```

---

## 5. Menjalankan Aplikasi

### 5.1 Build Docker Images

```bash
cd /opt/forecast

# Build semua images (proses pertama kali 5-15 menit)
docker compose build

# Monitor progress
# Akan download base images dan install dependencies
```

**Catatan:**
- Pastikan koneksi internet stabil untuk download images
- Jika gagal, coba: `docker compose build --no-cache`

### 5.2 Start Services

```bash
# Start semua services dalam background
docker compose up -d

# Expected output:
# [+] Running 5/5
#  ✔ Container forecast_postgres        Started
#  ✔ Container forecast_redis           Started  
#  ✔ Container forecast_backend         Started
#  ✔ Container forecast_celery_worker   Started
#  ✔ Container forecast_frontend        Started
```

### 5.3 Monitor Startup

```bash
# Check container status
docker compose ps

# Monitor logs (tekan Ctrl+C untuk stop)
docker compose logs -f

# Check specific service
docker compose logs -f backend
docker compose logs -f celery_worker
```

**Tunggu sampai semua service healthy (30-60 detik)**

---

## 6. Verifikasi

### 6.1 Check Container Status

```bash
cd /opt/forecast
docker compose ps
```

**Expected output:**

```
NAME                       STATUS              PORTS
forecast_backend           Up 2 minutes        0.0.0.0:9571->8000/tcp
forecast_celery_worker     Up 2 minutes
forecast_frontend          Up 2 minutes        0.0.0.0:9572->80/tcp
forecast_postgres          Up 2 minutes        0.0.0.0:9573->5432/tcp
forecast_redis             Up 2 minutes        0.0.0.0:9574->6379/tcp
```

Semua status harus **Up**.

### 6.2 Test Backend API

```bash
# Test health endpoint
curl http://localhost:9571/api/health

# Expected response:
# {"status":"ok","database":"connected","redis":"connected","celery":"running"}

# Test API docs
curl http://localhost:9571/api/docs
```

### 6.3 Test Frontend

```bash
# Test dari server
curl http://localhost:9572

# Test dari browser
# Buka: http://server-ip:9572
```

**Jika tidak bisa akses dari komputer lain, cek firewall (lihat section 7.1)**

### 6.4 Test Database

```bash
# Connect ke PostgreSQL
docker exec -it forecast_postgres psql -U forecast_user -d forecast_db

# Jalankan query test
\dt

# Expected output: List of tables
# Should see: batch_jobs, forecast_jobs, etc.

# Exit
\q
```

### 6.5 Test Celery Worker

```bash
# Check Celery logs
docker compose logs celery_worker --tail 50

# Should see:
# [2024-10-15 10:00:00,000: INFO/MainProcess] Connected to redis://redis:6379/0
# [2024-10-15 10:00:00,000: INFO/MainProcess] celery@... ready.
```

### 6.6 Test Complete Workflow

**Test via Web Interface:**

1. Buka browser: `http://server-ip:9572`
2. Upload file sample data (gunakan `sample_data.csv`)
3. Klik "Run Forecast"
4. Monitor status sampai "COMPLETED"
5. Download hasil forecast

**Test via API:**

```bash
# Test single forecast
curl -X POST http://localhost:9571/api/forecast/single \
  -H "Content-Type: multipart/form-data" \
  -F "file=@real_data/example.csv"

# Check response untuk job_id
# Kemudian check status:
curl http://localhost:9571/api/forecast/status/{job_id}
```

---

## 7. Konfigurasi Lanjutan

### 7.1 Setup Firewall (UFW)

```bash
# Install UFW jika belum ada
sudo apt install -y ufw

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (PENTING! Jangan lupa ini)
sudo ufw allow 22/tcp

# Allow Frontend (port 9572)
sudo ufw allow 9572/tcp comment 'Forecast Frontend'

# Allow Backend API (port 9571)
sudo ufw allow 9571/tcp comment 'Forecast API'

# Optional: Allow PostgreSQL (port 9573) - hanya jika perlu akses eksternal
# sudo ufw allow 9573/tcp comment 'Forecast PostgreSQL'

# Optional: Allow Redis (port 9574) - hanya jika perlu akses eksternal
# sudo ufw allow 9574/tcp comment 'Forecast Redis'

# Allow dari specific IP atau subnet (recommended)
# Contoh: hanya allow dari internal network 192.168.1.0/24
sudo ufw allow from 192.168.1.0/24 to any port 9572 comment 'Frontend Internal'
sudo ufw allow from 192.168.1.0/24 to any port 9571 comment 'API Internal'

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

**Expected output:**

```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
9572/tcp                   ALLOW       192.168.1.0/24
9571/tcp                   ALLOW       192.168.1.0/24
```

### 7.2 Setup Auto-Start on Boot

```bash
# Enable Docker service
sudo systemctl enable docker
sudo systemctl enable containerd

# Verify
sudo systemctl is-enabled docker

# Docker Compose sudah auto-restart containers
# Check docker-compose.yml untuk setting restart: unless-stopped
```

### 7.3 Setup Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/forecast
```

Isi file:

```
/opt/forecast/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 forecast forecast
    sharedscripts
    postrotate
        docker compose -f /opt/forecast/docker-compose.yml restart backend celery_worker > /dev/null 2>&1 || true
    endscript
}
```

Test logrotate:

```bash
sudo logrotate -d /etc/logrotate.d/forecast
sudo logrotate -f /etc/logrotate.d/forecast
```

### 7.4 Setup Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/forecast-backup.sh
```

Isi script:

```bash
#!/bin/bash
# Forecast System Backup Script

# Configuration
BACKUP_DIR="/opt/forecast/backups"
COMPOSE_FILE="/opt/forecast/docker-compose.yml"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup Database
echo "[$(date)] Starting database backup..."
docker exec forecast_postgres pg_dump -U forecast_user forecast_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

if [ $? -eq 0 ]; then
    echo "[$(date)] Database backup completed: db_$DATE.sql.gz"
else
    echo "[$(date)] ERROR: Database backup failed!"
    exit 1
fi

# Backup Files (uploads, outputs, models)
echo "[$(date)] Starting files backup..."
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" \
    -C /opt/forecast/backend \
    uploads \
    outputs \
    models \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "[$(date)] Files backup completed: files_$DATE.tar.gz"
else
    echo "[$(date)] WARNING: Files backup completed with warnings"
fi

# Backup configuration
cp /opt/forecast/.env "$BACKUP_DIR/env_$DATE.backup"
cp /opt/forecast/docker-compose.yml "$BACKUP_DIR/docker-compose_$DATE.yml"

# Cleanup old backups (keep last N days)
echo "[$(date)] Cleaning up old backups..."
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "files_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "env_*.backup" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "docker-compose_*.yml" -mtime +$RETENTION_DAYS -delete

# Show disk usage
echo "[$(date)] Backup directory size: $(du -sh $BACKUP_DIR | cut -f1)"

echo "[$(date)] Backup completed successfully!"
```

Make executable:

```bash
sudo chmod +x /usr/local/bin/forecast-backup.sh

# Test run
sudo /usr/local/bin/forecast-backup.sh
```

Setup Cron Job:

```bash
# Edit crontab
crontab -e

# Add line (backup setiap hari jam 2 pagi)
0 2 * * * /usr/local/bin/forecast-backup.sh >> /opt/forecast/logs/backup.log 2>&1
```

### 7.5 Setup Monitoring Script

```bash
# Create monitoring script
nano /usr/local/bin/forecast-monitor.sh
```

Isi script:

```bash
#!/bin/bash
# Forecast System Monitoring Script

cd /opt/forecast

echo "==================================="
echo "Forecast System Status"
echo "Date: $(date)"
echo "==================================="

# Container status
echo -e "\n[Container Status]"
docker compose ps

# Resource usage
echo -e "\n[Resource Usage]"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Disk usage
echo -e "\n[Disk Usage]"
df -h /opt/forecast
du -sh /opt/forecast/backend/uploads
du -sh /opt/forecast/backend/outputs

# Database size
echo -e "\n[Database Size]"
docker exec forecast_postgres psql -U forecast_user forecast_db -c "SELECT pg_size_pretty(pg_database_size('forecast_db'));"

# Check recent errors in logs
echo -e "\n[Recent Errors (last 10)]"
docker compose logs --tail 50 | grep -i error | tail -10

echo -e "\n==================================="
```

Make executable dan test:

```bash
chmod +x /usr/local/bin/forecast-monitor.sh
/usr/local/bin/forecast-monitor.sh
```

### 7.6 Setup System Resource Limits

```bash
# Edit Docker daemon config
sudo nano /etc/docker/daemon.json
```

Isi:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
```

Restart Docker:

```bash
sudo systemctl restart docker
docker compose -f /opt/forecast/docker-compose.yml up -d
```

---

## 8. Maintenance

### 8.1 Update Aplikasi

```bash
cd /opt/forecast

# Stop services
docker compose down

# Backup sebelum update
/usr/local/bin/forecast-backup.sh

# Pull latest changes (jika dari Git)
git pull origin main

# Rebuild images
docker compose build --no-cache

# Start services
docker compose up -d

# Check logs
docker compose logs -f
```

### 8.2 Restart Services

```bash
cd /opt/forecast

# Restart semua
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart celery_worker
docker compose restart frontend

# Full restart (stop + start)
docker compose down
docker compose up -d
```

### 8.3 View Logs

```bash
cd /opt/forecast

# All services (real-time)
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery_worker

# Last 100 lines
docker compose logs --tail 100 backend

# Save logs to file
docker compose logs backend > backend.log

# Search for errors
docker compose logs backend | grep -i error
```

### 8.4 Clean Up Disk Space

```bash
# Check disk usage
df -h
docker system df

# Remove unused images
docker image prune -a

# Remove unused volumes (HATI-HATI!)
docker volume prune

# Remove old outputs (older than 30 days)
find /opt/forecast/backend/outputs -type f -mtime +30 -delete

# Remove old uploads (older than 30 days)
find /opt/forecast/backend/uploads -type f -mtime +30 -delete
```

### 8.5 Database Maintenance

```bash
# Connect to database
docker exec -it forecast_postgres psql -U forecast_user forecast_db

# Vacuum (clean up)
VACUUM ANALYZE;

# Check table sizes
SELECT 
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

# Check old jobs (older than 90 days)
SELECT COUNT(*) FROM forecast_jobs WHERE created_at < NOW() - INTERVAL '90 days';

# Delete old jobs (optional)
DELETE FROM forecast_jobs WHERE created_at < NOW() - INTERVAL '90 days' AND status IN ('COMPLETED', 'FAILED');

# Exit
\q
```

### 8.6 Backup and Restore

**Manual Backup:**

```bash
cd /opt/forecast

# Backup database
docker exec forecast_postgres pg_dump -U forecast_user forecast_db | gzip > backups/manual_db_$(date +%Y%m%d).sql.gz

# Backup files
tar -czf backups/manual_files_$(date +%Y%m%d).tar.gz backend/uploads backend/outputs backend/models
```

**Restore from Backup:**

```bash
cd /opt/forecast

# Stop services
docker compose down

# Restore database
gunzip -c backups/manual_db_20241015.sql.gz | docker exec -i forecast_postgres psql -U forecast_user forecast_db

# Restore files
tar -xzf backups/manual_files_20241015.tar.gz -C backend/

# Start services
docker compose up -d
```

---

## 9. Troubleshooting

### 9.1 Services Tidak Bisa Start

**Problem: Port sudah digunakan**

```bash
# Check port usage
sudo netstat -tulpn | grep :9572
sudo netstat -tulpn | grep :9571
sudo netstat -tulpn | grep :9573
sudo netstat -tulpn | grep :9574

# Kill process yang menggunakan port
sudo kill -9 <PID>

# Atau ubah port di docker-compose.yml
```

**Problem: Permission denied**

```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/forecast
chmod -R 755 /opt/forecast/backend
```

**Problem: Out of disk space**

```bash
# Check disk space
df -h

# Clean Docker
docker system prune -a
docker volume prune

# Clean old files
rm -rf /opt/forecast/backend/outputs/*
rm -rf /opt/forecast/backend/uploads/*
```

### 9.2 Database Connection Error

**Problem: Connection refused**

```bash
# Check PostgreSQL logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres

# Wait 30 seconds then check
docker compose ps
```

**Problem: Wrong password**

```bash
# Check .env file
cat .env | grep DB_PASSWORD

# Recreate database dengan password baru
docker compose down -v
docker compose up -d
```

### 9.3 Frontend Tidak Bisa Akses Backend

**Problem: API URL salah**

```bash
# Check environment di container
docker exec forecast_frontend cat /etc/nginx/conf.d/default.conf

# Rebuild frontend dengan correct API URL
nano .env
# Update REACT_APP_API_URL
docker compose build frontend
docker compose up -d frontend
```

**Problem: CORS error**

Backend sudah configure CORS, tapi jika masih error:

```bash
# Check backend logs
docker compose logs backend | grep -i cors

# Restart backend
docker compose restart backend
```

### 9.4 Celery Jobs Stuck

**Problem: Jobs stuck di PROCESSING**

```bash
# Check Celery logs
docker compose logs celery_worker --tail 100

# Restart Celery
docker compose restart celery_worker

# Check Redis
docker exec -it forecast_redis redis-cli
KEYS celery*
```

**Problem: Jobs not starting**

```bash
# Check Redis connection
docker exec -it forecast_redis redis-cli ping

# Restart Redis dan Celery
docker compose restart redis
docker compose restart celery_worker

# Clear Redis cache (HATI-HATI!)
docker exec -it forecast_redis redis-cli FLUSHALL
```

### 9.5 High CPU/Memory Usage

```bash
# Check resource usage
docker stats

# If Celery using too much:
nano docker-compose.yml
# Ubah --concurrency=4 menjadi --concurrency=2
docker compose up -d celery_worker

# If backend using too much:
nano docker-compose.yml
# Ubah --workers 2 menjadi --workers 1
docker compose up -d backend

# Limit container resources
nano docker-compose.yml
# Tambahkan di service:
#   deploy:
#     resources:
#       limits:
#         cpus: '2'
#         memory: 2G
```

### 9.6 Docker Build Fails

**Problem: Cannot download packages**

```bash
# Check internet connection
ping google.com

# Try build with verbose
docker compose build --no-cache --progress=plain

# If behind proxy, configure Docker proxy
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo nano /etc/systemd/system/docker.service.d/http-proxy.conf

# Add:
# [Service]
# Environment="HTTP_PROXY=http://proxy.example.com:8080"
# Environment="HTTPS_PROXY=http://proxy.example.com:8080"

sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 9.7 Container Restart Loop

```bash
# Check which container restarting
docker compose ps

# Check logs for error
docker compose logs <container_name>

# Common fixes:
# 1. Database not ready - wait longer
# 2. Wrong environment variables - check .env
# 3. Port conflict - change port
# 4. Out of memory - increase server RAM or limit container resources
```

---

## 📊 Monitoring Commands Cheat Sheet

```bash
# Container status
docker compose ps

# Real-time logs
docker compose logs -f

# Resource usage
docker stats

# Disk space
df -h
du -sh /opt/forecast/backend/*

# Database size
docker exec forecast_postgres psql -U forecast_user forecast_db -c "SELECT pg_size_pretty(pg_database_size('forecast_db'));"

# Redis info
docker exec forecast_redis redis-cli INFO

# Check active jobs
docker exec forecast_postgres psql -U forecast_user forecast_db -c "SELECT status, COUNT(*) FROM forecast_jobs GROUP BY status;"

# Network connections
docker network inspect forecast_forecast_network

# Full system status
/usr/local/bin/forecast-monitor.sh
```

---

## 🔐 Security Checklist

- [ ] Password database diganti dari default
- [ ] Password Redis diganti dari default
- [ ] Firewall (UFW) dikonfigurasi
- [ ] Hanya allow akses dari internal network
- [ ] SSH key-based authentication enabled
- [ ] Regular backups configured
- [ ] Log rotation configured
- [ ] File permissions correct (755/644)
- [ ] .env file tidak di-commit ke Git
- [ ] Docker daemon secure
- [ ] Update OS dan packages regular

---

## ✅ Post-Installation Checklist

- [ ] Server requirements terpenuhi
- [ ] Docker dan Docker Compose installed
- [ ] Repository di-clone atau upload
- [ ] File .env configured
- [ ] Images berhasil di-build
- [ ] Semua 5 containers running
- [ ] Health check passed
- [ ] Frontend accessible dari browser
- [ ] Backend API accessible
- [ ] Test forecast job completed
- [ ] Backup script installed dan tested
- [ ] Monitoring script installed
- [ ] Firewall configured
- [ ] Auto-start on boot enabled
- [ ] Team mendapat akses
- [ ] Dokumentasi dibagikan ke team

---

## 📞 Support Information

**Jika mengalami masalah, kumpulkan informasi berikut:**

```bash
# System info
uname -a > system_info.txt
docker --version >> system_info.txt
docker compose version >> system_info.txt

# Container status
docker compose ps > container_status.txt

# Resource usage
docker stats --no-stream > resource_usage.txt

# Disk space
df -h > disk_space.txt

# Recent logs
docker compose logs --tail 100 backend > backend_logs.txt
docker compose logs --tail 100 celery_worker > celery_logs.txt

# Environment (tanpa password!)
cat .env | grep -v PASSWORD > env_config.txt
```

Kirimkan file-file ini ke tim support.

---

## 🎉 Selamat!

Jika semua checklist sudah completed, sistem Forecast siap digunakan!

**Akses Aplikasi:**
- Frontend: `http://server-ip:9572`
- Backend API: `http://server-ip:9571`
- API Documentation: `http://server-ip:9571/docs`

**Default Files Location:**
- Application: `/opt/forecast/`
- Uploads: `/opt/forecast/backend/uploads/`
- Outputs: `/opt/forecast/backend/outputs/`
- Models: `/opt/forecast/backend/models/`
- Backups: `/opt/forecast/backups/`
- Logs: `/opt/forecast/logs/`

**Useful Commands:**
```bash
# Quick status check
cd /opt/forecast && docker compose ps

# Quick restart
cd /opt/forecast && docker compose restart

# View logs
cd /opt/forecast && docker compose logs -f

# Backup now
/usr/local/bin/forecast-backup.sh

# Monitor system
/usr/local/bin/forecast-monitor.sh
```

---

**Dokumentasi dibuat:** Oktober 2024
**Versi:** 1.0
**Platform:** Ubuntu 20.04/22.04 LTS


