#!/bin/bash

# Script untuk check status semua services batch forecast
# Usage: ./check_batch_status.sh

echo "🔍 Checking Batch Forecast Services Status..."
echo ""

# Check Redis
echo "1️⃣  Redis Status:"
if redis-cli ping &> /dev/null; then
    echo "   ✅ Redis is running"
else
    echo "   ❌ Redis is NOT running"
    echo "   Start with: redis-server"
fi
echo ""

# Check Backend API
echo "2️⃣  Backend API Status:"
if curl -s http://localhost:8000/api/health &> /dev/null; then
    echo "   ✅ Backend API is running"
    
    # Check Celery status from health endpoint
    CELERY_STATUS=$(curl -s http://localhost:8000/api/health | grep -o '"celery":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$CELERY_STATUS" = "ok" ]; then
        echo "   ✅ Celery worker is connected"
    else
        echo "   ❌ Celery worker is NOT connected: $CELERY_STATUS"
        echo "   Start with: celery -A app.celery_app worker --loglevel=info"
    fi
else
    echo "   ❌ Backend API is NOT running"
    echo "   Start with: cd backend && uvicorn app.main:app --reload --port 8000"
fi
echo ""

# Check Frontend (optional)
echo "3️⃣  Frontend Status:"
if curl -s http://localhost:3000 &> /dev/null; then
    echo "   ✅ Frontend is running"
else
    echo "   ⚠️  Frontend is NOT running (optional)"
    echo "   Start with: cd frontend && npm start"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo ""

REDIS_OK=$(redis-cli ping &> /dev/null && echo "1" || echo "0")
API_OK=$(curl -s http://localhost:8000/api/health &> /dev/null && echo "1" || echo "0")
CELERY_STATUS=$(curl -s http://localhost:8000/api/health 2>/dev/null | grep -o '"celery":"[^"]*"' | cut -d'"' -f4)
CELERY_OK=$([ "$CELERY_STATUS" = "ok" ] && echo "1" || echo "0")

if [ "$REDIS_OK" = "1" ] && [ "$API_OK" = "1" ] && [ "$CELERY_OK" = "1" ]; then
    echo "✅ All services ready for BATCH forecast!"
    echo ""
    echo "You can now:"
    echo "  - Submit batch jobs via API or Frontend"
    echo "  - Monitor progress in Celery worker terminal"
    echo ""
    echo "API Docs: http://localhost:8000/api/docs"
    echo "Frontend: http://localhost:3000"
else
    echo "❌ Some services are not ready:"
    [ "$REDIS_OK" = "0" ] && echo "  - Start Redis"
    [ "$API_OK" = "0" ] && echo "  - Start Backend API"
    [ "$CELERY_OK" = "0" ] && echo "  - Start Celery Worker"
    echo ""
    echo "See BATCH_TROUBLESHOOTING.md for detailed instructions"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

