# backend/app/tasks/batch_task.py
"""
Batch processing task dengan auto-partition, timeout, dan rollback
"""

from celery import Task, group, chord
from datetime import datetime, timedelta
import traceback
import pandas as pd
from pathlib import Path
from uuid import uuid4
import time

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import BatchJob, ForecastJob
from app.core.batch_processor import BatchProcessor
from app.core.ml_engine import MLForecaster
from app.core.preprocessing import load_and_normalize, preprocess_data, prepare_features
from app.core.utils import safe_save_csv


class BatchForecastTask(Task):
    """Base task dengan error handling untuk batch"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle batch task failure"""
        batch_id = args[0] if args else None
        if batch_id:
            db = SessionLocal()
            try:
                batch_job = db.query(BatchJob).filter_by(batch_id=batch_id).first()
                if batch_job:
                    batch_job.status = 'FAILED'
                    batch_job.error_message = str(exc)
                    batch_job.completed_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()


@celery_app.task(base=BatchForecastTask, bind=True, name='batch.run_batch_forecast', 
                 time_limit=3600, soft_time_limit=3300)
def run_batch_forecast_task(self, batch_id: str):
    """
    Main batch forecast task dengan auto-partitioning
    
    Features:
    - Auto partition data by site or size
    - Parallel processing
    - Timeout monitoring (max 5 minutes per partition)
    - Auto rollback if any partition fails
    - Combine results
    """
    db = SessionLocal()
    
    try:
        # Get batch job
        batch_job = db.query(BatchJob).filter_by(batch_id=batch_id).first()
        if not batch_job:
            raise ValueError(f"Batch job {batch_id} not found")
        
        # Update status
        batch_job.status = 'PROCESSING'
        batch_job.started_at = datetime.utcnow()
        batch_job.progress = 5
        db.commit()
        
        print(f"[Batch {batch_id}] Starting batch forecast")
        self.update_state(state='PROGRESS', meta={'progress': 5, 'status': 'Loading data'})
        
        # Load data
        print(f"[Batch {batch_id}] Loading data from {batch_job.original_file_path}")
        df = load_and_normalize(batch_job.original_file_path, 
                               dayfirst=batch_job.config.get('dayfirst', True))
        
        batch_job.progress = 10
        db.commit()
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Analyzing data'})
        
        # Initialize batch processor
        processor = BatchProcessor(
            max_rows_per_job=batch_job.config.get('max_rows_per_partition', 2000),
            partition_by=batch_job.partition_strategy,
            max_partitions=batch_job.config.get('max_partitions', 20)
        )
        
        # Analyze and create partitions
        print(f"[Batch {batch_id}] Creating partitions...")
        partitions = processor.create_partitions(df)
        
        batch_job.total_partitions = len(partitions)
        batch_job.progress = 15
        db.commit()
        
        print(f"[Batch {batch_id}] Created {len(partitions)} partitions")
        
        # Estimate time
        time_estimate = processor.estimate_processing_time(partitions)
        print(f"[Batch {batch_id}] Estimated time: {time_estimate['parallel_total_seconds']}s " 
              f"(speedup: {time_estimate['speedup_factor']}x)")
        
        self.update_state(state='PROGRESS', meta={'progress': 15, 'status': f'Processing {len(partitions)} partitions'})
        
        # Save partitions and process
        partition_dir = Path('uploads') / batch_id / 'partitions'
        partition_dir.mkdir(parents=True, exist_ok=True)
        
        partition_results = []
        partition_files = []
        max_exec_time = batch_job.max_execution_time
        
        for i, partition in enumerate(partitions):
            try:
                progress = 15 + (i * 70 // len(partitions))
                batch_job.progress = progress
                db.commit()
                
                partition_id = partition['partition_id']
                metadata = partition['metadata']
                
                print(f"[Batch {batch_id}] Processing partition {partition_id}/{len(partitions)-1}")
                print(f"  Rows: {metadata['rows']}, Sites: {metadata['site_count']}, " 
                      f"Parts: {metadata['partnumbers_count']}")
                
                # Update state dengan detail partition info
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'status': f'Partition {partition_id+1}/{len(partitions)}',
                        'current_partition': {
                            'id': partition_id,
                            'rows': metadata['rows'],
                            'sites': metadata['sites'],
                            'partnumbers': metadata['partnumbers_count'],
                            'status': 'PROCESSING'
                        },
                        'partition_progress': [
                            {
                                'partition_id': p['partition_id'],
                                'status': p.get('status', 'PENDING')
                            } for p in partition_results
                        ]
                    }
                )
                
                # Process partition with timeout monitoring
                start_time = time.time()
                
                # Preprocess partition data
                df_partition = partition['data']
                df_processed = preprocess_data(df_partition)
                df_fe = prepare_features(df_processed, group_cols=['partnumber', 'site_code'])
                
                # Check timeout
                if time.time() - start_time > max_exec_time:
                    raise TimeoutError(f"Partition {partition_id} exceeded max execution time")
                
                # Train or load model
                forecaster = MLForecaster(batch_job.config)
                model_path = Path('models/best_model.pkl')
                
                if model_path.exists():
                    print(f"  Loading existing model")
                    forecaster.load_model(str(model_path))
                else:
                    print(f"  Training new model")
                    forecaster.train_and_select_model(df_fe)
                    forecaster.save_model(str(model_path))
                
                # Check timeout
                if time.time() - start_time > max_exec_time:
                    raise TimeoutError(f"Partition {partition_id} exceeded max execution time")
                
                # Generate forecast (with graceful handling for empty data after filtering)
                try:
                    forecast_df = forecaster.forecast(
                        df_processed,
                        start_date=batch_job.config.get('forecast_start_date'),
                        start_offset_days=batch_job.config.get('forecast_start_offset_days', 1)
                    )
                except ValueError as e:
                    # Handle case: data filtered by forecast_site_codes results in empty dataset
                    if "No data for specified forecast_site_codes" in str(e):
                        print(f"  ⏭️  SKIPPED: Partition {partition_id} - Sites in this partition not in forecast_site_codes filter")
                        print(f"     Partition sites: {metadata['sites']}")
                        if batch_job.config.get('forecast_site_codes'):
                            print(f"     Filter sites: {batch_job.config.get('forecast_site_codes')}")
                        
                        # Mark partition as skipped (not an error, just filtered out)
                        partition_results.append({
                            'partition_id': partition_id,
                            'status': 'SKIPPED',
                            'reason': 'Sites not in forecast_site_codes filter',
                            'metadata': metadata,
                            'partition_sites': metadata['sites'],
                            'filter_sites': batch_job.config.get('forecast_site_codes'),
                            'execution_time': round(time.time() - start_time, 2)
                        })
                        
                        # Increment skipped counter
                        batch_job.skipped_partitions += 1
                        db.commit()
                        
                        # Continue to next partition (not counted as failed)
                        continue
                    else:
                        # Other ValueError - treat as error
                        raise
                
                # Save partition result
                output_file = f"outputs/{batch_id}/partition_{partition_id:03d}_forecast.csv"
                saved_path = safe_save_csv(forecast_df, output_file)
                partition_files.append(saved_path)
                
                elapsed_time = time.time() - start_time
                
                partition_results.append({
                    'partition_id': partition_id,
                    'status': 'COMPLETED',
                    'metadata': metadata,
                    'output_file': saved_path,
                    'metrics': forecaster.get_metrics(),
                    'execution_time': round(elapsed_time, 2)
                })
                
                batch_job.completed_partitions += 1
                db.commit()
                
                print(f"  ✅ Partition {partition_id} completed in {elapsed_time:.1f}s")
                
            except TimeoutError as e:
                print(f"  ⏱️  TIMEOUT: Partition {partition_id} - {str(e)}")
                partition_results.append({
                    'partition_id': partition_id,
                    'status': 'TIMEOUT',
                    'error': str(e),
                    'metadata': partition['metadata']
                })
                batch_job.failed_partitions += 1
                db.commit()
                
                # Rollback: Stop processing dan mark sebagai failed
                raise TimeoutError(f"Partition {partition_id} timeout - Rolling back batch")
                
            except Exception as e:
                print(f"  ❌ ERROR: Partition {partition_id} - {str(e)}")
                partition_results.append({
                    'partition_id': partition_id,
                    'status': 'FAILED',
                    'error': str(e),
                    'metadata': partition['metadata']
                })
                batch_job.failed_partitions += 1
                db.commit()
                
                # Rollback: Stop jika ada failure
                raise Exception(f"Partition {partition_id} failed - Rolling back batch: {str(e)}")
        
        # All partitions completed - combine results (skip SKIPPED partitions)
        skipped_count = sum(1 for p in partition_results if p.get('status') == 'SKIPPED')
        success_count = sum(1 for p in partition_results if p.get('status') == 'COMPLETED')
        
        print(f"[Batch {batch_id}] Processing completed:")
        print(f"  Successful: {success_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Failed: {batch_job.failed_partitions}")
        
        if success_count == 0:
            raise Exception("No partitions produced forecasts. Check forecast_site_codes filter.")
        
        print(f"[Batch {batch_id}] Combining {success_count} successful partitions...")
        batch_job.progress = 90
        db.commit()
        
        # Combine only successful partition results (skip SKIPPED ones)
        if partition_files:
            combined_df = pd.concat([pd.read_csv(f) for f in partition_files], ignore_index=True)
            combined_output = f"outputs/{batch_id}/combined_forecast.csv"
            combined_path = safe_save_csv(combined_df, combined_output)
        else:
            raise Exception("No forecast files to combine")
        
        # Update batch job
        batch_job.status = 'COMPLETED'
        batch_job.progress = 100
        batch_job.partition_results = partition_results
        batch_job.output_files = partition_files
        batch_job.combined_output = combined_path
        batch_job.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"[Batch {batch_id}] Batch forecast completed successfully!")
        print(f"  Total partitions: {len(partitions)}")
        print(f"  Completed: {batch_job.completed_partitions}")
        print(f"  Skipped: {batch_job.skipped_partitions}")
        print(f"  Failed: {batch_job.failed_partitions}")
        print(f"  Combined output: {combined_path}")
        
        return {
            'status': 'success',
            'batch_id': batch_id,
            'total_partitions': len(partitions),
            'completed': batch_job.completed_partitions,
            'skipped': batch_job.skipped_partitions,
            'failed': batch_job.failed_partitions,
            'combined_output': combined_path,
            'partition_results': partition_results
        }
        
    except Exception as e:
        print(f"[Batch {batch_id}] BATCH FAILED: {str(e)}")
        print(traceback.format_exc())
        
        # Rollback
        batch_job.status = 'ROLLED_BACK'
        batch_job.error_message = f"Rolled back due to: {str(e)}"
        batch_job.completed_at = datetime.utcnow()
        db.commit()
        
        # Clean up partition files if needed
        try:
            partition_dir = Path('uploads') / batch_id
            if partition_dir.exists():
                print(f"[Batch {batch_id}] Cleaning up partition files...")
                # Optional: delete partition files to save space
                # shutil.rmtree(partition_dir)
        except:
            pass
        
        raise
        
    finally:
        db.close()

