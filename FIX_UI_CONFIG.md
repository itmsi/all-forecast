# 🔧 Fix UI Configuration - Server

## Masalah
UI masih menggunakan localhost untuk API calls, padahal sudah di server.

## Penyebab
1. Docker Compose hardcoded `REACT_APP_API_URL=http://localhost:9571`
2. Environment variable tidak terbaca saat build

## Solusi

### Di Server Ubuntu:

```bash
# 1. Login ke server
ssh user@server-ip
cd /opt/forecast

# 2. Pull update terbaru
git pull origin main

# 3. Jalankan script fix
chmod +x fix-ui-config.sh
./fix-ui-config.sh
```

### Manual Fix (jika script tidak ada):

```bash
# 1. Update .env file
nano .env
```

**Isi file .env:**
```bash
# Environment Variables untuk Forecast System
DB_PASSWORD=forecast_secure_password_123
REACT_APP_API_URL=http://SERVER_IP:9571
```

**Ganti `SERVER_IP` dengan IP server Anda:**
```bash
# Get server IP
hostname -I | awk '{print $1}'

# Contoh: jika IP server 192.168.1.100
REACT_APP_API_URL=http://192.168.1.100:9571
```

```bash
# 2. Stop services
docker compose down

# 3. Rebuild frontend
docker compose build frontend --no-cache

# 4. Start services
docker compose up -d

# 5. Check status
docker compose ps

# 6. Test
curl http://localhost:9571/api/health
```

## Verifikasi

Setelah fix, cek:

1. **Container status:**
   ```bash
   docker compose ps
   ```

2. **Frontend accessible:**
   ```bash
   curl http://SERVER_IP:9572
   ```

3. **API accessible:**
   ```bash
   curl http://SERVER_IP:9571/api/health
   ```

4. **Browser test:**
   - Buka: `http://SERVER_IP:9572`
   - Cek Network tab di Developer Tools
   - API calls harus ke `http://SERVER_IP:9571` bukan localhost

## Troubleshooting

### Jika masih localhost:
```bash
# Check environment variable
docker compose config | grep REACT_APP_API_URL

# Rebuild dengan force
docker compose build frontend --no-cache --pull
docker compose up -d frontend
```

### Jika API tidak accessible:
```bash
# Check firewall
sudo ufw status
sudo ufw allow 9571/tcp

# Check port
sudo netstat -tulpn | grep 9571
```

### Jika frontend tidak load:
```bash
# Check logs
docker compose logs frontend

# Restart frontend
docker compose restart frontend
```

## Script Otomatis

Gunakan script `fix-ui-config.sh` untuk fix otomatis:

```bash
cd /opt/forecast
chmod +x fix-ui-config.sh
./fix-ui-config.sh
```

Script akan:
- ✅ Check file .env
- ✅ Set REACT_APP_API_URL ke IP server
- ✅ Stop services
- ✅ Rebuild frontend
- ✅ Start services
- ✅ Test koneksi
- ✅ Show status
