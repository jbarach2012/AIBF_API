"""AIBF FastAPI application entry point.

Implements the OpenAPI contract in openapi/aibf.yaml:
  POST /api/resumes, GET /api/resumes
  POST /api/ats/evaluate
  POST /api/aibf/analyze
  POST /api/admin/feedback
  POST /api/model-training/retrain
plus /health and an admin flagged-feed convenience route.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  (ensure models are registered on Base)
from .config import settings
from .database import Base, SessionLocal, engine as db_engine
from .routers import admin, aibf, ats, model_training, resumes
from .services import features as feat
from .services.ats_engine import evaluate
from .services.bias_engine import engine as bias
from .services.seed_data import demo_resumes


def _seed_demo() -> None:
    db = SessionLocal()
    try:
        for d in demo_resumes():
            if db.query(models.Resume).filter_by(resume_id=d["resume_id"]).first():
                continue
            features = feat.normalize_features(d["features"], d["resume_id"])
            db.add(models.Resume(
                resume_id=d["resume_id"], candidate_id=d["candidate_id"],
                file_url=None, features=features,
            ))
            db.commit()
            js = feat.parse_job_skills(None)
            ats = evaluate(features, js)
            ats_id = f"ats_{d['resume_id']}"
            db.add(models.ATSDecision(
                ats_decision_id=ats_id, resume_id=d["resume_id"], candidate_id=d["candidate_id"],
                job_description=None, data_points=ats["data_points"],
                score=ats["score"], final_verdict=ats["final_verdict"],
            ))
            db.commit()
            res = bias.analyze(features, job_skills=js)
            db.add(models.AIBFDecision(
                aibf_decision_id=f"aibf_{d['resume_id']}", ats_decision_id=ats_id,
                candidate_id=d["candidate_id"], bias_score=res["bias_score"],
                upper_limit=res["upper_limit"], lower_limit=res["lower_limit"],
                flagged=res["flagged"], explanations=res["explanations"],
                attributions=res["attributions"],
            ))
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=db_engine)
    bias.ensure_fitted()
    if settings.seed_demo_data:
        _seed_demo()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="AI Bias Firewall (AIBF): real-time bias detection for ATS recruitment decisions.",
    lifespan=lifespan,
)

app.include_router(resumes.router)
app.include_router(ats.router)
app.include_router(aibf.router)
app.include_router(admin.router)
app.include_router(model_training.router)


@app.get("/", tags=["meta"])
def root():
    return {"name": settings.app_name, "version": settings.version, "docs": "/docs"}


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "model_version": bias.model_version}
