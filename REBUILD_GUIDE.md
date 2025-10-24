# 🔄 Rebuild Services Guide

Panduan untuk rebuild backend dan frontend setelah perubahan CORS configuration.

## 📋 Scripts yang Tersedia

### 1. **Complete Rebuild** (`rebuild_services.sh`)
Script lengkap dengan monitoring dan log checking:
```bash
chmod +x rebuild_services.sh
./rebuild_services.sh
```

### 2. **Quick Rebuild** (`quick_rebuild.sh`)
Script cepat untuk rebuild tanpa monitoring:
```bash
chmod +x quick_rebuild.sh
./quick_rebuild.sh
```

### 3. **Windows Script** (`rebuild_services.bat`)
Untuk Windows users:
```cmd
rebuild_services.bat
```

## 🚀 Manual Commands

Jika ingin menjalankan manual:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Stop services
docker-compose down

# 3. Build backend
docker-compose build --no-cache backend

# 4. Build frontend
docker-compose build --no-cache frontend

# 5. Start services
docker-compose up -d

# 6. Check status
docker-compose ps
```

## 🔍 Verification Steps

Setelah rebuild, verifikasi dengan:

1. **Check service status:**
   ```bash
   docker-compose ps
   ```

2. **Check logs:**
   ```bash
   docker logs forecast_backend --tail 20
   docker logs forecast_frontend --tail 20
   ```

3. **Test API health:**
   ```bash
   curl https://api-forecast.motorsights.com/api/health
   ```

4. **Test CORS:**
   ```bash
   curl -H "Origin: https://forecast.motorsights.com" \
        -H "Access-Control-Request-Method: GET" \
        -X OPTIONS \
        https://api-forecast.motorsights.com/api/health
   ```

## ⚠️ Troubleshooting

Jika masih ada masalah CORS:

1. **Clear browser cache** (Ctrl+Shift+R)
2. **Test di incognito mode**
3. **Check browser DevTools Network tab**
4. **Verify CORS headers** di response

## 📊 Expected Results

Setelah rebuild sukses:
- ✅ Frontend: https://forecast.motorsights.com
- ✅ Backend API: https://api-forecast.motorsights.com
- ✅ CORS headers present di response
- ✅ No CORS errors di browser console
