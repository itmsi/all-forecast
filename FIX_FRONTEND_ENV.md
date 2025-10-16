# 🔧 Fix Frontend Environment Variable

Problem: Sudah rebuild tapi frontend masih hit ke URL lama.

---

## 🎯 Root Cause

React environment variables (`REACT_APP_*`) harus:
1. ✅ Ada di file `.env` **DI FOLDER FRONTEND**
2. ✅ Di-build dengan `--no-cache`
3. ✅ Browser cache harus di-clear

---

## ⚡ Solution (Step-by-Step)

### 🔴 STEP 1: Buat .env di Folder Frontend

```bash
# Di server
cd /opt/forecast

# Buat .env DI FOLDER FRONTEND
cat > frontend/.env << 'EOF'
REACT_APP_API_URL=https://api-forecast.motorsights.com
EOF

# Verify
cat frontend/.env
```

**PENTING:** File `.env` harus ada di `frontend/` folder, bukan hanya di root!

---

### 🔴 STEP 2: Hapus Image & Container Lama

```bash
cd /opt/forecast

# Stop frontend
docker compose stop frontend

# Remove container
docker rm forecast_frontend

# Remove image
docker rmi forecast-frontend

# Verify image terhapus
docker images | grep frontend
```

---

### 🔴 STEP 3: Rebuild Dari Nol

```bash
cd /opt/forecast

# Build frontend tanpa cache
docker compose build --no-cache frontend

# Tunggu sampai selesai (2-3 menit)
```

**Output yang benar:**
```
=> [build 7/7] RUN npm run build
=> => exporting to image
=> => naming to docker.io/library/forecast-frontend:latest
```

---

### 🔴 STEP 4: Start Frontend Baru

```bash
cd /opt/forecast

# Start frontend
docker compose up -d frontend

# Check status
docker compose ps

# Check logs
docker compose logs frontend --tail 30
```

---

### 🔴 STEP 5: Verify di Container

```bash
# Masuk ke container frontend
docker exec -it forecast_frontend sh

# Check file JS yang di-build
ls -la /usr/share/nginx/html/static/js/

# Search API URL di file JS
grep -r "api-forecast" /usr/share/nginx/html/static/js/ || echo "URL TIDAK DITEMUKAN!"

# Exit
exit
```

**Jika muncul "api-forecast", berarti BERHASIL!** ✅

---

### 🔴 STEP 6: Clear Browser Cache

**Di Browser:**
1. Tekan `Ctrl+Shift+Del` (atau `Cmd+Shift+Del` di Mac)
2. Pilih "Cached images and files"
3. Clear cache
4. **ATAU** buka **Incognito/Private mode**

**Hard Refresh:**
- Windows: `Ctrl+Shift+R`
- Mac: `Cmd+Shift+R`

---

## 🔍 Debug: Check Apa URL yang Dipakai

### Method 1: Browser Developer Tools

```
1. Buka http://server-ip:9572
2. Tekan F12 (Developer Tools)
3. Tab "Network"
4. Upload file dan klik "Run Forecast"
5. Lihat request yang keluar
   - Harus ke: https://api-forecast.motorsights.com
   - BUKAN: http://localhost:9571
```

### Method 2: Check Source Code di Browser

```
1. Buka http://server-ip:9572
2. Tekan F12
3. Tab "Sources"
4. Cari file: static/js/main.*.js
5. Search "localhost" atau "9571"
   - Jika masih ada = Build GAGAL
   - Jika tidak ada = Build SUKSES
```

### Method 3: Check di Server

```bash
cd /opt/forecast

# Download file JS dari container
docker cp forecast_frontend:/usr/share/nginx/html/static/js/ ./temp_js/

# Search localhost
grep -r "localhost" temp_js/ || echo "CLEAN! Tidak ada localhost"

# Search API URL
grep -r "api-forecast" temp_js/ && echo "SUKSES! URL sudah benar"

# Cleanup
rm -rf temp_js/
```

---

## 🛠️ Alternative: Manual Build di Frontend

Jika cara di atas masih gagal:

```bash
cd /opt/forecast/frontend

# 1. Buat .env
cat > .env << 'EOF'
REACT_APP_API_URL=https://api-forecast.motorsights.com
EOF

# 2. Build manual (jika punya Node.js di server)
npm install
npm run build

# 3. Copy hasil build ke container
docker cp build/ forecast_frontend:/usr/share/nginx/html/

# 4. Restart
docker compose restart frontend
```

---

## 📝 Complete Fix Script (Copy-Paste)

```bash
#!/bin/bash
# === COMPLETE FIX FOR FRONTEND ENV ===

cd /opt/forecast

echo "🔧 Step 1: Create .env in frontend folder..."
cat > frontend/.env << 'EOF'
REACT_APP_API_URL=https://api-forecast.motorsights.com
EOF

echo "✅ .env created:"
cat frontend/.env
echo ""

echo "🔧 Step 2: Stop and remove old frontend..."
docker compose stop frontend
docker rm forecast_frontend
docker rmi forecast-frontend 2>/dev/null || true
echo ""

echo "🔧 Step 3: Rebuild frontend (2-3 minutes)..."
docker compose build --no-cache frontend
echo ""

echo "🔧 Step 4: Start new frontend..."
docker compose up -d frontend
echo ""

echo "🔧 Step 5: Wait 10 seconds..."
sleep 10

echo "🔧 Step 6: Verify..."
docker compose ps | grep frontend
echo ""

echo "🔍 Step 7: Check if API URL is correct..."
docker exec forecast_frontend sh -c "grep -r 'api-forecast' /usr/share/nginx/html/static/js/ | head -1" && echo "✅ SUCCESS! API URL found in build" || echo "❌ FAILED! API URL not found"
echo ""

echo "🎉 Done! Now:"
echo "1. Open browser in INCOGNITO mode"
echo "2. Go to: http://server-ip:9572"
echo "3. Open DevTools (F12) → Network tab"
echo "4. Upload file and run forecast"
echo "5. Check if requests go to: https://api-forecast.motorsights.com"
```

**Save script di server:**
```bash
# Di server
nano /opt/forecast/fix-frontend.sh
# Paste script di atas
# Save: Ctrl+O, Enter, Ctrl+X

# Make executable
chmod +x /opt/forecast/fix-frontend.sh

# Run
/opt/forecast/fix-frontend.sh
```

---

## 🔍 Checklist Troubleshooting

- [ ] File `frontend/.env` ada dan berisi `REACT_APP_API_URL=https://api-forecast.motorsights.com`
- [ ] Container frontend sudah di-remove (`docker rm forecast_frontend`)
- [ ] Image frontend sudah di-remove (`docker rmi forecast-frontend`)
- [ ] Rebuild dengan `--no-cache`
- [ ] Container frontend status "Up"
- [ ] Verify dengan `docker exec` - API URL ada di file JS
- [ ] Browser cache sudah di-clear (atau pakai incognito)
- [ ] DevTools Network tab menunjukkan request ke URL yang benar

---

## 🆘 Jika Masih Gagal

### Option 1: Edit Dockerfile

```bash
cd /opt/forecast
nano frontend/Dockerfile
```

**Tambahkan ENV sebelum build:**
```dockerfile
# Frontend Dockerfile - Multi-stage build
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code
COPY public/ ./public/
COPY src/ ./src/

# ⭐ TAMBAHKAN INI ⭐
ENV REACT_APP_API_URL=https://api-forecast.motorsights.com

# Build production bundle
RUN npm run build

# ... rest of Dockerfile
```

**Lalu rebuild:**
```bash
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Option 2: Edit docker-compose.yml

```bash
nano docker-compose.yml
```

**Tambahkan build args:**
```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - REACT_APP_API_URL=https://api-forecast.motorsights.com
    # ... rest of config
```

**Update Dockerfile untuk terima arg:**
```dockerfile
FROM node:18-alpine as build
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
# ... rest
```

---

## ✅ Success Indicators

Benar jika:
1. ✅ `grep "api-forecast"` di container menemukan URL
2. ✅ Browser DevTools Network tab request ke `https://api-forecast.motorsights.com`
3. ✅ Tidak ada request ke `localhost:9571`
4. ✅ Forecast job bisa jalan dan terkirim ke API production

---

**Good luck!** 🚀


