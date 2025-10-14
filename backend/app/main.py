# backend/app/main.py
"""
Main FastAPI application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

from app.database import init_db, engine
from app.models import Base
from app.api.forecast import router as forecast_router
from app.api.batch import router as batch_router
from app.schemas import HealthCheckResponse, ErrorResponse
from app import __version__

# Create FastAPI app
app = FastAPI(
    title="Demand Forecast API",
    description="API untuk forecasting demand menggunakan Machine Learning",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware - untuk allow requests dari React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost",
        "http://localhost:80",
        "*"  # Allow all origins untuk internal network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized")
    
    # Create required directories
    for directory in ['uploads', 'outputs', 'models']:
        os.makedirs(directory, exist_ok=True)
    print("Required directories created")


# Health check endpoint
@app.get("/api/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns status of API, database, and Celery
    """
    
    # Check database
    db_status = "ok"
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check Celery
    celery_status = "ok"
    try:
        from app.celery_app import celery_app
        # Ping Celery workers
        result = celery_app.control.ping(timeout=1.0)
        if not result:
            celery_status = "no workers available"
    except Exception as e:
        celery_status = f"error: {str(e)}"
    
    return HealthCheckResponse(
        status="ok",
        timestamp=datetime.utcnow(),
        database=db_status,
        celery=celery_status,
        version=__version__
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Demand Forecast API",
        "version": __version__,
        "docs": "/api/docs",
        "health": "/api/health"
    }


# Include routers
app.include_router(forecast_router)
app.include_router(batch_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

