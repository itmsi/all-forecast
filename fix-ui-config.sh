#!/bin/bash
# Script untuk memperbaiki konfigurasi UI di server

echo "🔧 Fixing UI Configuration..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ File .env tidak ditemukan!"
    echo "📝 Membuat file .env..."
    cat > .env << EOF
# Environment Variables untuk Forecast System
DB_PASSWORD=forecast_secure_password_123
REACT_APP_API_URL=http://$(hostname -I | awk '{print $1}'):9571
EOF
    echo "✅ File .env dibuat dengan IP server: $(hostname -I | awk '{print $1}')"
else
    echo "✅ File .env sudah ada"
fi

# Show current configuration
echo "📋 Current configuration:"
echo "REACT_APP_API_URL=$(grep REACT_APP_API_URL .env | cut -d'=' -f2)"

# Stop services
echo "🛑 Stopping services..."
docker compose down

# Rebuild frontend with correct API URL
echo "🔨 Rebuilding frontend..."
docker compose build frontend --no-cache

# Start services
echo "🚀 Starting services..."
docker compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check status
echo "✅ Checking status..."
docker compose ps

# Test API URL
echo "🔍 Testing API URL..."
API_URL=$(grep REACT_APP_API_URL .env | cut -d'=' -f2)
echo "API URL: $API_URL"
curl -s "$API_URL/api/health" && echo "✅ API accessible" || echo "❌ API not accessible"

echo "🎉 Fix completed!"
echo "🌐 Frontend: http://$(hostname -I | awk '{print $1}'):9572"
echo "📚 API: $API_URL"
