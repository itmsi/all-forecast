# 🔥 ULTIMATE FIX - Environment Variable Issue

Masih gagal? Mari coba approach yang lebih agresif.

---

## 🎯 Root Cause Analysis

Kemungkinan masalah:
1. Docker build cache masih ada
2. Node.js build process tidak membaca ENV
3. File .env tidak di-copy ke container
4. React build process bermasalah

---

## ⚡ NUCLEAR OPTION: Complete Rebuild

```bash
# === DI SERVER ===

cd /opt/forecast

# 1. STOP SEMUA
docker compose down

# 2. HAPUS SEMUA IMAGES & CONTAINERS
docker rm -f $(docker ps -aq) 2>/dev/null || true
docker rmi -f $(docker images -q) 2>/dev/null || true

# 3. HAPUS SEMUA VOLUMES & NETWORKS
docker volume prune -f
docker network prune -f
docker system prune -a -f

# 4. VERIFY CLEAN
docker images
docker ps -a
```

**Expected:** Semua kosong!

---

## 🔧 Method 1: Edit Source Code Langsung

```bash
cd /opt/forecast

# 1. Edit file API configuration di source code
nano frontend/src/services/api.js
```

**Cari baris yang berisi API URL, ubah menjadi:**

```javascript
// Ganti dari:
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:9571';

// Menjadi:
const API_BASE_URL = 'https://api-forecast.motorsights.com';
```

**Atau cari file yang import API URL dan hardcode:**

```bash
# Cari file yang menggunakan API URL
grep -r "localhost:9571" frontend/src/
grep -r "REACT_APP_API_URL" frontend/src/
```

**Edit file tersebut dan hardcode URL.**

---

## 🔧 Method 2: Build Manual dengan Node.js

```bash
cd /opt/forecast

# 1. Install Node.js di server (jika belum ada)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. Masuk ke folder frontend
cd frontend

# 3. Install dependencies
npm install

# 4. Build dengan environment variable
REACT_APP_API_URL=https://api-forecast.motorsights.com npm run build

# 5. Copy hasil build ke container
docker cp build/ forecast_frontend:/usr/share/nginx/html/

# 6. Restart frontend
docker compose restart frontend

# 7. Verify
docker exec forecast_frontend sh -c "grep -r 'api-forecast' /usr/share/nginx/html/static/js/"
```

---

## 🔧 Method 3: Edit Built Files Langsung

```bash
cd /opt/forecast

# 1. Start frontend container
docker compose up -d frontend

# 2. Masuk ke container
docker exec -it forecast_frontend sh

# 3. Cari file JS yang berisi localhost
find /usr/share/nginx/html/static/js/ -name "*.js" -exec grep -l "localhost" {} \;

# 4. Edit file tersebut
nano /usr/share/nginx/html/static/js/main.xxxxx.js

# 5. Replace semua localhost:9571 dengan api-forecast.motorsights.com
# Ctrl+W untuk search, ganti semua

# 6. Exit container
exit

# 7. Restart
docker compose restart frontend
```

---

## 🔧 Method 4: Dockerfile dengan Build Args

```bash
cd /opt/forecast

# 1. Edit docker-compose.yml
nano docker-compose.yml
```

**Update frontend section:**

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        REACT_APP_API_URL: https://api-forecast.motorsights.com
    container_name: forecast_frontend
    ports:
      - "9572:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - forecast_network
```

**2. Edit Dockerfile:**

```bash
nano frontend/Dockerfile
```

**Update menjadi:**

```dockerfile
# Frontend Dockerfile - Multi-stage build
FROM node:18-alpine as build

# Accept build argument
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY public/ ./public/
COPY src/ ./src/

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

**3. Rebuild:**

```bash
docker compose build --no-cache frontend
docker compose up -d frontend
```

---

## 🔧 Method 5: Nginx Proxy (Bypass Issue)

```bash
cd /opt/forecast

# 1. Edit nginx config
nano frontend/nginx.conf
```

**Update nginx.conf:**

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API calls to production
    location /api/ {
        proxy_pass https://api-forecast.motorsights.com/api/;
        proxy_set_header Host api-forecast.motorsights.com;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**2. Update frontend code untuk pakai relative URL:**

```bash
nano frontend/src/services/api.js
```

**Ubah menjadi:**

```javascript
// Pakai relative URL, nginx akan proxy ke production
const API_BASE_URL = '/api';
```

**3. Rebuild:**

```bash
docker compose build --no-cache frontend
docker compose up -d frontend
```

---

## 🎯 Quick Test Script

```bash
#!/bin/bash
# === ULTIMATE TEST SCRIPT ===

cd /opt/forecast

echo "🔍 Testing all methods..."

echo ""
echo "Method 1: Check current build..."
docker exec forecast_frontend sh -c "grep -r 'api-forecast' /usr/share/nginx/html/static/js/" || echo "❌ Method 1: FAILED"

echo ""
echo "Method 2: Check for localhost..."
docker exec forecast_frontend sh -c "grep -r 'localhost' /usr/share/nginx/html/static/js/" && echo "❌ Method 2: Still has localhost" || echo "✅ Method 2: No localhost found"

echo ""
echo "Method 3: Check environment in container..."
docker exec forecast_frontend sh -c "env | grep REACT" || echo "❌ Method 3: No REACT env vars"

echo ""
echo "Method 4: Check nginx config..."
docker exec forecast_frontend cat /etc/nginx/conf.d/default.conf | grep -i proxy || echo "❌ Method 4: No proxy config"

echo ""
echo "Method 5: Manual file check..."
docker exec forecast_frontend find /usr/share/nginx/html/static/js/ -name "*.js" -exec grep -l "9571" {} \; || echo "✅ Method 5: No port 9571 found"

echo ""
echo "🎯 RECOMMENDATION:"
echo "If all methods failed, try Method 5 (Nginx Proxy) - it bypasses the build issue completely!"
```

**Save dan jalankan:**
```bash
nano /opt/forecast/test-methods.sh
# Paste script
chmod +x /opt/forecast/test-methods.sh
/opt/forecast/test-methods.sh
```

---

## 🚀 RECOMMENDED: Method 5 (Nginx Proxy)

**Ini paling pasti berhasil** karena tidak bergantung pada React build process:

```bash
cd /opt/forecast

# 1. Edit nginx config
nano frontend/nginx.conf
# Paste config di atas

# 2. Edit API service
nano frontend/src/services/api.js
# Ubah ke: const API_BASE_URL = '/api';

# 3. Rebuild
docker compose build --no-cache frontend
docker compose up -d frontend

# 4. Test
curl http://server-ip:9572/api/health
# Should proxy to: https://api-forecast.motorsights.com/api/health
```

---

## 📞 Debug Commands

```bash
# Check what's actually in the built files
docker exec forecast_frontend sh -c "find /usr/share/nginx/html/static/js/ -name '*.js' -exec head -20 {} \;"

# Check nginx logs
docker compose logs frontend

# Check if nginx is running
docker exec forecast_frontend ps aux | grep nginx

# Check nginx config
docker exec forecast_frontend nginx -t
```

---

**Coba Method 5 (Nginx Proxy) dulu!** Ini bypass semua masalah build React! 🚀
