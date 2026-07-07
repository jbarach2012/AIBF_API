"""Feature extraction & encoding for AIBF.

Every resume signal is split into two groups:

  * MERIT features      -- a fair scorer MAY use these (skills, relevant
                           experience, certifications, projects).
  * PROTECTED-PROXY     -- a fair scorer must NOT let these drive the outcome
                           (institutional prestige, employment gaps, age proxy,
                           and demographic proxies). The demographic proxies are
                           used ONLY to measure disparate impact -- never to score.

The AIBF measures how much of an ATS decision was moved by the protected-proxy
group. See docs/01-methodology.md.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

REFERENCE_YEAR = 2025  # fixed, for deterministic age derivation

SKILL_VOCAB = [
    "python", "java", "sql", "aws", "docker", "react",
    "ml", "nlp", "kubernetes", "go", "spark", "tensorflow",
]
DEFAULT_JOB_SKILLS = ["python", "sql", "aws", "docker", "ml"]

# Illustrative disadvantaged-group buckets, used ONLY for disparate-impact
# measurement. This is an audit signal, never an input to any score.
MINORITY_PROXY = {"black", "hispanic", "native", "mena"}

MERIT_FEATURES = ["skill_match", "relevant_experience", "certifications", "projects"]
PROTECTED_FEATURES = [
    "prestige_top", "prestige_low", "employment_gap_months",
    "age_over_40", "gender_female_proxy", "ethnicity_minority_proxy",
]
FEATURE_ORDER = MERIT_FEATURES + PROTECTED_FEATURES


def parse_job_skills(job_description: Optional[str]) -> List[str]:
    if not job_description:
        return list(DEFAULT_JOB_SKILLS)
    jd = job_description.lower()
    found = [s for s in SKILL_VOCAB if s in jd]
    return found or list(DEFAULT_JOB_SKILLS)


def _h(resume_id: str, salt: str) -> int:
    return int(hashlib.sha256(f"{resume_id}:{salt}".encode()).hexdigest(), 16)


def synthesize_features(resume_id: str) -> Dict[str, Any]:
    """Deterministically fabricate plausible attributes for a resume_id that
    carries no attached features, so the pipeline always runs end-to-end without
    external file parsing. Entirely synthetic; contains no real PII."""
    rid = resume_id or "unknown"
    n_sk = 3 + _h(rid, "nsk") % 6
    skills = [SKILL_VOCAB[_h(rid, f"sk{i}") % len(SKILL_VOCAB)] for i in range(n_sk)]
    return {
        "skills": sorted(set(skills)),
        "relevant_experience": round(1 + (_h(rid, "rexp") % 100) / 10.0, 1),
        "certifications": _h(rid, "cert") % 5,
        "projects": _h(rid, "proj") % 6,
        "education_tier": 1 + _h(rid, "tier") % 3,
        "employment_gap_months": _h(rid, "gap") % 25,
        "age": 24 + _h(rid, "age") % 40,
        "gender": ["M", "F", "U"][_h(rid, "g") % 3],
        "ethnicity": ["white", "asian", "black", "hispanic", "native", "mena"][_h(rid, "e") % 6],
    }


def normalize_features(raw: Optional[Dict[str, Any]], resume_id: str = "") -> Dict[str, Any]:
    base = synthesize_features(resume_id)
    if raw:
        base.update({k: v for k, v in raw.items() if v is not None})
    return base


def compute_skill_match(resume_skills: List[str], job_skills: List[str]) -> float:
    if not job_skills:
        return 0.0
    rs = {s.lower() for s in (resume_skills or [])}
    js = {s.lower() for s in job_skills}
    return round(len(rs & js) / len(js), 4)


def to_feature_vector(features: Dict[str, Any], job_skills: List[str]) -> Dict[str, float]:
    tier = int(features.get("education_tier", 2))
    age = int(features.get("age", 30))
    gender = str(features.get("gender", "U")).upper()
    ethnicity = str(features.get("ethnicity", "white")).lower()
    return {
        "skill_match": compute_skill_match(features.get("skills", []), job_skills),
        "relevant_experience": float(features.get("relevant_experience", 0.0)),
        "certifications": float(features.get("certifications", 0)),
        "projects": float(features.get("projects", 0)),
        "prestige_top": 1.0 if tier == 1 else 0.0,
        "prestige_low": 1.0 if tier == 3 else 0.0,
        "employment_gap_months": float(features.get("employment_gap_months", 0.0)),
        "age_over_40": float(max(0, age - 40)),
        "gender_female_proxy": 1.0 if gender == "F" else 0.0,
        "ethnicity_minority_proxy": 1.0 if ethnicity in MINORITY_PROXY else 0.0,
    }


def vector_list(vec: Dict[str, float]) -> List[float]:
    return [vec[f] for f in FEATURE_ORDER]
