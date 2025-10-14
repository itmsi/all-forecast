# ⚡ Quick Start Guide

Panduan cepat untuk mulai menggunakan Forecast System dalam 5 menit.

## 🚀 Untuk Administrator (Deploy)

### 1. Prerequisites
```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Deploy
```bash
# Clone repository
git clone <repo-url> forecast-system
cd forecast-system

# Setup environment
cp .env.example .env
nano .env  # Edit DB_PASSWORD

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Verify
```bash
# Test API
curl http://localhost:8000/api/health

# Akses frontend
open http://localhost
```

✅ **Done!** Aplikasi siap digunakan.

---

## 👤 Untuk User (Gunakan)

### 1. Akses Aplikasi
```
Buka browser → http://server-ip
```

### 2. Prepare Data CSV
File harus punya kolom: `date`, `partnumber`, `site_code`, `demand_qty`

Contoh:
```csv
date,partnumber,site_code,demand_qty
2024-01-01,PART-001,IEL-ST-KDI,50
2024-01-02,PART-001,IEL-ST-KDI,75
```

### 3. Run Forecast
1. **Upload** CSV file
2. **Atur** config (default OK untuk pertama kali)
3. **Klik** "Jalankan Forecast"
4. **Tunggu** sampai status = COMPLETED
5. **Download** hasil CSV

✅ **Done!** Anda punya forecast demand.

---

## 📚 Dokumentasi Lengkap

- **README.md** - Overview & architecture
- **DEPLOYMENT.md** - Deployment detail untuk admin
- **USER_GUIDE.md** - Panduan lengkap untuk user

---

## 🆘 Troubleshooting Cepat

**Service tidak start?**
```bash
docker-compose logs backend
docker-compose restart
```

**Forecast FAILED?**
- Check format CSV (kolom wajib ada)
- Check format tanggal konsisten
- Lihat detail error di Status Monitor

**Perlu bantuan?**
- Lihat logs: `docker-compose logs -f`
- Health check: `curl http://localhost:8000/api/health`
- Contact IT Support dengan Job ID

---

**Happy Forecasting! 🎯**

