# Demand Forecasting System

Sistem forecasting demand berbasis Machine Learning dengan web interface untuk memprediksi kebutuhan (demand) berdasarkan data historis.

## 🎯 Fitur Utama

- **Web-based Interface**: UI modern dengan React + Ant Design
- **Machine Learning**: Multiple models (Random Forest, Extra Trees, Gradient Boosting, Ridge)
- **Async Processing**: Background jobs dengan Celery untuk handling concurrent users
- **Real-time Status**: Progress tracking dengan polling
- **History Management**: Lihat dan kelola riwayat forecast
- **Docker Deployment**: Easy deployment dengan Docker Compose
- **Production-Ready**: PostgreSQL, Redis, optimized for 10+ concurrent users

## 🏗️ Arsitektur

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI    │─────▶│ PostgreSQL  │
│  Frontend   │      │   Backend    │      │             │
└─────────────┘      └──────┬───────┘      └─────────────┘
                            │
                     ┌──────┴───────┐
                     │              │
                ┌────▼────┐    ┌────▼─────┐
                │ Celery  │    │  Redis   │
                │ Worker  │    │          │
                └─────────┘    └──────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- (Opsional) Python 3.9+ untuk development
- (Opsional) Node.js 18+ untuk development

## 🚀 Quick Start (Production Deployment)

### 1. Clone Repository

```bash
cd /path/to/your/server
git clone <repository-url>
cd forecast
```

### 2. Setup Environment Variables

```bash
cp .env.example .env
nano .env  # Edit dan sesuaikan DB_PASSWORD
```

### 3. Build & Run dengan Docker Compose

```bash
# Build semua services
docker-compose build

# Start semua services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Akses Aplikasi

- **Frontend**: http://localhost (atau http://server-ip)
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

### 5. Stop Services

```bash
docker-compose down

# Untuk hapus volumes juga (WARNING: hapus data!)
docker-compose down -v
```

## 📖 User Guide

### Upload Data

1. Buka halaman Dashboard
2. Klik atau drag file CSV ke upload area
3. File harus berisi kolom: `date`, `partnumber`, `site_code`, `demand_qty`

### Konfigurasi Forecast

- **Forecast Horizon**: Jumlah hari ke depan (1-90 hari)
- **Site Codes**: Kosongkan untuk semua site, atau masukkan kode site spesifik
- **Zero Threshold**: Prediksi < nilai ini akan di-set ke 0
- **Rounding Mode**: Metode pembulatan hasil
- **Format Tanggal**: Day-first (DD/MM/YYYY) atau Month-first (MM/DD/YYYY)

### Menjalankan Forecast

1. Upload CSV data
2. Atur konfigurasi
3. Klik "Jalankan Forecast"
4. Tunggu proses selesai (progress bar akan update otomatis)
5. Download hasil CSV

### Melihat Riwayat

1. Klik menu "Riwayat"
2. Filter by status jika diperlukan
3. Download hasil dari forecast sebelumnya
4. Hapus job yang sudah tidak diperlukan

## 🛠️ Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
export DATABASE_URL="postgresql://forecast_user:password@localhost:5432/forecast_db"
export CELERY_BROKER_URL="redis://localhost:6379/0"

# Run FastAPI
uvicorn app.main:app --reload

# Run Celery worker (terminal baru)
celery -A app.celery_app worker --loglevel=info
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm run build
```

## 🔧 Configuration

### Docker Compose Environment Variables

Edit `docker-compose.yml` atau `.env`:

- `DB_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user

### Backend Configuration

File: `backend/app/core/ml_engine.py`

- Model parameters (n_estimators, max_depth, dll)
- Feature engineering settings
- Training/validation split

### Frontend Configuration

File: `frontend/src/services/api.js`

- `API_BASE_URL`: Backend API URL

## 📊 API Endpoints

### Forecast Endpoints

- `POST /api/forecast/submit` - Submit forecast job
- `GET /api/forecast/status/{task_id}` - Get status by task ID
- `GET /api/forecast/status/job/{job_id}` - Get status by job ID
- `GET /api/forecast/download/{job_id}` - Download result CSV
- `GET /api/forecast/history` - Get forecast history
- `DELETE /api/forecast/{job_id}` - Delete forecast job

### Utility Endpoints

- `GET /api/health` - Health check
- `GET /api/docs` - API documentation (Swagger UI)

## 🔐 Security Notes

### Internal Network Deployment

Untuk deployment internal:

1. **Firewall**: Pastikan port 80 (frontend) dan 8000 (API) hanya accessible dari internal network
2. **Database**: PostgreSQL tidak perlu exposed ke luar (hanya antar-container)
3. **Environment Variables**: Jangan commit `.env` ke git

### Future: SSO Integration

Backend sudah siap untuk SSO integration:

- Database model `ForecastJob` memiliki field `created_by`
- Tinggal tambahkan middleware authentication di `backend/app/main.py`
- Frontend tinggal tambahkan token handling di `frontend/src/services/api.js`

## 📦 Data Backup

### Backup Database

```bash
# Backup PostgreSQL
docker exec forecast_postgres pg_dump -U forecast_user forecast_db > backup.sql

# Restore
docker exec -i forecast_postgres psql -U forecast_user forecast_db < backup.sql
```

### Backup Files

```bash
# Backup models, uploads, outputs
tar -czf forecast_data_backup.tar.gz backend/models backend/uploads backend/outputs
```

## 🐛 Troubleshooting

### Service tidak start

```bash
# Check logs
docker-compose logs backend
docker-compose logs celery_worker

# Restart specific service
docker-compose restart backend
```

### Database connection error

```bash
# Check PostgreSQL
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Celery worker tidak process job

```bash
# Check Celery logs
docker-compose logs celery_worker

# Check Redis
docker-compose exec redis redis-cli ping
```

### Frontend tidak bisa connect ke backend

- Check `frontend/nginx.conf` proxy settings
- Check CORS settings di `backend/app/main.py`
- Check network settings di `docker-compose.yml`

## 📈 Performance Tuning

### Untuk Large Data

1. **Celery concurrency**: Edit `docker-compose.yml`, ubah `--concurrency=4` sesuai CPU
2. **Database connection pool**: Edit `backend/app/database.py`, sesuaikan `pool_size`
3. **Nginx worker**: Edit `frontend/nginx.conf`, tambahkan `worker_processes`

### Untuk Many Users

1. **Backend workers**: Edit `docker-compose.yml`, ubah `--workers 2` di backend
2. **Celery workers**: Scale dengan `docker-compose up -d --scale celery_worker=3`
3. **Redis memory**: Tambahkan `maxmemory` di Redis config

## 📝 Version History

- **v1.0.0** (2025-10) - Initial release
  - Multi-model forecasting
  - Web interface
  - Docker deployment
  - Async processing

## 👥 Support

Untuk pertanyaan atau issues, hubungi tim internal atau buat issue di repository ini.

## 📄 License

Internal use only - Proprietary

