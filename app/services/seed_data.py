"""Synthetic historical training data.

No real PII -- every record is fabricated. A fixed seed makes training and every
bias score fully reproducible.
"""
from __future__ import annotations

import random
from typing import Dict, List, Tuple

from .ats_engine import _clip, raw_score
from .features import DEFAULT_JOB_SKILLS, SKILL_VOCAB, to_feature_vector, vector_list


def _random_resume(rng: random.Random) -> Dict:
    n = rng.randint(2, 7)
    return {
        "skills": rng.sample(SKILL_VOCAB, n),
        "relevant_experience": round(rng.uniform(0, 12), 1),
        "certifications": rng.randint(0, 5),
        "projects": rng.randint(0, 6),
        "education_tier": rng.choice([1, 2, 2, 3, 3]),
        "employment_gap_months": rng.choice([0, 0, 0, 3, 6, 12, 18, 24]),
        "age": rng.randint(24, 62),
        "gender": rng.choice(["M", "M", "F", "F", "U"]),
        "ethnicity": rng.choice(["white", "asian", "black", "hispanic", "native", "mena"]),
    }


def build_training_set(n: int = 500, seed: int = 42) -> Tuple[List[List[float]], List[float]]:
    rng = random.Random(seed)
    X: List[List[float]] = []
    y: List[float] = []
    for _ in range(n):
        feats = _random_resume(rng)
        vec = to_feature_vector(feats, DEFAULT_JOB_SKILLS)
        score = _clip(raw_score(vec) + rng.gauss(0, 1.5))
        X.append(vector_list(vec))
        y.append(score)
    return X, y


def demo_resumes() -> List[Dict]:
    """Two labelled demo resumes: one the biased ATS penalises via protected
    proxies (should be flagged), one it scores cleanly (should not)."""
    return [
        {
            "resume_id": "res_demo_biased",
            "candidate_id": "cand_demo_1",
            "features": {
                "skills": ["python", "sql", "aws", "docker", "ml"],
                "relevant_experience": 9, "certifications": 3, "projects": 4,
                "education_tier": 3, "employment_gap_months": 18,
                "age": 55, "gender": "F", "ethnicity": "black",
            },
        },
        {
            "resume_id": "res_demo_clean",
            "candidate_id": "cand_demo_2",
            "features": {
                "skills": ["python", "sql", "aws"],
                "relevant_experience": 6, "certifications": 2, "projects": 3,
                "education_tier": 2, "employment_gap_months": 0,
                "age": 31, "gender": "M", "ethnicity": "white",
            },
        },
    ]
