"""Pydantic request/response schemas.

These mirror the OpenAPI contract in ``openapi/aibf.yaml`` and add a few
optional response fields (e.g. ``flagged``, ``explanations``) that are a
superset of the spec and useful to the admin UI.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

# ``model_`` is a pydantic-v2 protected namespace; several of our fields legitimately
# start with it (model_training_feedback_id, model_version), so we disable the guard.
_ALLOW_MODEL = ConfigDict(protected_namespaces=())


class ResumeCreate(BaseModel):
    resume_id: Optional[str] = None
    candidate_id: Optional[str] = None
    file_url: Optional[str] = None
    submitted_at: Optional[datetime] = None
    # extensions (superset of the spec) so the pipeline is fully runnable:
    job_description: Optional[str] = None
    features: Optional[Dict[str, Any]] = None


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    resume_id: str
    candidate_id: Optional[str] = None
    file_url: Optional[str] = None
    submitted_at: Optional[datetime] = None


class SubmitResumeResponse(BaseModel):
    ats_decision_id: str
    candidate_id: str
    score: float
    final_verdict: str
    flagged: bool = False
    bias_score: float = 0.0


class ATSInput(BaseModel):
    resume_id: str
    job_description: Optional[str] = None


class ATSDecisionResponse(BaseModel):
    ats_decision_id: str
    candidate_id: str
    data_points: Dict[str, Any]
    score: float
    final_verdict: str


class AIBFInput(BaseModel):
    ats_decision_id: str
    resume_id: str


class ThresholdLimits(BaseModel):
    upper_limit: float
    lower_limit: float


class AIBFDecisionResponse(BaseModel):
    aibf_decision_id: str
    ats_decision_id: str
    candidate_id: str
    bias_score: float
    bias_threshold_limits: ThresholdLimits
    flagged: bool
    explanations: List[str] = Field(default_factory=list)
    attributions: Dict[str, float] = Field(default_factory=dict)


class HRFeedbackInput(BaseModel):
    feedback_type: str
    hr_id: str
    ats_decision_id: str
    aibf_decision_id: str
    feedback_details: Optional[str] = None
    final_verdict: str


class HRFeedbackResponse(BaseModel):
    model_config = _ALLOW_MODEL
    model_training_feedback_id: str
    ats_output: Optional[str] = None
    aibf_output: Optional[str] = None
    training_outcome: str


class ModelTrainingInput(BaseModel):
    model_config = _ALLOW_MODEL
    feedback_id: Optional[str] = None
    model_version: Optional[str] = None


class RetrainResponse(BaseModel):
    model_config = _ALLOW_MODEL
    model_training_feedback_id: str
    ats_output: Optional[str] = None
    aibf_output: Optional[str] = None
    training_outcome: str


class FlaggedItem(BaseModel):
    aibf_decision_id: str
    ats_decision_id: str
    candidate_id: str
    bias_score: float
    explanations: List[str]
