from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
import uuid
import json

from ..models.request_models import AnalysisRequest, FeedbackRequest, AuthRequest
from ..models.response_models import AnalysisResponse, HealthResponse, ErrorResponse
from ..pipeline.orchestrator import run_analysis_pipeline
from ..storage.db import get_db
from ..storage.repository import EventRepository, DecisionRepository, FeedbackRepository, UserRiskProfileRepository
from ..core.security import verify_token, generate_api_key
from ..utils.logger import logger

router = APIRouter()


def verify_api_key(api_key: str = Header(None)) -> bool:
    """Verify API key"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # In production, verify against stored keys
    return True


@router.post("/shadow/analyze", response_model=AnalysisResponse)
async def analyze_input(
    request: AnalysisRequest,
    db = Depends(get_db),
    api_key: str = Header(None)
):
    """Analyze input for sensitive data"""
    try:
        verify_api_key(api_key)

        request_id = str(uuid.uuid4())
        
        # Run pipeline
        result = run_analysis_pipeline({
            "request_id": request_id,
            "raw_data": request.raw_data,
            "user_id": request.user_id or "anonymous",
            "context": request.context or {},
        })

        # Store in database
        try:
            EventRepository.create(
                db,
                event_id=request_id,
                user_id=request.user_id or "anonymous",
                raw_data=request.raw_data[:500],  # Store truncated version
                classification=json.dumps(result.get("classification", [])),
                risk_score=result.get("risk_score", 0),
                severity=result.get("severity", "LOW"),
                action=result.get("action", "ALLOW")
            )

            DecisionRepository.create(
                db,
                decision_id=str(uuid.uuid4()),
                event_id=request_id,
                action=result.get("action"),
                risk_score=result.get("risk_score"),
                reason=result.get("reason")
            )

            # Update user profile if high risk
            if result.get("risk_score", 0) > 0.6:
                UserRiskProfileRepository.increment_alert_count(db, request.user_id or "anonymous")
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            # Don't fail the request if DB is down

        logger.info(f"Analysis completed: {request_id}, action={result.get('action')}")

        return result

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shadow/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db = Depends(get_db),
    api_key: str = Header(None)
):
    """Submit feedback on analysis"""
    try:
        verify_api_key(api_key)

        feedback_id = str(uuid.uuid4())

        FeedbackRepository.create(
            db,
            feedback_id=feedback_id,
            event_id=request.request_id,
            user_id="feedback_user",
            is_correct=request.is_correct,
            actual_classification=json.dumps(request.actual_classification),
            notes=request.notes
        )

        logger.info(f"Feedback recorded: {feedback_id}, is_correct={request.is_correct}")

        return {
            "feedback_id": feedback_id,
            "status": "recorded",
            "message": "Feedback submitted successfully"
        }

    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shadow/risk/{user_id}")
async def get_user_risk(
    user_id: str,
    db = Depends(get_db),
    api_key: str = Header(None)
):
    """Get user risk profile"""
    try:
        verify_api_key(api_key)

        profile = UserRiskProfileRepository.get_or_create(db, user_id)

        return {
            "user_id": user_id,
            "risk_level": profile.risk_level,
            "alert_count": profile.alert_count,
            "last_alert": profile.last_alert,
            "trusted": profile.trusted
        }

    except Exception as e:
        logger.error(f"Risk profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@router.post("/auth/login")
async def login(request: AuthRequest):
    """Login endpoint (simplified)"""
    # In production, verify credentials against database
    if request.username and request.password:
        token = generate_api_key()
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")
