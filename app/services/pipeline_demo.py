"""End-to-end pipeline demo without starting a server.

    python -m app.services.pipeline_demo
"""
from __future__ import annotations

from . import features as feat
from .ats_engine import evaluate
from .bias_engine import engine
from .seed_data import demo_resumes


def main() -> None:
    engine.ensure_fitted()
    js = feat.parse_job_skills("python sql aws docker ml engineer")
    print(f"AIBF model: {engine.model_version}  (flag threshold = {engine.upper_limit})\n")
    for d in demo_resumes():
        f = feat.normalize_features(d["features"], d["resume_id"])
        ats = evaluate(f, js)
        res = engine.analyze(f, job_skills=js)
        print(f"{d['resume_id']}: ATS score={ats['score']} verdict={ats['final_verdict']}")
        print(f"    bias_score={res['bias_score']}  flagged={res['flagged']}")
        for e in res["explanations"]:
            print(f"      - {e}")
        print()


if __name__ == "__main__":
    main()
