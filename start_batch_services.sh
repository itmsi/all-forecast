#!/bin/bash

# Script untuk start semua services yang dibutuhkan batch forecast
# Usage: ./start_batch_services.sh

echo "🚀 Starting Batch Forecast Services..."
echo ""

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis not found. Please install Redis:"
    echo "   brew install redis"
    exit 1
fi

# Check if Redis is already running
if redis-cli ping &> /dev/null; then
    echo "✅ Redis already running"
else
    echo "🔄 Starting Redis..."
    redis-server --daemonize yes
    sleep 2
    
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis started successfully"
    else
        echo "❌ Failed to start Redis"
        exit 1
    fi
fi

echo ""
echo "📝 Next steps:"
echo ""
echo "1. Start Backend API (Terminal 1):"
echo "   cd backend"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "2. Start Celery Worker (Terminal 2):"
echo "   cd backend"
echo "   celery -A app.celery_app worker --loglevel=info"
echo ""
echo "3. Verify services:"
echo "   curl http://localhost:8000/api/health"
echo "   (Check that celery: \"ok\")"
echo ""
echo "4. Start Frontend (Terminal 3 - optional):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "✅ Redis is ready. Now start Backend and Celery worker in separate terminals."

