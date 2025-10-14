# backend/app/api/batch.py
"""
Batch forecast API endpoints with auto-partitioning
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json
import shutil
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from app.database import get_db
from app.models import BatchJob
from app.schemas import ForecastConfig
from app.tasks.batch_task import run_batch_forecast_task
from app.core.batch_processor import BatchProcessor
from app.core.preprocessing import load_and_normalize

router = APIRouter(prefix="/api/batch", tags=["Batch Forecast"])


@router.post("/submit")
async def submit_batch_forecast(
    file: UploadFile = File(..., description="CSV file with demand data"),
    config: str = Form(..., description="JSON config for forecast"),
    partition_strategy: str = Form(default='site', description="Partition strategy: 'site' or 'auto'"),
    max_rows_per_partition: int = Form(default=2000, description="Max rows per partition"),
    max_execution_time: int = Form(default=300, description="Max execution time per partition (seconds)"),
    db: Session = Depends(get_db)
):
    """
    Submit batch forecast dengan auto-partitioning
    
    Features:
    - Auto partition data by site atau size
    - Parallel/sequential processing
    - Progress tracking per partition
    - Auto rollback if any partition fails
    - Timeout monitoring
    
    Returns:
        batch_id: Unique batch identifier
        total_partitions: Number of partitions
        estimated_time: Estimated completion time
    """
    
    # Validate file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    # Parse config
    try:
        config_dict = json.loads(config)
        forecast_config = ForecastConfig(**config_dict)
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
    
    # Analyze data untuk partition planning
    try:
        df = load_and_normalize(str(file_path), dayfirst=forecast_config.dayfirst)
        
        processor = BatchProcessor(
            max_rows_per_job=max_rows_per_partition,
            partition_by=partition_strategy,
            max_partitions=20
        )
        
        analysis = processor.analyze_data(df)
        partitions = processor.create_partitions(df)
        time_estimate = processor.estimate_processing_time(partitions)
        
    except Exception as e:
        # Cleanup file if analysis fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail=f"Data analysis failed: {str(e)}")
    
    # Create batch job record
    batch_id = str(uuid4())
    
    batch_job = BatchJob(
        batch_id=batch_id,
        original_filename=file.filename,
        original_file_path=str(file_path),
        config=forecast_config.dict(),
        partition_strategy=partition_strategy,
        total_partitions=len(partitions),
        max_execution_time=max_execution_time,
        status='QUEUED',
        progress=0
    )
    
    db.add(batch_job)
    db.commit()
    db.refresh(batch_job)
    
    # Submit to Celery
    try:
        task = run_batch_forecast_task.delay(batch_id)
        
        return {
            "batch_id": batch_id,
            "batch_job_id": batch_job.id,
            "task_id": task.id,
            "status": "QUEUED",
            "message": "Batch forecast submitted successfully",
            "analysis": {
                "total_rows": analysis['total_rows'],
                "unique_sites": analysis['unique_sites'],
                "unique_partnumbers": analysis['unique_partnumbers'],
                "total_partitions": len(partitions),
                "partition_strategy": partition_strategy,
                "estimated_time_seconds": time_estimate['parallel_total_seconds'],
                "estimated_time_minutes": round(time_estimate['parallel_total_seconds'] / 60, 1),
                "speedup_factor": time_estimate['speedup_factor']
            }
        }
    except Exception as e:
        batch_job.status = 'FAILED'
        batch_job.error_message = f"Failed to queue: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{batch_id}")
async def get_batch_status(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    Get batch job status dengan detail per partition
    
    Returns:
        - Overall status & progress
        - Status per partition
        - Failed/stuck partitions
        - Execution time per partition
    """
    
    batch_job = db.query(BatchJob).filter_by(batch_id=batch_id).first()
    
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    return {
        "batch_id": batch_id,
        "batch_job_id": batch_job.id,
        "status": batch_job.status,
        "progress": batch_job.progress,
        "total_partitions": batch_job.total_partitions,
        "completed_partitions": batch_job.completed_partitions,
        "failed_partitions": batch_job.failed_partitions,
        "partition_results": batch_job.partition_results,
        "created_at": batch_job.created_at.isoformat() if batch_job.created_at else None,
        "started_at": batch_job.started_at.isoformat() if batch_job.started_at else None,
        "completed_at": batch_job.completed_at.isoformat() if batch_job.completed_at else None,
        "error_message": batch_job.error_message,
        "combined_output": batch_job.combined_output
    }


@router.get("/download/{batch_id}")
async def download_batch_result(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Download combined batch forecast result"""
    
    batch_job = db.query(BatchJob).filter_by(batch_id=batch_id).first()
    
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    if batch_job.status != 'COMPLETED':
        raise HTTPException(
            status_code=400,
            detail=f"Batch not completed. Current status: {batch_job.status}"
        )
    
    if not batch_job.combined_output or not Path(batch_job.combined_output).exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        path=batch_job.combined_output,
        media_type='text/csv',
        filename=f'batch_forecast_{batch_id}_{datetime.now().strftime("%Y%m%d")}.csv',
        headers={
            "Content-Disposition": f'attachment; filename="batch_forecast_{batch_id}.csv"'
        }
    )


@router.post("/cancel/{batch_id}")
async def cancel_batch_job(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """Cancel running batch job"""
    
    batch_job = db.query(BatchJob).filter_by(batch_id=batch_id).first()
    
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    if batch_job.status not in ['QUEUED', 'PROCESSING']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel batch with status: {batch_job.status}"
        )
    
    # Update status
    batch_job.status = 'CANCELLED'
    batch_job.error_message = 'Cancelled by user'
    batch_job.completed_at = datetime.utcnow()
    db.commit()
    
    # Note: Actual Celery task termination handled in task itself
    
    return {
        "message": f"Batch {batch_id} cancelled",
        "batch_id": batch_id,
        "status": "CANCELLED"
    }


@router.get("/history")
async def get_batch_history(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Get batch job history"""
    
    query = db.query(BatchJob)
    total = query.count()
    
    skip = (page - 1) * page_size
    jobs = (query.order_by(BatchJob.created_at.desc())
            .offset(skip)
            .limit(page_size)
            .all())
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "jobs": [job.to_dict() for job in jobs]
    }

