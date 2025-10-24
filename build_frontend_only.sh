#!/bin/bash

# ===============================================
# 🔧 BUILD FRONTEND ONLY (Memory Optimized)
# ===============================================

echo "🔧 Building frontend only with memory optimization..."
echo "====================================================="

# 1. Stop frontend service
echo "🛑 Step 1: Stopping frontend service..."
docker-compose stop frontend

# 2. Remove old frontend container and image
echo "🧹 Step 2: Cleaning up old frontend..."
docker rm forecast_frontend 2>/dev/null || true
docker rmi forecast-frontend 2>/dev/null || true

# 3. Set memory optimization environment
echo "🔧 Step 3: Setting memory optimization..."
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

# 4. Build frontend with memory limit
echo "🔧 Step 4: Building frontend (this may take 5-10 minutes)..."
echo "   - Memory limit: 2GB"
echo "   - Node.js memory: 2GB"
echo "   - Optimized build process..."

# Try build dengan memory limit
docker-compose build --no-cache --memory=2g frontend

# 5. Start frontend
echo "🚀 Step 5: Starting frontend..."
docker-compose up -d frontend

# 6. Wait and check
echo "⏳ Step 6: Waiting for frontend to be ready..."
sleep 15

echo "🔍 Step 7: Checking frontend status..."
docker-compose ps frontend

echo "✅ Frontend build completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Check logs: docker logs forecast_frontend"
echo "2. Test frontend: https://forecast.motorsights.com"
echo "3. Check CORS in browser DevTools"
