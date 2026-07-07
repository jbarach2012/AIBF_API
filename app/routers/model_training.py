"""/api/model-training/retrain -- recalibrate the bias model from HR feedback."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import features as feat
from ..services.bias_engine import engine
from .resumes import gen

router = APIRouter(prefix="/api/model-training", tags=["model-training"])

_OVERRIDE_VERDICTS = {"override", "overridden", "overturn", "overturned", "reject_ats"}


@router.post("/retrain", response_model=schemas.RetrainResponse)
def retrain(body: schemas.ModelTrainingInput, db: Session = Depends(get_db)):
    feedback = db.query(models.HRFeedback).all()
    total = len(feedback)
    overrides = sum(1 for f in feedback if (f.final_verdict or "").lower() in _OVERRIDE_VERDICTS)
    override_rate = overrides / total if total else 0.0

    extra_x, extra_y = [], []
    for ats in db.query(models.ATSDecision).all():
        resume = db.query(models.Resume).filter_by(resume_id=ats.resume_id).first()
        if resume and resume.features and ats.score is not None:
            js = feat.parse_job_skills(ats.job_description)
            extra_x.append(feat.vector_list(feat.to_feature_vector(resume.features, js)))
            extra_y.append(float(ats.score))

    result = engine.retrain(
        extra_X=extra_x or None, extra_y=extra_y or None,
        feedback_stats={"override_rate": override_rate}, version=body.model_version,
    )

    mtf_id = gen("mtf")
    db.add(models.ModelTrainingFeedback(
        model_training_feedback_id=mtf_id, hr_feedback_id=body.feedback_id,
        ats_output="recalibrated",
        aibf_output=f"model={result['model_version']} upper_limit={result['upper_limit']:.3f} n_train={result['n_train']}",
        training_outcome="success", model_version=result["model_version"],
    ))
    db.commit()
    return schemas.RetrainResponse(
        model_training_feedback_id=mtf_id, ats_output="recalibrated",
        aibf_output=f"model={result['model_version']} upper_limit={result['upper_limit']:.3f}",
        training_outcome="success",
    )
