# 🔄 Update Environment Variables di Server

Panduan update konfigurasi .env untuk sistem yang sudah running.

---

## 📝 Scenario: Lupa Update .env Sebelum Deploy

Sistem sudah jalan, tapi REACT_APP_API_URL masih localhost atau salah.

---

## ⚡ Quick Fix (3 Langkah)

### 1️⃣ Update File .env di Server

```bash
# Login ke server
ssh user@server-ip

# Masuk ke folder aplikasi
cd /opt/forecast

# Edit .env
nano .env
```

**Update isi .env:**
```bash
# Database Configuration
DB_PASSWORD=PasswordKuatAnda123!@#

# API Configuration  
REACT_APP_API_URL=https://api-forecast.motorsights.com
```

**Simpan:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### 2️⃣ Rebuild Frontend Saja

```bash
cd /opt/forecast

# Rebuild HANYA frontend (lebih cepat, ~2-3 menit)
docker compose build --no-cache frontend
```

**Tunggu sampai selesai.** Output:
```
...
=> => naming to docker.io/library/forecast-frontend:latest
```

---

### 3️⃣ Restart Frontend

```bash
cd /opt/forecast

# Stop dan start ulang frontend
docker compose up -d frontend

# Check status
docker compose ps
```

**Expected:** Container `forecast_frontend` status "Up"

---

## ✅ Verifikasi

### Check di Browser
```bash
# Buka developer console (F12)
# Periksa Network tab saat melakukan request
# URL harus ke: https://api-forecast.motorsights.com

# Atau check source code frontend
curl http://server-ip:9572 | grep api-forecast
```

### Check Environment di Container
```bash
# Masuk ke container frontend
docker exec -it forecast_frontend sh

# Check nginx config
cat /usr/share/nginx/html/static/js/main.*.js | grep -o "api-forecast" | head -1

# Exit
exit
```

Jika muncul "api-forecast", berarti sudah benar! ✅

---

## 🔧 Alternative: Rebuild Semua (Jika Perlu)

Jika ada perubahan di backend juga:

```bash
cd /opt/forecast

# Update .env
nano .env

# Rebuild semua
docker compose build

# Restart semua services
docker compose down
docker compose up -d

# Check status
docker compose ps
```

---

## 📊 Perbedaan Rebuild vs Restart

| Action | Command | Kapan Dipakai | Downtime |
|--------|---------|---------------|----------|
| **Restart** | `docker compose restart` | Ubah env backend (DB_PASSWORD, dll) | ~5 detik |
| **Rebuild Frontend** | `docker compose build frontend` | Ubah REACT_APP_* | ~2 menit |
| **Rebuild All** | `docker compose build` | Ubah code atau semua env | ~5 menit |

---

## 🎯 Kapan Perlu Rebuild?

### ✅ PERLU Rebuild Frontend:
- Ubah `REACT_APP_API_URL`
- Ubah environment variable dengan prefix `REACT_APP_*`
- Ubah code di folder `frontend/src/`

### ✅ PERLU Restart (Tidak Perlu Rebuild):
- Ubah `DB_PASSWORD`
- Ubah `REDIS_URL`
- Ubah konfigurasi backend (bukan code)

### ✅ PERLU Rebuild Backend:
- Ubah code di folder `backend/app/`
- Ubah `requirements.txt`

---

## 🆘 Troubleshooting

### Frontend Masih Pakai URL Lama

**Problem:** Setelah rebuild, frontend masih connect ke localhost

**Solution:**
```bash
# 1. Stop container
docker compose stop frontend

# 2. Remove container
docker rm forecast_frontend

# 3. Remove image
docker rmi forecast-frontend

# 4. Rebuild dari awal
docker compose build --no-cache frontend

# 5. Start
docker compose up -d frontend

# 6. Clear browser cache atau buka incognito
```

### Build Error: "Cannot find .env"

**Solution:**
```bash
# Pastikan .env ada di root folder
cd /opt/forecast
ls -la .env

# Jika tidak ada, buat:
nano .env
```

### Backend Connection Error After Restart

**Solution:**
```bash
# Check logs
docker compose logs backend

# Restart database dan backend
docker compose restart postgres
sleep 5
docker compose restart backend
```

---

## 📝 Complete Step-by-Step (Copy-Paste Ready)

```bash
# === DI SERVER ===

# 1. Update .env
cd /opt/forecast
nano .env
# Edit: REACT_APP_API_URL=https://api-forecast.motorsights.com
# Save: Ctrl+O, Enter, Ctrl+X

# 2. Rebuild frontend
docker compose build --no-cache frontend

# 3. Restart frontend
docker compose up -d frontend

# 4. Verify
docker compose ps
docker compose logs frontend --tail 20

# 5. Test dari browser
# http://server-ip:9572
```

---

## 🔐 Bonus: Update Password Database

Jika juga perlu update DB_PASSWORD:

```bash
cd /opt/forecast

# 1. Update .env
nano .env
# Ubah: DB_PASSWORD=PasswordBaru123!@#

# 2. Stop semua
docker compose down

# 3. HAPUS volume database (HATI-HATI! Data hilang!)
docker volume rm forecast_postgres_data

# 4. Start ulang (database baru dengan password baru)
docker compose up -d

# Atau kalau mau keep data, update password manual di PostgreSQL
```

---

## ⏱️ Estimasi Waktu

- **Update .env:** 1 menit
- **Rebuild frontend:** 2-3 menit
- **Restart frontend:** 10 detik
- **Verify:** 1 menit

**Total:** ~5 menit ⚡

---

## ✅ Checklist

- [ ] Login ke server
- [ ] `cd /opt/forecast`
- [ ] Edit `.env` dengan value yang benar
- [ ] `docker compose build --no-cache frontend`
- [ ] `docker compose up -d frontend`
- [ ] `docker compose ps` - frontend status "Up"
- [ ] Test dari browser - bisa akses
- [ ] Check network tab - request ke API URL yang benar
- [ ] Clear browser cache jika perlu

---

**Done!** Environment variable sudah terupdate dan aplikasi running dengan config baru! 🎉


