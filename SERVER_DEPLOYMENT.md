# 🚀 Panduan Deploy ke Server Ubuntu

Cara deploy Forecast System dengan port baru ke server Ubuntu.

---

## 📋 Port Configuration

| Service | Port | URL |
|---------|------|-----|
| **Backend API** | 9572 | `http://server-ip:9572` |
| **Frontend UI** | 9573 | `http://server-ip:9573` |
| **PostgreSQL** | 9574 | `server-ip:9574` |
| **Redis** | 9575 | `server-ip:9575` |

---

## 🎯 Step-by-Step Deployment

### 1️⃣ Upload Project ke Server

**Option A: Via SCP (dari komputer lokal)**
```bash
# Compress project
cd /Users/falaqmsi/Documents/GitHub/forecast
tar -czf forecast.tar.gz \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='backend/uploads/*' \
  --exclude='backend/outputs/*' \
  .

# Upload ke server
scp forecast.tar.gz user@server-ip:/opt/
```

**Option B: Via Git (jika repository sudah di-push)**
```bash
# Di server
cd /opt
sudo mkdir -p forecast
sudo chown $USER:$USER forecast
cd forecast
git clone <your-repo-url> .
```

**Option C: Via SFTP/FileZilla**
- Upload semua folder ke server: `/opt/forecast/`

---

### 2️⃣ Setup di Server

```bash
# Login ke server
ssh user@server-ip

# Extract (jika via SCP)
cd /opt
sudo mkdir -p forecast
sudo chown $USER:$USER forecast
tar -xzf forecast.tar.gz -C forecast/
cd forecast

# Atau jika via Git, sudah di folder forecast
cd /opt/forecast
```

---

### 3️⃣ Setup Environment Variables

```bash
cd /opt/forecast

# Buat file .env
nano .env
```

**Isi file `.env`:**
```bash
# Database Configuration
DB_PASSWORD=GantiDenganPasswordKuat2024!@#$

# API Configuration (untuk production)
REACT_APP_API_URL=https://api-forecast.motorsights.com
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### 4️⃣ Setup Folder Permissions

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

### 5️⃣ Build & Start Services

```bash
cd /opt/forecast

# Build semua images (5-10 menit pertama kali)
docker compose build

# Start semua services
docker compose up -d

# Check status
docker compose ps
```

**Expected output:**
```
NAME                     STATUS              PORTS
forecast_backend         Up                  0.0.0.0:9572->8000/tcp
forecast_celery_worker   Up
forecast_frontend        Up                  0.0.0.0:9573->80/tcp
forecast_postgres        Up (healthy)        0.0.0.0:9574->5432/tcp
forecast_redis           Up (healthy)        0.0.0.0:9575->6379/tcp
```

---

### 6️⃣ Setup Firewall

```bash
# Install UFW (jika belum ada)
sudo apt install ufw -y

# Setup firewall rules
sudo ufw allow 22/tcp          # SSH
sudo ufw allow 9572/tcp        # Backend API
sudo ufw allow 9573/tcp        # Frontend UI

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

**Expected output:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
9572/tcp                   ALLOW       Anywhere
9573/tcp                   ALLOW       Anywhere
```

---

### 7️⃣ Verify Deployment

```bash
# Test dari server
curl http://localhost:9572/api/health
curl http://localhost:9573

# Test dari browser (komputer lain)
# Buka: http://server-ip:9573
```

---

## 🔧 Management Commands

### Start Services
```bash
cd /opt/forecast
docker compose up -d
```

### Stop Services
```bash
cd /opt/forecast
docker compose down
```

### Restart Services
```bash
cd /opt/forecast
docker compose restart
```

### View Logs
```bash
cd /opt/forecast

# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery_worker
```

### Check Status
```bash
cd /opt/forecast
docker compose ps
```

---

## 🔄 Update Application

```bash
cd /opt/forecast

# Stop services
docker compose down

# Pull latest changes (jika via Git)
git pull

# Rebuild images
docker compose build

# Start services
docker compose up -d

# Check status
docker compose ps
```

---

## 🆘 Troubleshooting

### Services Not Starting
```bash
# Check logs
docker compose logs backend
docker compose logs frontend

# Check disk space
df -h

# Check port usage
sudo netstat -tulpn | grep 9572
sudo netstat -tulpn | grep 9573
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :9572
sudo lsof -i :9573

# Kill process
sudo kill -9 <PID>
```

### Frontend Can't Connect to Backend
```bash
# Check if frontend is using correct API URL
docker exec forecast_frontend sh -c "grep -r 'localhost:9572' /usr/share/nginx/html/static/js/"

# If not found, rebuild frontend
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Database Connection Error
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

---

## 📊 Monitoring

### Check Resource Usage
```bash
# Container resource usage
docker stats

# Disk usage
df -h /opt/forecast
du -sh /opt/forecast/backend/*
```

### Check Database Size
```bash
docker exec forecast_postgres psql -U forecast_user forecast_db -c "SELECT pg_size_pretty(pg_database_size('forecast_db'));"
```

### Check Active Jobs
```bash
docker exec forecast_postgres psql -U forecast_user forecast_db -c "SELECT status, COUNT(*) FROM forecast_jobs GROUP BY status;"
```

---

## 🔐 Security Setup

### Restrict Access to Internal Network
```bash
# Hanya allow dari internal network (contoh: 192.168.1.0/24)
sudo ufw delete allow 9572/tcp
sudo ufw delete allow 9573/tcp

sudo ufw allow from 192.168.1.0/24 to any port 9572
sudo ufw allow from 192.168.1.0/24 to any port 9573

# Check status
sudo ufw status
```

### Setup Auto-Start on Boot
```bash
# Docker auto-restart sudah configured
# Pastikan Docker service auto-start
sudo systemctl enable docker
sudo systemctl enable containerd

# Verify
sudo systemctl is-enabled docker
```

---

## ✅ Verification Checklist

- [ ] All containers status "Up"
- [ ] Backend API accessible: `http://server-ip:9572/api/health`
- [ ] Frontend UI accessible: `http://server-ip:9573`
- [ ] Frontend build contains `localhost:9572` in JS files
- [ ] Test upload and forecast from frontend
- [ ] Check DevTools Network tab - requests go to `localhost:9572`
- [ ] Firewall configured with correct ports
- [ ] Auto-start on boot enabled

---

## 🌐 Access URLs

**For Users:**
- Frontend: `http://server-ip:9573`

**For Developers:**
- Backend API: `http://server-ip:9572`
- API Docs: `http://server-ip:9572/docs`
- Health Check: `http://server-ip:9572/api/health`

**For Database Admin (Optional):**
- PostgreSQL: `server-ip:9574`
- Redis: `server-ip:9575`

---

## 📞 Quick Reference

### Important Commands
```bash
# Start
cd /opt/forecast && docker compose up -d

# Stop
cd /opt/forecast && docker compose down

# Restart
cd /opt/forecast && docker compose restart

# Status
cd /opt/forecast && docker compose ps

# Logs
cd /opt/forecast && docker compose logs -f
```

### Important Directories
```
/opt/forecast/              # Application root
/opt/forecast/backend/      # Backend code
/opt/forecast/frontend/     # Frontend code
/opt/forecast/backups/      # Backup files
/opt/forecast/logs/         # Application logs
```

---

## 🎉 Success!

Jika semua checklist terpenuhi, aplikasi sudah siap digunakan!

**Next Steps:**
1. Test upload data dan run forecast
2. Share URL ke user: `http://server-ip:9573`
3. Monitor logs regular
4. Setup monitoring/alerting (optional)

---

**Dokumentasi Lengkap:** Lihat `UBUNTU_SETUP_GUIDE.md`  
**Port Config:** Lihat `PORT_CONFIGURATION.md`  
**Troubleshooting:** Lihat `BATCH_TROUBLESHOOTING.md`
