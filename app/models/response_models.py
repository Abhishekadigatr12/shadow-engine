from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum


class ClassificationEnum(str, Enum):
    """Data classification categories"""
    PII = "PII"
    CREDENTIALS = "Credentials"
    SOURCE_CODE = "Source Code"
    FINANCIAL_DATA = "Financial Data"
    MEDICAL_DATA = "Medical Data"
    CONFIDENTIAL_BUSINESS_DATA = "Confidential Business Data"
    SAFE = "Safe"


class SeverityEnum(str, Enum):
    """Risk severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionEnum(str, Enum):
    """Decision actions"""
    ALLOW = "ALLOW"
    ALERT = "ALERT"
    MASK = "MASK"
    BLOCK = "BLOCK"


class SensitiveEntity(BaseModel):
    """Detected sensitive entity"""
    entity_type: str
    value: Optional[str] = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    location: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoint"""
    classification: List[str]
    risk_score: float = Field(..., ge=0, le=1)
    severity: SeverityEnum
    action: ActionEnum
    reason: str
    sensitive_entities: List[SensitiveEntity]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    status_code: int
