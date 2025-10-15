# 🔌 Port Configuration - Forecast System

## Port Mapping

Sistem Forecast menggunakan port berikut untuk akses eksternal:

| Service | Internal Port | External Port | URL Access |
|---------|---------------|---------------|------------|
| **PostgreSQL** | 5432 | **9573** | `localhost:9573` |
| **Redis** | 6379 | **9574** | `localhost:9574` |
| **Backend API** | 8000 | **9571** | `http://localhost:9571` |
| **Frontend UI** | 80 | **9572** | `http://localhost:9572` |

---

## 🌐 URL Akses

### Untuk User (Web Interface)
```
Frontend: http://server-ip:9572
```

### Untuk Developer (API)
```
API Base URL: http://server-ip:9571
API Docs: http://server-ip:9571/docs
Health Check: http://server-ip:9571/api/health
```

### Untuk Database Admin (Optional)
```
PostgreSQL: server-ip:9573
Username: forecast_user
Database: forecast_db
Password: (lihat .env file)
```

### Untuk Redis Admin (Optional)
```
Redis: server-ip:9574
```

---

## 📝 Quick Commands

### Check Status
```bash
cd /path/to/forecast
docker compose ps
```

### Test Connections
```bash
# Test Frontend
curl http://localhost:9572

# Test Backend API
curl http://localhost:9571/api/health

# Test PostgreSQL
docker exec forecast_postgres psql -U forecast_user -d forecast_db -c "SELECT 1;"

# Test Redis
docker exec forecast_redis redis-cli ping
```

### Restart Services
```bash
cd /path/to/forecast

# Restart semua
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart celery_worker
docker compose restart frontend
```

### View Logs
```bash
cd /path/to/forecast

# Semua logs
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery_worker
```

---

## 🔧 Firewall Configuration (Ubuntu)

Jika menggunakan UFW firewall, allow port berikut:

```bash
# Frontend (WAJIB untuk user akses)
sudo ufw allow 9572/tcp comment 'Forecast Frontend'

# Backend API (WAJIB untuk API calls)
sudo ufw allow 9571/tcp comment 'Forecast API'

# PostgreSQL (OPTIONAL - hanya jika perlu akses database eksternal)
# sudo ufw allow 9573/tcp comment 'Forecast PostgreSQL'

# Redis (OPTIONAL - hanya jika perlu akses Redis eksternal)
# sudo ufw allow 9574/tcp comment 'Forecast Redis'

# Apply firewall
sudo ufw enable
sudo ufw status
```

**Note:** Untuk keamanan, PostgreSQL dan Redis port sebaiknya TIDAK dibuka untuk akses eksternal.

---

## 🔐 Security Notes

1. **PostgreSQL (9573)** dan **Redis (9574)** port sebaiknya:
   - TIDAK dibuka untuk akses dari luar server
   - Hanya diakses melalui container internal network
   - Jika perlu akses eksternal, gunakan SSH tunnel

2. **Backend API (9571)** port:
   - Bisa dibuka untuk internal network
   - Gunakan firewall untuk restrict access ke IP tertentu
   - Contoh: `sudo ufw allow from 192.168.1.0/24 to any port 9571`

3. **Frontend (9572)** port:
   - Bisa dibuka untuk semua user internal
   - Untuk production, gunakan reverse proxy (Nginx/Apache) dengan HTTPS

---

## 🔄 Change Port Configuration

Jika ingin mengubah port, edit file `docker-compose.yml`:

```yaml
services:
  postgres:
    ports:
      - "NEW_PORT:5432"  # Ubah NEW_PORT
  
  redis:
    ports:
      - "NEW_PORT:6379"  # Ubah NEW_PORT
  
  backend:
    ports:
      - "NEW_PORT:8000"  # Ubah NEW_PORT
  
  frontend:
    ports:
      - "NEW_PORT:80"    # Ubah NEW_PORT
```

Setelah ubah, rebuild:
```bash
docker compose down
docker compose up -d
```

---

## ✅ Verification Checklist

Setelah start services, verify dengan checklist ini:

- [ ] `docker compose ps` - Semua container status **Up**
- [ ] `curl http://localhost:9572` - Frontend return HTML
- [ ] `curl http://localhost:9571/api/health` - Backend return JSON {"status":"ok"}
- [ ] `docker exec forecast_postgres psql -U forecast_user -d forecast_db -c "SELECT 1;"` - Return 1
- [ ] `docker exec forecast_redis redis-cli ping` - Return PONG
- [ ] Akses dari browser: `http://server-ip:9572` - Tampil web interface
- [ ] Upload sample data dan run forecast - Job complete successfully

---

## 📊 Port Usage Monitoring

Check port yang digunakan di system:

```bash
# Check specific ports
sudo netstat -tulpn | grep -E "9571|9572|9573|9574"

# Atau dengan ss command
sudo ss -tulpn | grep -E "9571|9572|9573|9574"

# Atau dengan lsof
sudo lsof -i :9571
sudo lsof -i :9572
sudo lsof -i :9573
sudo lsof -i :9574
```

---

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :9572

# Kill process
sudo kill -9 <PID>

# Atau ubah port di docker-compose.yml
```

### Cannot Connect from Other Computer

```bash
# Check if port listening on 0.0.0.0
netstat -an | grep 9572

# Check firewall
sudo ufw status

# Allow port
sudo ufw allow 9572/tcp
```

### Connection Refused

```bash
# Check container status
docker compose ps

# Check logs
docker compose logs backend

# Restart services
docker compose restart
```

---

**Last Updated:** October 15, 2024  
**Configuration Version:** 1.0


