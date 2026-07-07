"""/api/resumes -- submit a resume (runs the full ATS + AIBF pipeline) and list resumes."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import features as feat
from ..services.ats_engine import evaluate
from ..services.bias_engine import engine

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


def gen(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@router.get("", response_model=List[schemas.ResumeOut])
def get_resumes(
    status: Optional[str] = Query(None, pattern="^(flagged|active)$"),
    db: Session = Depends(get_db),
):
    resumes = db.query(models.Resume).order_by(models.Resume.submitted_at.desc()).all()
    if not status:
        return resumes
    flagged_ats = {
        a.ats_decision_id
        for a in db.query(models.AIBFDecision).filter(models.AIBFDecision.flagged.is_(True)).all()
    }
    flagged_resumes = set()
    if flagged_ats:
        flagged_resumes = {
            d.resume_id
            for d in db.query(models.ATSDecision)
            .filter(models.ATSDecision.ats_decision_id.in_(flagged_ats))
            .all()
        }
    if status == "flagged":
        return [r for r in resumes if r.resume_id in flagged_resumes]
    return [r for r in resumes if r.resume_id not in flagged_resumes]


@router.post("", status_code=201, response_model=schemas.SubmitResumeResponse)
def submit_resume(body: schemas.ResumeCreate, db: Session = Depends(get_db)):
    resume_id = body.resume_id or gen("res")
    candidate_id = body.candidate_id or gen("cand")
    features = feat.normalize_features(body.features, resume_id)

    db.merge(models.Resume(
        resume_id=resume_id, candidate_id=candidate_id, file_url=body.file_url,
        submitted_at=body.submitted_at or datetime.now(timezone.utc).replace(tzinfo=None), features=features,
    ))
    db.commit()

    job_skills = feat.parse_job_skills(body.job_description)
    ats = evaluate(features, job_skills)
    ats_id = gen("ats")
    db.add(models.ATSDecision(
        ats_decision_id=ats_id, resume_id=resume_id, candidate_id=candidate_id,
        job_description=body.job_description, data_points=ats["data_points"],
        score=ats["score"], final_verdict=ats["final_verdict"],
    ))
    db.commit()

    res = engine.analyze(features, job_skills=job_skills)
    db.add(models.AIBFDecision(
        aibf_decision_id=gen("aibf"), ats_decision_id=ats_id, candidate_id=candidate_id,
        bias_score=res["bias_score"], upper_limit=res["upper_limit"], lower_limit=res["lower_limit"],
        flagged=res["flagged"], explanations=res["explanations"], attributions=res["attributions"],
    ))
    db.commit()

    return schemas.SubmitResumeResponse(
        ats_decision_id=ats_id, candidate_id=candidate_id, score=ats["score"],
        final_verdict=ats["final_verdict"], flagged=res["flagged"], bias_score=res["bias_score"],
    )
