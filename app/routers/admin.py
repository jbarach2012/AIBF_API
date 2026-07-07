"""/api/admin -- HR feedback and the flagged-resume review feed."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.bias_engine import engine
from .resumes import gen

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/feedback", status_code=201, response_model=schemas.HRFeedbackResponse)
def submit_feedback(body: schemas.HRFeedbackInput, db: Session = Depends(get_db)):
    hrf_id = gen("hrf")
    db.add(models.HRFeedback(
        hr_feedback_id=hrf_id, feedback_type=body.feedback_type, hr_id=body.hr_id,
        ats_decision_id=body.ats_decision_id, aibf_decision_id=body.aibf_decision_id,
        feedback_details=body.feedback_details, final_verdict=body.final_verdict,
    ))

    ats = db.query(models.ATSDecision).filter_by(ats_decision_id=body.ats_decision_id).first()
    aibf = db.query(models.AIBFDecision).filter_by(aibf_decision_id=body.aibf_decision_id).first()
    mtf_id = gen("mtf")
    db.add(models.ModelTrainingFeedback(
        model_training_feedback_id=mtf_id, hr_feedback_id=hrf_id,
        ats_output=(ats.final_verdict if ats else None),
        aibf_output=("flagged" if (aibf and aibf.flagged) else "not_flagged"),
        training_outcome="recorded", model_version=engine.model_version,
    ))
    db.commit()
    return schemas.HRFeedbackResponse(
        model_training_feedback_id=mtf_id,
        ats_output=(ats.final_verdict if ats else None),
        aibf_output=("flagged" if (aibf and aibf.flagged) else "not_flagged"),
        training_outcome="recorded",
    )


@router.get("/flagged", response_model=List[schemas.FlaggedItem])
def list_flagged(db: Session = Depends(get_db)):
    rows = (
        db.query(models.AIBFDecision)
        .filter(models.AIBFDecision.flagged.is_(True))
        .order_by(models.AIBFDecision.bias_score.desc())
        .all()
    )
    return [
        schemas.FlaggedItem(
            aibf_decision_id=r.aibf_decision_id, ats_decision_id=r.ats_decision_id,
            candidate_id=r.candidate_id, bias_score=r.bias_score,
            explanations=r.explanations or [],
        )
        for r in rows
    ]
