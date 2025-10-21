# backend/app/schemas.py
"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ForecastConfig(BaseModel):
    """Configuration for forecast job"""
    forecast_horizon: int = Field(default=7, ge=1, le=90, description="Number of days to forecast")
    forecast_site_codes: Optional[List[str]] = Field(default=None, description="List of site codes to forecast")
    forecast_start_date: Optional[str] = Field(default=None, description="Start date for forecast in DD/MM/YYYY format")
    zero_threshold: float = Field(default=0.5, ge=0, le=10, description="Threshold below which forecast is set to 0")
    rounding_mode: str = Field(default='half_up', description="Rounding mode: half_up, round, ceil, floor")
    random_state: int = Field(default=42, description="Random state for reproducibility")
    dayfirst: bool = Field(default=True, description="Parse dates with day first (DD/MM/YYYY)")
    
    @validator('rounding_mode')
    def validate_rounding_mode(cls, v):
        allowed = ['half_up', 'round', 'ceil', 'floor']
        if v not in allowed:
            raise ValueError(f"rounding_mode must be one of {allowed}")
        return v
    
    @validator('forecast_start_date')
    def validate_forecast_start_date(cls, v):
        if v is not None and v != '':
            try:
                from datetime import datetime
                # Try to parse DD/MM/YYYY format
                datetime.strptime(v, '%d/%m/%Y')
            except ValueError:
                raise ValueError("forecast_start_date must be in DD/MM/YYYY format")
        return v if v != '' else None


class ForecastSubmitRequest(BaseModel):
    """Request schema for submitting forecast job"""
    config: ForecastConfig


class ForecastResponse(BaseModel):
    """Response schema for forecast submission"""
    job_id: int
    task_id: Optional[str]
    status: str
    message: str


class ForecastStatusResponse(BaseModel):
    """Response schema for forecast status"""
    job_id: int
    task_id: Optional[str]
    status: str
    progress: int
    filename: Optional[str]
    created_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metrics: Optional[Dict[str, Any]]
    error_message: Optional[str]
    
    class Config:
        orm_mode = True


class ForecastHistoryResponse(BaseModel):
    """Response schema for forecast history"""
    total: int
    page: int
    page_size: int
    jobs: List[Dict[str, Any]]


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    database: str
    celery: str
    version: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str]
    timestamp: datetime

