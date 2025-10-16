# ⚡ Quick Deploy Guide - Server Ubuntu

Panduan ringkas deploy dalam 10 langkah.

---

## 🎯 Di Server Ubuntu

### 1️⃣ Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2️⃣ Upload Project
```bash
# Buat folder
sudo mkdir -p /opt/forecast
sudo chown $USER:$USER /opt/forecast

# Upload via SCP dari lokal:
# scp -r forecast/ user@server-ip:/opt/
```

### 3️⃣ Setup Environment
```bash
cd /opt/forecast
nano .env
```
Isi:
```bash
DB_PASSWORD=PasswordKuatAnda123!@#
REACT_APP_API_URL=https://api-forecast.motorsights.com
```

### 4️⃣ Build & Start
```bash
cd /opt/forecast

# Build (5-10 menit)
docker compose build

# Start
docker compose up -d

# Check status
docker compose ps
```

### 5️⃣ Setup Firewall
```bash
sudo apt install ufw -y
sudo ufw allow 22/tcp
sudo ufw allow 9572/tcp
sudo ufw allow 9571/tcp
sudo ufw enable
```

### 6️⃣ Test
```bash
# Test dari server
curl http://localhost:9572
curl http://localhost:9571/api/health

# Test dari browser
# http://server-ip:9572
```

---

## ✅ Checklist

- [ ] Docker installed
- [ ] Project uploaded ke `/opt/forecast/`
- [ ] File `.env` created dengan password & API URL
- [ ] `docker compose build` success
- [ ] `docker compose up -d` running
- [ ] All containers status "Up"
- [ ] Firewall configured
- [ ] Frontend accessible: `http://server-ip:9572`
- [ ] API accessible: `http://server-ip:9571/docs`

---

## 🔄 Management Commands

```bash
cd /opt/forecast

# Start
docker compose up -d

# Stop
docker compose down

# Restart
docker compose restart

# View logs
docker compose logs -f

# Check status
docker compose ps
```

---

## 🆘 Troubleshooting

**Problem:** Container not starting
```bash
docker compose logs backend
docker compose restart
```

**Problem:** Port in use
```bash
sudo lsof -i :9572
sudo kill -9 <PID>
```

**Problem:** Can't access from browser
```bash
sudo ufw status
sudo ufw allow 9572/tcp
```

---

Untuk panduan lengkap, lihat: **DEPLOY_TO_SERVER.md**


