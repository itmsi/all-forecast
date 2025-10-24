#!/bin/bash

# ===============================================
# 🔧 FIX FRONTEND BUILD
# ===============================================
# Script untuk memperbaiki build frontend

echo "🔧 Fixing frontend build..."
echo "=========================="

# 1. Stop frontend
echo "🛑 Step 1: Stopping frontend..."
docker-compose stop frontend

# 2. Remove old containers and images
echo "🧹 Step 2: Cleaning up..."
docker rm forecast_frontend 2>/dev/null || true
docker rmi forecast-frontend 2>/dev/null || true

# 3. Pull latest changes
echo "📥 Step 3: Pulling latest changes..."
git pull origin main

# 4. Build frontend with simple approach
echo "🔧 Step 4: Building frontend (simple approach)..."
echo "   - Using npm install instead of npm ci"
echo "   - Memory optimization enabled"
echo "   - This may take 5-10 minutes..."

# Build dengan approach yang lebih sederhana
docker-compose build --no-cache frontend

# 5. Start frontend
echo "🚀 Step 5: Starting frontend..."
docker-compose up -d frontend

# 6. Wait and check
echo "⏳ Step 6: Waiting for frontend to be ready..."
sleep 20

echo "🔍 Step 7: Checking frontend status..."
docker-compose ps frontend

echo "✅ Frontend build completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Check logs: docker logs forecast_frontend"
echo "2. Test frontend: https://forecast.motorsights.com"
echo "3. Check CORS in browser DevTools"
