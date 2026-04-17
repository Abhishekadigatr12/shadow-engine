from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from ..core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, echo=settings.DATABASE_ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Event(Base):
    """Event analysis record"""
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    raw_data = Column(Text)
    classification = Column(Text)  # JSON string
    risk_score = Column(Float)
    severity = Column(String)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class Decision(Base):
    """Decision log"""
    __tablename__ = "decisions"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, index=True)
    action = Column(String)
    risk_score = Column(Float)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    """User feedback"""
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, index=True)
    user_id = Column(String, index=True)
    is_correct = Column(Boolean)
    actual_classification = Column(Text)  # JSON string
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserRiskProfile(Base):
    """User risk profile"""
    __tablename__ = "user_risk_profiles"

    user_id = Column(String, primary_key=True, index=True)
    risk_level = Column(String)
    alert_count = Column(Integer, default=0)
    last_alert = Column(DateTime)
    trusted = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
