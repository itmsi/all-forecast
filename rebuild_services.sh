#!/bin/bash

# ===============================================
# 🔄 SCRIPT REBUILD BACKEND & FRONTEND
# ===============================================
# Script untuk rebuild ulang semua services
# dengan konfigurasi terbaru (CORS fix)

echo "🚀 Starting rebuild process..."
echo "=================================="

# 1. Stop semua services
echo "🛑 Step 1: Stopping all services..."
docker-compose down

# 2. Pull perubahan terbaru dari git
echo "📥 Step 2: Pulling latest changes from git..."
git pull origin main

# 3. Build backend (untuk memastikan semua perubahan terupdate)
echo "🔧 Step 3: Building backend..."
docker-compose build --no-cache backend

# 4. Build frontend (untuk update nginx.conf)
echo "🔧 Step 4: Building frontend..."
docker-compose build --no-cache frontend

# 5. Start semua services
echo "🚀 Step 5: Starting all services..."
docker-compose up -d

# 6. Tunggu services ready
echo "⏳ Step 6: Waiting for services to be ready..."
sleep 15

# 7. Check status services
echo "🔍 Step 7: Checking services status..."
docker-compose ps

# 8. Check logs untuk memastikan tidak ada error
echo "📋 Step 8: Checking logs..."
echo ""
echo "=== BACKEND LOGS ==="
docker logs forecast_backend --tail 10

echo ""
echo "=== FRONTEND LOGS ==="
docker logs forecast_frontend --tail 10

echo ""
echo "✅ Rebuild process completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Test frontend: https://forecast.motorsights.com"
echo "2. Test API: https://api-forecast.motorsights.com/api/health"
echo "3. Check browser DevTools Network tab for CORS"
echo ""
echo "📊 Service URLs:"
echo "- Frontend: https://forecast.motorsights.com"
echo "- Backend API: https://api-forecast.motorsights.com"
echo "- Health Check: https://api-forecast.motorsights.com/api/health"
