# backend/app/models.py
"""
SQLAlchemy database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base


class ForecastJob(Base):
    """Model untuk menyimpan forecast job metadata"""
    __tablename__ = "forecast_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # File information
    filename = Column(String(500))
    file_path = Column(String(1000))
    output_file = Column(String(1000), nullable=True)
    
    # Configuration
    config = Column(JSON)
    
    # Status tracking
    status = Column(String(50), default='QUEUED', index=True)
    # Status values: QUEUED, PROCESSING, COMPLETED, FAILED
    
    progress = Column(Integer, default=0)  # 0-100
    
    # Metrics and results
    metrics = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # User info (untuk future SSO integration)
    created_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<ForecastJob(id={self.id}, status={self.status})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'filename': self.filename,
            'status': self.status,
            'progress': self.progress,
            'config': self.config,
            'metrics': self.metrics,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_by': self.created_by
        }


class ModelRegistry(Base):
    """Registry untuk trained models"""
    __tablename__ = "model_registry"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255))
    model_path = Column(String(1000))
    
    # Model info
    model_type = Column(String(100))  # RF_log, Ridge_log, etc.
    metrics = Column(JSON)
    
    # Training info
    trained_on = Column(DateTime(timezone=True), server_default=func.now())
    training_config = Column(JSON)
    training_data_rows = Column(Integer)
    
    # Status
    is_active = Column(Integer, default=1)  # 1=active, 0=inactive
    
    def __repr__(self):
        return f"<ModelRegistry(id={self.id}, model_type={self.model_type})>"


class BatchJob(Base):
    """Batch job untuk parallel processing dengan auto-partition"""
    __tablename__ = "batch_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Parent batch info
    batch_id = Column(String(255), unique=True, index=True)
    original_filename = Column(String(500))
    original_file_path = Column(String(1000))
    
    # Configuration
    config = Column(JSON)
    partition_strategy = Column(String(50))  # 'site', 'auto'
    total_partitions = Column(Integer)
    max_execution_time = Column(Integer, default=300)  # seconds per partition
    
    # Status tracking
    status = Column(String(50), default='QUEUED', index=True)
    # Status: QUEUED, PROCESSING, COMPLETED, FAILED, ROLLED_BACK
    
    progress = Column(Integer, default=0)  # 0-100
    completed_partitions = Column(Integer, default=0)
    failed_partitions = Column(Integer, default=0)
    skipped_partitions = Column(Integer, default=0)  # Partitions filtered out by forecast_site_codes
    
    # Results
    output_files = Column(JSON, nullable=True)  # List of output file paths
    partition_results = Column(JSON, nullable=True)  # Results per partition
    combined_output = Column(String(1000), nullable=True)  # Combined result file
    
    # Metrics & errors
    metrics = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # User
    created_by = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<BatchJob(id={self.id}, batch_id={self.batch_id}, status={self.status})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'batch_job_id': self.id,  # Alias for frontend consistency
            'original_filename': self.original_filename,
            'status': self.status,
            'progress': self.progress,
            'partition_strategy': self.partition_strategy if self.partition_strategy else 'site',
            'total_partitions': self.total_partitions,
            'completed_partitions': self.completed_partitions if self.completed_partitions else 0,
            'failed_partitions': self.failed_partitions if self.failed_partitions else 0,
            'skipped_partitions': getattr(self, 'skipped_partitions', 0),  # Backward compatible
            'config': self.config,
            'partition_results': self.partition_results,
            'metrics': self.metrics,
            'error_message': self.error_message,
            'combined_output': self.combined_output,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

