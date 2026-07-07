"""/api/aibf/analyze -- run bias detection on an ATS decision + resume."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import features as feat
from ..services.bias_engine import engine
from .resumes import gen

router = APIRouter(prefix="/api/aibf", tags=["aibf"])


@router.post("/analyze", response_model=schemas.AIBFDecisionResponse)
def analyze_aibf(body: schemas.AIBFInput, db: Session = Depends(get_db)):
    ats = db.query(models.ATSDecision).filter_by(ats_decision_id=body.ats_decision_id).first()
    resume = db.query(models.Resume).filter_by(resume_id=body.resume_id).first()

    features = resume.features if resume else feat.normalize_features(None, body.resume_id)
    candidate_id = (resume.candidate_id if resume else (ats.candidate_id if ats else gen("cand")))
    job_description = ats.job_description if ats else None

    res = engine.analyze(features, job_description=job_description)
    aibf_id = gen("aibf")
    db.add(models.AIBFDecision(
        aibf_decision_id=aibf_id, ats_decision_id=body.ats_decision_id, candidate_id=candidate_id,
        bias_score=res["bias_score"], upper_limit=res["upper_limit"], lower_limit=res["lower_limit"],
        flagged=res["flagged"], explanations=res["explanations"], attributions=res["attributions"],
    ))
    db.commit()

    return schemas.AIBFDecisionResponse(
        aibf_decision_id=aibf_id, ats_decision_id=body.ats_decision_id, candidate_id=candidate_id,
        bias_score=res["bias_score"],
        bias_threshold_limits=schemas.ThresholdLimits(
            upper_limit=res["upper_limit"], lower_limit=res["lower_limit"]),
        flagged=res["flagged"], explanations=res["explanations"], attributions=res["attributions"],
    )
