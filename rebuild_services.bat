@echo off
REM ===============================================
REM 🔄 REBUILD SERVICES SCRIPT (Windows)
REM ===============================================

echo 🚀 Starting rebuild process...
echo ==================================

REM 1. Stop semua services
echo 🛑 Step 1: Stopping all services...
docker-compose down

REM 2. Pull perubahan terbaru dari git
echo 📥 Step 2: Pulling latest changes from git...
git pull origin main

REM 3. Build backend
echo 🔧 Step 3: Building backend...
docker-compose build --no-cache backend

REM 4. Build frontend
echo 🔧 Step 4: Building frontend...
docker-compose build --no-cache frontend

REM 5. Start semua services
echo 🚀 Step 5: Starting all services...
docker-compose up -d

REM 6. Tunggu services ready
echo ⏳ Step 6: Waiting for services to be ready...
timeout /t 15 /nobreak

REM 7. Check status services
echo 🔍 Step 7: Checking services status...
docker-compose ps

echo ✅ Rebuild process completed!
echo.
echo 🎯 Next steps:
echo 1. Test frontend: https://forecast.motorsights.com
echo 2. Test API: https://api-forecast.motorsights.com/api/health
echo 3. Check browser DevTools Network tab for CORS

pause
