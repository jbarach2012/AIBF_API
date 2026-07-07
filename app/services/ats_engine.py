"""A *simulated* ATS scorer.

It deliberately blends legitimate merit signal with biased signal (prestige,
employment gaps, an age proxy, and demographic proxies) so that the AIBF has a
realistic, non-trivial decision to audit. In a real deployment the ATS is an
external system and AIBF consumes its score + data points via the API.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .features import FEATURE_ORDER, to_feature_vector

INTERCEPT = 20.0
WEIGHTS: Dict[str, float] = {
    # merit
    "skill_match": 40.0,
    "relevant_experience": 4.0,
    "certifications": 3.0,
    "projects": 2.0,
    # bias baked into the ATS (this is what AIBF exists to catch)
    "prestige_top": 15.0,
    "prestige_low": -8.0,
    "employment_gap_months": -1.2,
    "age_over_40": -0.5,
    "gender_female_proxy": -5.0,
    "ethnicity_minority_proxy": -5.0,
}


def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def raw_score(vec: Dict[str, float]) -> float:
    return INTERCEPT + sum(WEIGHTS[f] * vec[f] for f in FEATURE_ORDER)


def verdict_for(score: float) -> str:
    if score >= 60:
        return "accepted"
    if score >= 40:
        return "review"
    return "rejected"


def evaluate(features: Dict[str, Any], job_skills: List[str]) -> Dict[str, Any]:
    vec = to_feature_vector(features, job_skills)
    score = round(_clip(raw_score(vec)), 2)
    contributions = {f: round(WEIGHTS[f] * vec[f], 3) for f in FEATURE_ORDER}
    data_points = {
        "contributions": contributions,
        "intercept": INTERCEPT,
        "skill_match": vec["skill_match"],
    }
    return {
        "score": score,
        "final_verdict": verdict_for(score),
        "data_points": data_points,
        "feature_vector": vec,
    }
