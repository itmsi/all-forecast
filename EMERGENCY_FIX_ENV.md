# 🚨 Emergency Fix: Environment Variable Tidak Terbaca

Problem: `grep -r 'api-forecast'` tidak menemukan apa-apa = Build gagal.

---

## 🔥 Solution: Edit Dockerfile Langsung

### Method 1: Hardcode di Dockerfile (PALING PASTI)

```bash
# Di server
cd /opt/forecast

# Edit Dockerfile frontend
nano frontend/Dockerfile
```

**Tambahkan ENV sebelum RUN npm run build:**

```dockerfile
# Frontend Dockerfile - Multi-stage build
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY public/ ./public/
COPY src/ ./src/

# ⭐ TAMBAHKAN INI ⭐
ENV REACT_APP_API_URL=https://api-forecast.motorsights.com

# Build production bundle
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

**Save:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Method 2: Via docker-compose.yml (Alternative)

```bash
# Edit docker-compose.yml
nano docker-compose.yml
```

**Update section frontend:**

```yaml
  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - REACT_APP_API_URL=https://api-forecast.motorsights.com
    container_name: forecast_frontend
    ports:
      - "9572:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - forecast_network
```

**Dan update Dockerfile untuk terima ARG:**

```dockerfile
FROM node:18-alpine as build

# ⭐ TAMBAHKAN INI ⭐
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY public/ ./public/
COPY src/ ./src/
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## ⚡ Execute Fix

### Pilih Method 1 (Hardcode) - Lebih Simple

```bash
# Di server
cd /opt/forecast

# 1. Edit Dockerfile (sudah di atas)
nano frontend/Dockerfile

# 2. Hapus container & image lama
docker compose stop frontend
docker rm forecast_frontend
docker rmi forecast-frontend

# 3. Rebuild
docker compose build --no-cache frontend

# 4. Start
docker compose up -d frontend

# 5. Verify
docker exec forecast_frontend sh -c "grep -r 'api-forecast' /usr/share/nginx/html/static/js/"
```

**Expected output:**
```
/usr/share/nginx/html/static/js/main.xxxxx.js:...api-forecast.motorsights.com...
```

---

## 🔍 Debug: Check Build Process

```bash
# Check build logs
docker compose build --no-cache frontend 2>&1 | grep -i "react_app"

# Check environment di build stage
docker run --rm -it forecast-frontend sh -c "echo $REACT_APP_API_URL"
```

---

## 🎯 Alternative: Manual Build (Jika Dockerfile Gagal)

```bash
# Di server
cd /opt/forecast/frontend

# 1. Install Node.js (jika belum ada)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. Build manual
npm install
REACT_APP_API_URL=https://api-forecast.motorsights.com npm run build

# 3. Copy ke container
docker cp build/ forecast_frontend:/usr/share/nginx/html/

# 4. Restart
docker compose restart frontend

# 5. Verify
docker exec forecast_frontend sh -c "grep -r 'api-forecast' /usr/share/nginx/html/static/js/"
```

---

## 📝 Complete Fix Script

```bash
#!/bin/bash
# === EMERGENCY FIX SCRIPT ===

cd /opt/forecast

echo "🚨 Emergency Fix: Environment Variable Issue"
echo ""

echo "🔧 Step 1: Backup current Dockerfile..."
cp frontend/Dockerfile frontend/Dockerfile.backup

echo "🔧 Step 2: Create new Dockerfile with hardcoded ENV..."
cat > frontend/Dockerfile << 'EOF'
# Frontend Dockerfile - Multi-stage build
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY public/ ./public/
COPY src/ ./src/

# ⭐ HARDCODE ENVIRONMENT VARIABLE ⭐
ENV REACT_APP_API_URL=https://api-forecast.motorsights.com

# Build production bundle
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
EOF

echo "✅ New Dockerfile created with hardcoded ENV"
echo ""

echo "🔧 Step 3: Stop and remove old frontend..."
docker compose stop frontend
docker rm forecast_frontend
docker rmi forecast-frontend 2>/dev/null || true

echo "🔧 Step 4: Rebuild frontend (2-3 minutes)..."
docker compose build --no-cache frontend

echo "🔧 Step 5: Start new frontend..."
docker compose up -d frontend

echo "🔧 Step 6: Wait 10 seconds..."
sleep 10

echo "🔍 Step 7: Verify API URL in build..."
RESULT=$(docker exec forecast_frontend sh -c "grep -r 'api-forecast' /usr/share/nginx/html/static/js/ | head -1" 2>/dev/null)

if [ -n "$RESULT" ]; then
    echo "✅ SUCCESS! API URL found:"
    echo "$RESULT"
    echo ""
    echo "🎉 Frontend is now using: https://api-forecast.motorsights.com"
    echo ""
    echo "📋 Next steps:"
    echo "1. Open browser in INCOGNITO mode"
    echo "2. Go to: http://server-ip:9572"
    echo "3. Test upload and forecast"
    echo "4. Check DevTools Network tab - should see requests to api-forecast.motorsights.com"
else
    echo "❌ FAILED! API URL still not found in build"
    echo ""
    echo "🔧 Try manual build method..."
    echo "cd /opt/forecast/frontend"
    echo "npm install"
    echo "REACT_APP_API_URL=https://api-forecast.motorsights.com npm run build"
    echo "docker cp build/ forecast_frontend:/usr/share/nginx/html/"
    echo "docker compose restart frontend"
fi

echo ""
echo "📁 Backup Dockerfile saved as: frontend/Dockerfile.backup"
```

**Save dan jalankan:**
```bash
# Di server
nano /opt/forecast/emergency-fix.sh
# Paste script di atas
# Save: Ctrl+O, Enter, Ctrl+X

# Make executable
chmod +x /opt/forecast/emergency-fix.sh

# Run
/opt/forecast/emergency-fix.sh
```

---

## 🎯 Quick Commands (Copy-Paste)

```bash
# === EMERGENCY FIX ===

cd /opt/forecast

# 1. Edit Dockerfile
nano frontend/Dockerfile
# Tambahkan: ENV REACT_APP_API_URL=https://api-forecast.motorsights.com
# Sebelum: RUN npm run build

# 2. Rebuild
docker compose stop frontend
docker rm forecast_frontend
docker rmi forecast-frontend
docker compose build --no-cache frontend
docker compose up -d frontend

# 3. Verify
docker exec forecast_frontend sh -c "grep -r 'api-forecast' /usr/share/nginx/html/static/js/"
```

---

## ✅ Success Indicators

**Benar jika:**
1. ✅ `grep` command menemukan "api-forecast" di file JS
2. ✅ Browser DevTools Network tab request ke `https://api-forecast.motorsights.com`
3. ✅ Forecast job berhasil terkirim ke API production

**Salah jika:**
1. ❌ `grep` command kosong (tidak ada output)
2. ❌ Browser masih request ke `localhost:9571`
3. ❌ Forecast job gagal dengan connection error

---

**Coba Method 1 (hardcode di Dockerfile) dulu!** 🚀
