# backend/app/api/forecast.py
"""
Forecast API endpoints
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import json
import shutil
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from app.database import get_db
from app.models import ForecastJob
from app.schemas import (
    ForecastConfig,
    ForecastResponse,
    ForecastStatusResponse,
    ForecastHistoryResponse
)
from app.tasks.forecast_task import run_forecast_task
from app.celery_app import celery_app

router = APIRouter(prefix="/api/forecast", tags=["Forecast"])


@router.post("/submit", response_model=ForecastResponse)
async def submit_forecast(
    file: UploadFile = File(..., description="CSV file with demand data"),
    config: str = Form(..., description="JSON config for forecast"),
    db: Session = Depends(get_db)
):
    """
    Submit a new forecast job
    
    - **file**: CSV file containing historical demand data
    - **config**: JSON configuration for the forecast
    
    Returns job_id and task_id for status tracking
    """
    
    # Validate file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Parse config
    try:
        config_dict = json.loads(config)
        forecast_config = ForecastConfig(**config_dict)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON config")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid config: {str(e)}")
    
    # Save uploaded file
    file_id = str(uuid4())
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{file_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create job record
    job = ForecastJob(
        filename=file.filename,
        file_path=str(file_path),
        config=forecast_config.dict(),
        status='QUEUED',
        progress=0
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Submit to Celery
    try:
        task = run_forecast_task.delay(job.id)
        
        # Update task_id
        job.task_id = task.id
        db.commit()
        
        return ForecastResponse(
            job_id=job.id,
            task_id=task.id,
            status='QUEUED',
            message="Forecast job submitted successfully"
        )
    except Exception as e:
        job.status = 'FAILED'
        job.error_message = f"Failed to queue task: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=ForecastStatusResponse)
async def get_forecast_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Get forecast job status by task_id
    
    Returns current status, progress, and metrics (if completed)
    """
    
    job = db.query(ForecastJob).filter_by(task_id=task_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get Celery task state
    task = celery_app.AsyncResult(task_id)
    
    # Update progress from Celery if task is running
    if task.state == 'PROGRESS' and task.info:
        job.progress = task.info.get('progress', job.progress)
    
    return ForecastStatusResponse(
        job_id=job.id,
        task_id=job.task_id,
        status=job.status,
        progress=job.progress,
        filename=job.filename,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        metrics=job.metrics,
        error_message=job.error_message
    )


@router.get("/status/job/{job_id}", response_model=ForecastStatusResponse)
async def get_forecast_status_by_job_id(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get forecast job status by job_id
    """
    
    job = db.query(ForecastJob).filter_by(id=job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ForecastStatusResponse(
        job_id=job.id,
        task_id=job.task_id,
        status=job.status,
        progress=job.progress,
        filename=job.filename,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        metrics=job.metrics,
        error_message=job.error_message
    )


@router.get("/download/{job_id}")
async def download_forecast_result(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Download forecast result CSV file
    
    Only available for completed jobs
    """
    
    job = db.query(ForecastJob).filter_by(id=job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != 'COMPLETED':
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job.status}"
        )
    
    if not job.output_file or not Path(job.output_file).exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        path=job.output_file,
        media_type='text/csv',
        filename=f'forecast_result_{job_id}_{datetime.now().strftime("%Y%m%d")}.csv',
        headers={
            "Content-Disposition": f'attachment; filename="forecast_result_{job_id}.csv"'
        }
    )


@router.get("/history", response_model=ForecastHistoryResponse)
async def get_forecast_history(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get forecast job history
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of jobs per page
    - **status**: Filter by status (QUEUED, PROCESSING, COMPLETED, FAILED)
    """
    
    # Build query
    query = db.query(ForecastJob)
    
    if status:
        query = query.filter(ForecastJob.status == status.upper())
    
    # Get total count
    total = query.count()
    
    # Paginate
    skip = (page - 1) * page_size
    jobs = (query.order_by(ForecastJob.created_at.desc())
            .offset(skip)
            .limit(page_size)
            .all())
    
    return ForecastHistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        jobs=[job.to_dict() for job in jobs]
    )


@router.post("/cancel/{job_id}")
async def cancel_forecast_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancel/Stop a running forecast job
    
    Can cancel QUEUED or PROCESSING jobs
    """
    
    job = db.query(ForecastJob).filter_by(id=job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in ['QUEUED', 'PROCESSING']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Revoke Celery task if exists
    if job.task_id:
        try:
            celery_app.control.revoke(job.task_id, terminate=True, signal='SIGKILL')
            print(f"Celery task {job.task_id} terminated")
        except Exception as e:
            print(f"Error terminating Celery task: {e}")
    
    # Update job status
    job.status = 'CANCELLED'
    job.error_message = 'Cancelled by user'
    job.completed_at = datetime.utcnow()
    job.progress = 0
    db.commit()
    
    return {
        "message": f"Job {job_id} cancelled successfully",
        "job_id": job_id,
        "status": "CANCELLED"
    }


@router.delete("/{job_id}")
async def delete_forecast_job(
    job_id: int,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete a forecast job and its files
    
    - **force**: If True, can delete even QUEUED/PROCESSING jobs (will terminate them)
    - Without force: Can only delete COMPLETED, FAILED, or CANCELLED jobs
    """
    
    job = db.query(ForecastJob).filter_by(id=job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if force delete needed
    if job.status in ['QUEUED', 'PROCESSING'] and not force:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete job with status: {job.status}. Use force=true to force delete."
        )
    
    # If force delete and job is running, terminate it first
    if job.status in ['QUEUED', 'PROCESSING'] and force:
        if job.task_id:
            try:
                celery_app.control.revoke(job.task_id, terminate=True, signal='SIGKILL')
                print(f"Force terminated Celery task {job.task_id}")
            except Exception as e:
                print(f"Error terminating task: {e}")
    
    # Delete files
    try:
        if job.file_path and Path(job.file_path).exists():
            Path(job.file_path).unlink()
            print(f"Deleted file: {job.file_path}")
        
        if job.output_file and Path(job.output_file).exists():
            Path(job.output_file).unlink()
            print(f"Deleted output: {job.output_file}")
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    # Delete from database
    db.delete(job)
    db.commit()
    
    return {
        "message": f"Job {job_id} deleted successfully",
        "force": force
    }

