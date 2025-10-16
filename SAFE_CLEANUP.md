# 🧹 Safe Cleanup - Hapus Forecast Saja

Cara hapus container/image forecast tanpa impact ke Docker lain.

---

## ⚡ Safe Cleanup Commands

### 1️⃣ Stop & Remove Forecast Containers Saja

```bash
# Di server
cd /opt/forecast

# Stop semua container forecast
docker compose down

# Remove container forecast saja (jika masih ada)
docker rm forecast_frontend forecast_backend forecast_celery_worker forecast_postgres forecast_redis 2>/dev/null || true

# Verify container terhapus
docker ps -a | grep forecast
```

**Expected:** Tidak ada container forecast yang muncul

---

### 2️⃣ Remove Forecast Images Saja

```bash
# Remove image forecast saja
docker rmi forecast-frontend forecast-backend forecast-celery_worker 2>/dev/null || true

# Verify image terhapus
docker images | grep forecast
```

**Expected:** Tidak ada image forecast yang muncul

---

### 3️⃣ Remove Forecast Volumes Saja

```bash
# List volume forecast
docker volume ls | grep forecast

# Remove volume forecast saja
docker volume rm forecast_postgres_data forecast_redis_data 2>/dev/null || true

# Verify volume terhapus
docker volume ls | grep forecast
```

**Expected:** Tidak ada volume forecast yang muncul

---

### 4️⃣ Remove Forecast Network Saja

```bash
# List network forecast
docker network ls | grep forecast

# Remove network forecast saja
docker network rm forecast_forecast_network 2>/dev/null || true

# Verify network terhapus
docker network ls | grep forecast
```

**Expected:** Tidak ada network forecast yang muncul

---

## 🎯 Complete Safe Cleanup Script

```bash
#!/bin/bash
# === SAFE CLEANUP FORECAST ONLY ===

cd /opt/forecast

echo "🧹 Safe Cleanup: Forecast System Only"
echo ""

echo "🔧 Step 1: Stop forecast containers..."
docker compose down

echo "🔧 Step 2: Remove forecast containers..."
docker rm forecast_frontend forecast_backend forecast_celery_worker forecast_postgres forecast_redis 2>/dev/null || true

echo "🔧 Step 3: Remove forecast images..."
docker rmi forecast-frontend forecast-backend forecast-celery_worker 2>/dev/null || true

echo "🔧 Step 4: Remove forecast volumes..."
docker volume rm forecast_postgres_data forecast_redis_data 2>/dev/null || true

echo "🔧 Step 5: Remove forecast network..."
docker network rm forecast_forecast_network 2>/dev/null || true

echo ""
echo "✅ Cleanup completed!"
echo ""

echo "📊 Verification:"
echo "Containers:"
docker ps -a | grep forecast || echo "  ✅ No forecast containers"
echo ""

echo "Images:"
docker images | grep forecast || echo "  ✅ No forecast images"
echo ""

echo "Volumes:"
docker volume ls | grep forecast || echo "  ✅ No forecast volumes"
echo ""

echo "Networks:"
docker network ls | grep forecast || echo "  ✅ No forecast networks"
echo ""

echo "🎉 Forecast system completely removed!"
echo "Other Docker containers/images are safe."
```

**Save dan jalankan:**
```bash
# Di server
nano /opt/forecast/safe-cleanup.sh
# Paste script di atas
# Save: Ctrl+O, Enter, Ctrl+X

# Make executable
chmod +x /opt/forecast/safe-cleanup.sh

# Run
/opt/forecast/safe-cleanup.sh
```

---

## 🔍 Verify Other Docker Containers Safe

```bash
# Check containers lain masih ada
docker ps -a

# Check images lain masih ada
docker images

# Check volumes lain masih ada
docker volume ls

# Check networks lain masih ada
docker network ls
```

**Expected:** Container/image/volume/network lain masih ada, hanya forecast yang hilang.

---

## 🚀 Rebuild After Cleanup

Setelah cleanup, rebuild forecast:

```bash
cd /opt/forecast

# Rebuild semua
docker compose build

# Start
docker compose up -d

# Check status
docker compose ps
```

---

## ⚠️ What NOT to Use

**JANGAN pakai command ini** (akan hapus SEMUA Docker):

```bash
# ❌ JANGAN PAKAI INI - HAPUS SEMUA!
docker system prune -a -f
docker volume prune -f
docker network prune -f
docker rm -f $(docker ps -aq)
docker rmi -f $(docker images -q)
```

---

## 🎯 Quick Commands (Copy-Paste)

```bash
# === SAFE CLEANUP FORECAST ONLY ===

cd /opt/forecast

# Stop & remove containers
docker compose down
docker rm forecast_frontend forecast_backend forecast_celery_worker forecast_postgres forecast_redis 2>/dev/null || true

# Remove images
docker rmi forecast-frontend forecast-backend forecast-celery_worker 2>/dev/null || true

# Remove volumes
docker volume rm forecast_postgres_data forecast_redis_data 2>/dev/null || true

# Remove network
docker network rm forecast_forecast_network 2>/dev/null || true

# Verify
echo "=== VERIFICATION ==="
docker ps -a | grep forecast || echo "✅ No forecast containers"
docker images | grep forecast || echo "✅ No forecast images"
docker volume ls | grep forecast || echo "✅ No forecast volumes"
docker network ls | grep forecast || echo "✅ No forecast networks"

echo "🎉 Forecast cleanup completed! Other Docker services are safe."
```

---

## 📊 Before vs After

**Before cleanup:**
```bash
docker ps -a
# forecast_frontend, forecast_backend, other_containers...

docker images
# forecast-frontend, forecast-backend, other_images...
```

**After cleanup:**
```bash
docker ps -a
# other_containers... (forecast containers gone)

docker images
# other_images... (forecast images gone)
```

---

## ✅ Safety Checklist

- [ ] Hanya container dengan nama `forecast_*` yang dihapus
- [ ] Hanya image dengan nama `forecast-*` yang dihapus
- [ ] Hanya volume dengan nama `forecast_*` yang dihapus
- [ ] Hanya network dengan nama `forecast_*` yang dihapus
- [ ] Container/image/volume/network lain masih ada
- [ ] Docker daemon masih running
- [ ] Other services tidak terpengaruh

---

**Safe cleanup completed!** 🎉 Docker lain aman, hanya forecast yang terhapus.
