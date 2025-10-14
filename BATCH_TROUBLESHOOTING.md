# 🔧 Troubleshooting Guide: Batch Tidak Jalan

## Problem
- Regular forecast: ✅ SUKSES
- Batch forecast: ❌ TIDAK JALAN

## Root Cause Analysis

### 1. Celery Worker Tidak Running
Batch proses membutuhkan Celery worker untuk background processing.

### 2. Redis Tidak Running  
Celery butuh Redis sebagai message broker.

### 3. Format Date Berpotensi Ambigu
Format seperti `7/1/2024` bisa diparse sebagai July 1 atau Jan 7 tergantung setting.

---

## ✅ Langkah Perbaikan

### Step 1: Cek Status Services

```bash
# Cek apakah Redis running
redis-cli ping
# Expected output: PONG
```

Jika Redis tidak running:
```bash
# macOS dengan Homebrew
brew services start redis

# Atau manual
redis-server
```

### Step 2: Jalankan Celery Worker

Buka terminal BARU, masuk ke folder backend:

```bash
cd /Users/falaqmsi/Documents/GitHub/forecast/backend

# Jalankan Celery worker
celery -A app.celery_app worker --loglevel=info
```

**PENTING:** Biarkan terminal ini tetap terbuka saat menjalankan batch!

### Step 3: Cek Health Check

Buka browser, akses:
```
http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "database": "ok",
  "celery": "ok",  // ← Harus "ok", bukan "no workers available"
  "version": "1.0.0"
}
```

Jika `celery: "no workers available"` → Celery worker belum jalan (kembali ke Step 2)

### Step 4: Test Batch Forecast

Sekarang coba batch forecast lagi dengan `sample_optimal.csv`

---

## 🚀 Cara Menjalankan Full System

Untuk menjalankan batch forecast, Anda butuh **3 terminal**:

### Terminal 1: Redis
```bash
redis-server
```

### Terminal 2: Backend API
```bash
cd /Users/falaqmsi/Documents/GitHub/forecast/backend
uvicorn app.main:app --reload --port 8000
```

### Terminal 3: Celery Worker
```bash
cd /Users/falaqmsi/Documents/GitHub/forecast/backend
celery -A app.celery_app worker --loglevel=info
```

### Terminal 4 (optional): Frontend
```bash
cd /Users/falaqmsi/Documents/GitHub/forecast/frontend
npm start
```

---

## 🔍 Debug Tips

### Melihat Log Celery
Di terminal Celery worker, Anda akan melihat:
```
[2024-10-14 10:30:00,123: INFO/MainProcess] Received task: batch.run_batch_forecast[abc123]
[2024-10-14 10:30:01,456: INFO/ForkPoolWorker-1] [Batch abc123] Starting batch forecast
[2024-10-14 10:30:02,789: INFO/ForkPoolWorker-1] [Batch abc123] Processing partition 0/3
```

### Cek Status Job
```bash
# Via API
curl http://localhost:8000/api/batch/status/YOUR_BATCH_ID

# Atau via browser
http://localhost:8000/api/batch/history
```

### Common Errors

#### Error: "no workers available"
**Solusi:** Jalankan Celery worker (Step 2)

#### Error: "Connection refused (Redis)"
**Solusi:** Jalankan Redis server (Step 1)

#### Error: "Date parsing failed"
**Solusi:** Gunakan parameter `dayfirst=true` di config

---

## 📝 Quick Start Script

Buat file `start_all.sh`:

```bash
#!/bin/bash

# Start Redis
redis-server &

# Wait for Redis
sleep 2

# Start Backend
cd /Users/falaqmsi/Documents/GitHub/forecast/backend
uvicorn app.main:app --reload --port 8000 &

# Wait for Backend
sleep 3

# Start Celery Worker
celery -A app.celery_app worker --loglevel=info &

echo "✅ All services started!"
echo "API: http://localhost:8000/api/docs"
echo "Health: http://localhost:8000/api/health"
```

Jalankan:
```bash
chmod +x start_all.sh
./start_all.sh
```

---

## 📊 File CSV Requirements

File `sample_optimal.csv` Anda sudah benar formatnya:

```csv
demand_qty,date,partnumber,site_code
27,7/1/2024,HD95009410007,IEL-MU-SFI
63,7/1/2024,Q151C1275T1F3,IEL-MU-SFI
```

**Pastikan:**
- Header: `demand_qty,date,partnumber,site_code` ✅
- Date format consistent ✅
- No missing values di kolom wajib ✅

---

## ✅ Verification Checklist

- [ ] Redis running (`redis-cli ping` → PONG)
- [ ] Backend API running (http://localhost:8000)
- [ ] Celery worker running (terminal aktif dengan log)
- [ ] Health check OK (celery: "ok")
- [ ] Upload file CSV
- [ ] Submit batch forecast
- [ ] Lihat progress di Celery log
- [ ] Download hasil

---

## 💡 Tips

1. **Selalu jalankan Celery worker** sebelum submit batch
2. **Jangan close terminal** Celery saat batch berjalan
3. **Monitor log** di terminal Celery untuk debug
4. **Gunakan smaller batch** untuk testing (max 2000 rows/partition)


