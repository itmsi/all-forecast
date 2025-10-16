# 🚀 Step-by-Step Deploy ke Server Ubuntu

Panduan singkat deploy Forecast System ke server internal Ubuntu.

---

## 📋 Persiapan di Lokal (Sebelum Upload)

### 1. Pastikan File Lengkap
```bash
cd /path/to/forecast

# Cek struktur folder
ls -la

# Harus ada:
# - backend/
# - frontend/
# - docker-compose.yml
# - requirements.txt
# - dll
```

### 2. Compress Project (Opsional - untuk upload cepat)
```bash
# Compress tanpa node_modules dan __pycache__
tar -czf forecast.tar.gz \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='backend/uploads/*' \
  --exclude='backend/outputs/*' \
  .

# File siap di-upload: forecast.tar.gz
```

---

## 🖥️ Di Server Ubuntu

### STEP 1: Persiapan Server

```bash
# Login ke server
ssh user@server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (jika belum)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker
docker --version
docker compose version
```

---

### STEP 2: Upload Project ke Server

**Option A: Via SCP (dari komputer lokal)**
```bash
# Upload dari lokal ke server
scp forecast.tar.gz user@server-ip:/opt/

# Di server, extract
ssh user@server-ip
cd /opt
sudo mkdir -p forecast
sudo chown $USER:$USER forecast
tar -xzf forecast.tar.gz -C forecast/
cd forecast
```

**Option B: Via Git**
```bash
# Di server
cd /opt
sudo mkdir -p forecast
sudo chown $USER:$USER forecast
cd forecast

# Clone repository
git clone <your-git-url> .
```

**Option C: Via SFTP/FileZilla**
- Upload semua folder ke server: `/opt/forecast/`

---

### STEP 3: Setup Environment Variables

```bash
cd /opt/forecast

# Buat file .env
nano .env
```

**Isi file `.env`:**
```bash
# Database Configuration
DB_PASSWORD=GantiDenganPasswordKuat2024!@#$

# API Configuration
REACT_APP_API_URL=https://api-forecast.motorsights.com
```

**PENTING:**
- Ganti `DB_PASSWORD` dengan password yang kuat
- `REACT_APP_API_URL` pakai domain API production Anda

**Simpan file:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### STEP 4: Setup Folder Permissions

```bash
cd /opt/forecast

# Buat folder yang diperlukan
mkdir -p backend/uploads
mkdir -p backend/outputs
mkdir -p backend/models
mkdir -p logs
mkdir -p backups

# Set permissions
chmod -R 755 backend/
```

---

### STEP 5: Build Docker Images

```bash
cd /opt/forecast

# Build semua images (5-10 menit pertama kali)
docker compose build

# Tunggu sampai selesai
# Output akan menunjukkan: Built backend, frontend, celery_worker
```

**Jika ada error**, coba:
```bash
docker compose build --no-cache
```

---

### STEP 6: Start Services

```bash
cd /opt/forecast

# Start semua services
docker compose up -d

# Expected output:
# Creating forecast_postgres ... done
# Creating forecast_redis ... done
# Creating forecast_backend ... done
# Creating forecast_celery_worker ... done
# Creating forecast_frontend ... done
```

---

### STEP 7: Verifikasi Deployment

```bash
# Check container status (tunggu 30 detik)
docker compose ps

# Semua harus status "Up"
```

**Expected output:**
```
NAME                     STATUS              PORTS
forecast_backend         Up                  0.0.0.0:9571->8000/tcp
forecast_celery_worker   Up
forecast_frontend        Up                  0.0.0.0:9572->80/tcp
forecast_postgres        Up (healthy)        0.0.0.0:9573->5432/tcp
forecast_redis           Up (healthy)        0.0.0.0:9574->6379/tcp
```

**Check logs:**
```bash
# Lihat logs untuk pastikan tidak ada error
docker compose logs backend --tail 50
docker compose logs celery_worker --tail 50
docker compose logs frontend --tail 20
```

---

### STEP 8: Test Koneksi

```bash
# Test dari server
curl http://localhost:9572  # Frontend
curl http://localhost:9571/api/health  # Backend API

# Test dari browser (komputer lain)
# http://server-ip:9572  # Frontend UI
# http://server-ip:9571/docs  # API Documentation
```

---

### STEP 9: Setup Firewall

```bash
# Install UFW (jika belum ada)
sudo apt install ufw -y

# Setup firewall rules
sudo ufw allow 22/tcp          # SSH
sudo ufw allow 9572/tcp        # Frontend
sudo ufw allow 9571/tcp        # Backend API

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

**Untuk restrict ke IP tertentu (recommended):**
```bash
# Hanya allow dari internal network
sudo ufw allow from 192.168.1.0/24 to any port 9572
sudo ufw allow from 192.168.1.0/24 to any port 9571
```

---

### STEP 10: Auto-Start on Boot

```bash
# Docker auto-restart sudah configured
# Pastikan Docker service auto-start

sudo systemctl enable docker
sudo systemctl enable containerd

# Verify
sudo systemctl is-enabled docker
```

---

## ✅ Checklist Deployment

Setelah semua step, verify dengan checklist ini:

- [ ] Semua 5 containers running (`docker compose ps`)
- [ ] PostgreSQL status "healthy"
- [ ] Redis status "healthy"
- [ ] Backend logs tidak ada error
- [ ] Celery worker connected ke Redis
- [ ] Frontend accessible: `http://server-ip:9572`
- [ ] Backend API accessible: `http://server-ip:9571/docs`
- [ ] Health check OK: `curl http://localhost:9571/api/health`
- [ ] Firewall configured
- [ ] Test upload dan forecast berhasil

---

## 🔧 Post-Deployment

### Setup Automated Backup

```bash
# Buat backup script
sudo nano /usr/local/bin/forecast-backup.sh
```

**Isi script:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/forecast/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup database
docker exec forecast_postgres pg_dump -U forecast_user forecast_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup files
tar -czf "$BACKUP_DIR/files_$DATE.tar.gz" -C /opt/forecast/backend uploads outputs models

# Keep last 7 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Setup cron:**
```bash
# Make executable
sudo chmod +x /usr/local/bin/forecast-backup.sh

# Test run
sudo /usr/local/bin/forecast-backup.sh

# Add to crontab (backup daily at 2 AM)
crontab -e
# Add line:
0 2 * * * /usr/local/bin/forecast-backup.sh >> /opt/forecast/logs/backup.log 2>&1
```

---

## 🔄 Update/Restart Commands

### Restart Services
```bash
cd /opt/forecast

# Restart semua
docker compose restart

# Restart specific
docker compose restart backend
docker compose restart celery_worker
```

### Update Aplikasi
```bash
cd /opt/forecast

# Stop services
docker compose down

# Pull latest (jika via Git)
git pull

# Rebuild
docker compose build

# Start
docker compose up -d
```

### View Logs
```bash
cd /opt/forecast

# Real-time logs
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery_worker

# Last 100 lines
docker compose logs --tail 100 backend
```

---

## 🆘 Troubleshooting

### Services Not Starting
```bash
# Check logs
docker compose logs

# Check disk space
df -h

# Check port usage
sudo netstat -tulpn | grep 9571
```

### Port Already in Use
```bash
# Find process
sudo lsof -i :9572

# Kill process
sudo kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL
docker compose logs postgres

# Restart database
docker compose restart postgres
```

### Frontend Can't Connect to API
```bash
# Check API URL in logs
docker compose logs frontend | grep api

# Rebuild frontend dengan .env yang benar
docker compose build frontend
docker compose up -d frontend
```

### Complete Restart
```bash
cd /opt/forecast
docker compose down
docker compose up -d
docker compose logs -f
```

---

## 📊 Monitoring

### Check Status
```bash
# Container status
docker compose ps

# Resource usage
docker stats

# Disk space
df -h /opt/forecast
du -sh /opt/forecast/backend/*
```

### Database Size
```bash
docker exec forecast_postgres psql -U forecast_user forecast_db -c "SELECT pg_size_pretty(pg_database_size('forecast_db'));"
```

### Check Jobs
```bash
docker exec forecast_postgres psql -U forecast_user forecast_db -c "SELECT status, COUNT(*) FROM forecast_jobs GROUP BY status;"
```

---

## 🌐 Domain & SSL (Optional)

Jika ingin pakai domain dengan SSL:

### Setup Nginx Reverse Proxy
```bash
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure Nginx
sudo nano /etc/nginx/sites-available/forecast
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name forecast.motorsights.com;

    location / {
        proxy_pass http://localhost:9572;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name api-forecast.motorsights.com;

    location / {
        proxy_pass http://localhost:9571;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/forecast /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Setup SSL:**
```bash
sudo certbot --nginx -d forecast.motorsights.com -d api-forecast.motorsights.com
```

---

## 📞 Quick Reference

### Important Directories
```
/opt/forecast/              # Application root
/opt/forecast/backend/      # Backend code
/opt/forecast/frontend/     # Frontend code
/opt/forecast/backups/      # Backup files
/opt/forecast/logs/         # Application logs
```

### Important Commands
```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart
docker compose restart

# Status
docker compose ps

# Logs
docker compose logs -f

# Backup
/usr/local/bin/forecast-backup.sh
```

### Important URLs
```
Frontend: http://server-ip:9572
API Docs: http://server-ip:9571/docs
Health:   http://server-ip:9571/api/health
```

---

## ✅ Deployment Complete!

Jika semua checklist terpenuhi, aplikasi sudah siap digunakan! 🎉

**Next Steps:**
1. Test upload data dan run forecast
2. Share URL ke user: `http://server-ip:9572`
3. Monitor logs regular
4. Setup monitoring/alerting (optional)

---

**Dokumentasi Lengkap:** Lihat `UBUNTU_SETUP_GUIDE.md`  
**Port Config:** Lihat `PORT_CONFIGURATION.md`  
**Troubleshooting:** Lihat `BATCH_TROUBLESHOOTING.md`


