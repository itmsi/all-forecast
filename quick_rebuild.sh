#!/bin/bash

# ===============================================
# ⚡ QUICK REBUILD SCRIPT
# ===============================================

echo "⚡ Quick rebuild starting..."

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Rebuild backend
echo "🔧 Rebuilding backend..."
docker-compose build --no-cache backend

# Rebuild frontend  
echo "🔧 Rebuilding frontend..."
docker-compose build --no-cache frontend

# Restart services
echo "🚀 Restarting services..."
docker-compose up -d

echo "✅ Quick rebuild completed!"
echo "🔍 Check status: docker-compose ps"
