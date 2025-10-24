#!/bin/bash

# ===============================================
# 🔧 REBUILD WITH MEMORY FIX
# ===============================================
# Script untuk rebuild dengan optimasi memory

echo "🔧 Starting rebuild with memory optimization..."
echo "=============================================="

# 1. Stop services
echo "🛑 Step 1: Stopping services..."
docker-compose down

# 2. Pull latest changes
echo "📥 Step 2: Pulling latest changes..."
git pull origin main

# 3. Clean up old images and containers
echo "🧹 Step 3: Cleaning up old images..."
docker system prune -f
docker image prune -f

# 4. Build backend first (lighter)
echo "🔧 Step 4: Building backend..."
docker-compose build --no-cache backend

# 5. Build frontend with memory optimization
echo "🔧 Step 5: Building frontend (with memory optimization)..."
echo "   - Setting memory limit..."
echo "   - Using optimized Dockerfile..."

# Set memory limit untuk build process
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

# Build frontend dengan memory limit
docker-compose build --no-cache --memory=2g frontend

# 6. Start services
echo "🚀 Step 6: Starting services..."
docker-compose up -d

# 7. Wait for services
echo "⏳ Step 7: Waiting for services to be ready..."
sleep 20

# 8. Check status
echo "🔍 Step 8: Checking services status..."
docker-compose ps

echo "✅ Rebuild with memory optimization completed!"
echo ""
echo "🎯 If build still fails, try:"
echo "1. Increase server memory"
echo "2. Use: docker-compose build --no-cache --memory=4g frontend"
echo "3. Or build locally and push image"
