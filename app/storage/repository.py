import json
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from .db import Event, Decision, Feedback, UserRiskProfile


class EventRepository:
    """Repository for event operations"""

    @staticmethod
    def create(db: Session, event_id: str, **kwargs) -> Event:
        """Create new event"""
        db_event = Event(
            id=event_id or str(uuid.uuid4()),
            **kwargs
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def get(db: Session, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_by_user(db: Session, user_id: str, limit: int = 100) -> List[Event]:
        """Get events by user"""
        return db.query(Event).filter(Event.user_id == user_id).limit(limit).all()

    @staticmethod
    def get_high_risk(db: Session, threshold: float = 0.85) -> List[Event]:
        """Get high risk events"""
        return db.query(Event).filter(Event.risk_score >= threshold).all()


class DecisionRepository:
    """Repository for decision operations"""

    @staticmethod
    def create(db: Session, decision_id: str, **kwargs) -> Decision:
        """Create new decision"""
        db_decision = Decision(
            id=decision_id or str(uuid.uuid4()),
            **kwargs
        )
        db.add(db_decision)
        db.commit()
        db.refresh(db_decision)
        return db_decision

    @staticmethod
    def get_by_event(db: Session, event_id: str) -> Optional[Decision]:
        """Get decision for event"""
        return db.query(Decision).filter(Decision.event_id == event_id).first()


class FeedbackRepository:
    """Repository for feedback operations"""

    @staticmethod
    def create(db: Session, feedback_id: str, **kwargs) -> Feedback:
        """Create new feedback"""
        db_feedback = Feedback(
            id=feedback_id or str(uuid.uuid4()),
            **kwargs
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback

    @staticmethod
    def get_by_event(db: Session, event_id: str) -> Optional[Feedback]:
        """Get feedback for event"""
        return db.query(Feedback).filter(Feedback.event_id == event_id).first()

    @staticmethod
    def get_user_feedback(db: Session, user_id: str, limit: int = 100) -> List[Feedback]:
        """Get user feedback"""
        return db.query(Feedback).filter(Feedback.user_id == user_id).limit(limit).all()


class UserRiskProfileRepository:
    """Repository for user risk profile operations"""

    @staticmethod
    def get_or_create(db: Session, user_id: str) -> UserRiskProfile:
        """Get or create user risk profile"""
        profile = db.query(UserRiskProfile).filter(UserRiskProfile.user_id == user_id).first()
        
        if not profile:
            profile = UserRiskProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        return profile

    @staticmethod
    def update_risk_level(db: Session, user_id: str, risk_level: str) -> UserRiskProfile:
        """Update user risk level"""
        profile = UserRiskProfileRepository.get_or_create(db, user_id)
        profile.risk_level = risk_level
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def increment_alert_count(db: Session, user_id: str) -> UserRiskProfile:
        """Increment alert count"""
        profile = UserRiskProfileRepository.get_or_create(db, user_id)
        profile.alert_count += 1
        profile.last_alert = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        return profile
