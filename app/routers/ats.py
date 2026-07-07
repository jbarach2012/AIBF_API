"""/api/ats/evaluate -- score a resume and produce an ATS decision + data points."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import features as feat
from ..services.ats_engine import evaluate
from .resumes import gen

router = APIRouter(prefix="/api/ats", tags=["ats"])


@router.post("/evaluate", response_model=schemas.ATSDecisionResponse)
def evaluate_ats(body: schemas.ATSInput, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter_by(resume_id=body.resume_id).first()
    features = resume.features if resume else feat.normalize_features(None, body.resume_id)
    candidate_id = resume.candidate_id if resume else gen("cand")

    job_skills = feat.parse_job_skills(body.job_description)
    ats = evaluate(features, job_skills)
    ats_id = gen("ats")
    db.add(models.ATSDecision(
        ats_decision_id=ats_id, resume_id=body.resume_id, candidate_id=candidate_id,
        job_description=body.job_description, data_points=ats["data_points"],
        score=ats["score"], final_verdict=ats["final_verdict"],
    ))
    db.commit()
    return schemas.ATSDecisionResponse(
        ats_decision_id=ats_id, candidate_id=candidate_id, data_points=ats["data_points"],
        score=ats["score"], final_verdict=ats["final_verdict"],
    )
