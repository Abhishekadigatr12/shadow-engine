from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


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
    value: str
    confidence: float = Field(..., ge=0, le=1)
    location: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint"""
    raw_data: str = Field(..., min_length=1, max_length=10000)
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

    @validator('raw_data')
    def sanitize_raw_data(cls, v):
        """Sanitize input data"""
        return v.replace('\x00', '')[:10000]


class DetectionResult(BaseModel):
    """Detection engine output"""
    regex_matches: List[Dict[str, Any]] = []
    anomaly_score: float = Field(default=0, ge=0, le=1)
    detected_patterns: List[str] = []


class LLMResult(BaseModel):
    """LLM classification output"""
    classification: List[str]
    risk_score: float = Field(..., ge=0, le=1)
    reasoning: str
    entities: List[SensitiveEntity] = []


class RiskScore(BaseModel):
    """Computed risk score"""
    overall_score: float = Field(..., ge=0, le=1)
    regex_contribution: float = Field(default=0, ge=0, le=1)
    llm_contribution: float = Field(default=0, ge=0, le=1)
    anomaly_contribution: float = Field(default=0, ge=0, le=1)


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


class FeedbackRequest(BaseModel):
    """User feedback on analysis"""
    request_id: str
    actual_classification: List[str]
    is_correct: bool
    notes: Optional[str] = None


class RiskProfile(BaseModel):
    """User risk profile"""
    user_id: str
    risk_level: SeverityEnum
    last_alert: Optional[datetime] = None
    alert_count: int = 0
    trusted: bool = False


class AuthRequest(BaseModel):
    """Authentication request"""
    username: str
    password: str


class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
