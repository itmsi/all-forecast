# backend/app/tasks/forecast_task.py
"""
Celery tasks for forecasting
"""

from celery import Task
from datetime import datetime
import traceback
import pandas as pd
from pathlib import Path

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import ForecastJob
from app.core.ml_engine import MLForecaster
from app.core.preprocessing import load_and_normalize, preprocess_data, prepare_features
from app.core.utils import safe_save_csv


class ForecastTask(Task):
    """Base task with error handling"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        job_id = args[0] if args else None
        if job_id:
            db = SessionLocal()
            try:
                job = db.query(ForecastJob).filter_by(id=job_id).first()
                if job:
                    job.status = 'FAILED'
                    job.error_message = str(exc)
                    job.completed_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()


@celery_app.task(base=ForecastTask, bind=True, name='forecast.run_forecast')
def run_forecast_task(self, job_id: int):
    """
    Main forecast task
    
    Args:
        job_id: Database ID of the forecast job
    """
    db = SessionLocal()
    
    try:
        # Get job
        job = db.query(ForecastJob).filter_by(id=job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Update status
        job.status = 'PROCESSING'
        job.started_at = datetime.utcnow()
        job.progress = 5
        db.commit()
        
        print(f"[Job {job_id}] Starting forecast task")
        self.update_state(state='PROGRESS', meta={'progress': 5, 'status': 'Loading data'})
        
        # Load and normalize data
        print(f"[Job {job_id}] Loading data from {job.file_path}")
        df = load_and_normalize(job.file_path, dayfirst=job.config.get('dayfirst', True))
        
        job.progress = 15
        db.commit()
        self.update_state(state='PROGRESS', meta={'progress': 15, 'status': 'Preprocessing data'})
        
        # Preprocess
        print(f"[Job {job_id}] Preprocessing data")
        df_processed = preprocess_data(df)
        
        job.progress = 25
        db.commit()
        self.update_state(state='PROGRESS', meta={'progress': 25, 'status': 'Feature engineering'})
        
        # Prepare features
        print(f"[Job {job_id}] Preparing features")
        df_fe = prepare_features(df_processed, group_cols=['partnumber', 'site_code'])
        
        job.progress = 35
        db.commit()
        self.update_state(state='PROGRESS', meta={'progress': 35, 'status': 'Loading/training model'})
        
        # Initialize forecaster
        print(f"[Job {job_id}] Initializing forecaster")
        forecaster = MLForecaster(job.config)
        
        # Check if model exists, otherwise train
        model_path = Path('models/best_model.pkl')
        if model_path.exists():
            print(f"[Job {job_id}] Loading existing model")
            forecaster.load_model(str(model_path))
            job.progress = 50
        else:
            print(f"[Job {job_id}] Training new model")
            forecaster.train_and_select_model(df_fe)
            forecaster.save_model(str(model_path))
            job.progress = 60
        
        db.commit()
        self.update_state(state='PROGRESS', meta={'progress': job.progress, 'status': 'Generating forecast'})
        
        # Generate forecast
        print(f"[Job {job_id}] Generating forecast")
        forecast_df = forecaster.forecast(
            df_processed,
            start_date=job.config.get('forecast_start_date'),
            start_offset_days=job.config.get('forecast_start_offset_days', 1)
        )
        
        job.progress = 85
        db.commit()
        self.update_state(state='PROGRESS', meta={'progress': 85, 'status': 'Saving results'})
        
        # Save results
        print(f"[Job {job_id}] Saving results")
        output_path = f"outputs/forecast_job_{job_id}.csv"
        saved_path = safe_save_csv(forecast_df, output_path)
        
        # Get metrics
        metrics = forecaster.get_metrics()
        
        # Update job
        job.status = 'COMPLETED'
        job.progress = 100
        job.output_file = saved_path
        job.metrics = metrics
        job.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"[Job {job_id}] Forecast completed successfully")
        
        return {
            'status': 'success',
            'job_id': job_id,
            'output_file': saved_path,
            'metrics': metrics
        }
        
    except Exception as e:
        print(f"[Job {job_id}] Error: {str(e)}")
        print(traceback.format_exc())
        
        job.status = 'FAILED'
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        raise
        
    finally:
        db.close()


@celery_app.task(name='forecast.train_model')
def train_model_task(file_path: str, config: dict):
    """
    Train model task (optional, untuk scheduled retraining)
    
    Args:
        file_path: Path to training data
        config: Training configuration
    """
    try:
        print(f"Training model with data from {file_path}")
        
        # Load and preprocess
        df = load_and_normalize(file_path, dayfirst=config.get('dayfirst', True))
        df_processed = preprocess_data(df)
        df_fe = prepare_features(df_processed, group_cols=['partnumber', 'site_code'])
        
        # Train
        forecaster = MLForecaster(config)
        forecaster.train_and_select_model(df_fe)
        
        # Save
        model_path = config.get('model_path', 'models/best_model.pkl')
        forecaster.save_model(model_path)
        
        print(f"Model training completed and saved to {model_path}")
        
        return {
            'status': 'success',
            'model_path': model_path,
            'metrics': forecaster.get_metrics()
        }
        
    except Exception as e:
        print(f"Training error: {str(e)}")
        print(traceback.format_exc())
        raise

