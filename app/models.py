"""ORM models for the AIBF pipeline: Resume -> ATSDecision -> AIBFDecision,
plus HRFeedback and ModelTrainingFeedback."""
from __future__ import annotations

from datetime import datetime, timezone


def _utcnow() -> datetime:
    """Naive UTC timestamp (SQLite-friendly, no deprecation warning)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String, Text

from .database import Base


class Resume(Base):
    __tablename__ = "resumes"
    resume_id = Column(String, primary_key=True)
    candidate_id = Column(String, index=True)
    file_url = Column(String, nullable=True)
    submitted_at = Column(DateTime, default=_utcnow)
    features = Column(JSON, default=dict)


class ATSDecision(Base):
    __tablename__ = "ats_decisions"
    ats_decision_id = Column(String, primary_key=True)
    resume_id = Column(String, ForeignKey("resumes.resume_id"), index=True)
    candidate_id = Column(String, index=True)
    job_description = Column(Text, nullable=True)
    data_points = Column(JSON, default=dict)
    score = Column(Float)
    final_verdict = Column(String)
    created_at = Column(DateTime, default=_utcnow)


class AIBFDecision(Base):
    __tablename__ = "aibf_decisions"
    aibf_decision_id = Column(String, primary_key=True)
    ats_decision_id = Column(String, ForeignKey("ats_decisions.ats_decision_id"), index=True)
    candidate_id = Column(String, index=True)
    bias_score = Column(Float)
    upper_limit = Column(Float)
    lower_limit = Column(Float)
    flagged = Column(Boolean, default=False)
    explanations = Column(JSON, default=list)
    attributions = Column(JSON, default=dict)
    created_at = Column(DateTime, default=_utcnow)


class HRFeedback(Base):
    __tablename__ = "hr_feedback"
    hr_feedback_id = Column(String, primary_key=True)
    feedback_type = Column(String)
    hr_id = Column(String, index=True)
    ats_decision_id = Column(String, index=True)
    aibf_decision_id = Column(String, index=True)
    feedback_details = Column(Text, nullable=True)
    final_verdict = Column(String)
    created_at = Column(DateTime, default=_utcnow)


class ModelTrainingFeedback(Base):
    __tablename__ = "model_training_feedback"
    model_training_feedback_id = Column(String, primary_key=True)
    hr_feedback_id = Column(String, index=True, nullable=True)
    ats_output = Column(String, nullable=True)
    aibf_output = Column(String, nullable=True)
    training_outcome = Column(String)
    model_version = Column(String)
    created_at = Column(DateTime, default=_utcnow)
