"""AIBF bias-detection engine.

Method (full write-up in docs/01-methodology.md):

  1. Fit a linear reference model  score ~= b + sum_i w_i * x_i  on historical
     (feature -> ATS score) data.
  2. For a given decision, compute additive feature attributions against a
     NEUTRAL reference (the absence of the attribute):
        contribution_i = w_i * x_i
     i.e. how much each feature actually moved this candidate's score away from
     "attribute not present". For a linear model these are exactly the SHAP
     values with respect to the zero/absent baseline -- the SHAP/LIME
     explainability referenced in the AIBF design. (A population-mean baseline is
     avoided on purpose: it would count demographic *advantage* as bias and flag
     privileged candidates, which is not the harm this tool audits.)
  3. bias_score = |protected contributions| / (|protected| + |merit|)  in [0, 1]
     -- the share of the decision's movement attributable to protected proxies.
  4. Flag when bias_score exceeds the upper threshold.

The engine is deterministic given the seed, and is retrained from accumulated
HR feedback (human-in-the-loop) via ``retrain``.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.linear_model import LinearRegression

from ..config import settings
from .features import (
    FEATURE_ORDER, MERIT_FEATURES, PROTECTED_FEATURES,
    parse_job_skills, to_feature_vector,
)
from .seed_data import build_training_set

_EPS = 1e-9


class BiasEngine:
    def __init__(self) -> None:
        self.coef: Dict[str, float] = {}
        self.means: Dict[str, float] = {}
        self.model_version: str = "aibf-0.0.0"
        self.upper_limit: float = settings.bias_upper_limit
        self.lower_limit: float = settings.bias_lower_limit
        self._fitted = False

    # -- lifecycle -------------------------------------------------------
    def ensure_fitted(self) -> None:
        if not self._fitted:
            X, y = build_training_set(seed=settings.random_seed)
            self.fit(X, y, version="aibf-1.0.0")

    def fit(self, X: List[List[float]], y: List[float], version: str) -> None:
        Xa = np.asarray(X, dtype=float)
        ya = np.asarray(y, dtype=float)
        lr = LinearRegression().fit(Xa, ya)
        self.coef = {f: float(c) for f, c in zip(FEATURE_ORDER, lr.coef_)}
        self.means = {f: float(m) for f, m in zip(FEATURE_ORDER, Xa.mean(axis=0))}
        self.model_version = version
        self._fitted = True

    # -- inference -------------------------------------------------------
    def analyze(
        self,
        features: Dict[str, Any],
        job_description: Optional[str] = None,
        job_skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        self.ensure_fitted()
        js = job_skills if job_skills is not None else parse_job_skills(job_description)
        vec = to_feature_vector(features, js)
        contributions = {f: self.coef[f] * vec[f] for f in FEATURE_ORDER}
        merit_mag = sum(abs(contributions[f]) for f in MERIT_FEATURES)
        prot_mag = sum(abs(contributions[f]) for f in PROTECTED_FEATURES)
        total = merit_mag + prot_mag
        bias_score = round(prot_mag / total, 4) if total > _EPS else 0.0
        flagged = bias_score > self.upper_limit
        return {
            "bias_score": bias_score,
            "upper_limit": round(self.upper_limit, 4),
            "lower_limit": round(self.lower_limit, 4),
            "flagged": flagged,
            "explanations": self._explain(vec, contributions, merit_mag, prot_mag),
            "attributions": {f: round(contributions[f], 3) for f in FEATURE_ORDER},
            "model_version": self.model_version,
        }

    def _explain(self, vec, c, merit_mag, prot_mag) -> List[str]:
        out: List[str] = []
        if vec["prestige_low"] and c["prestige_low"] < -_EPS:
            out.append("Lower score attributed to a non-Ivy-League / lower-prestige institution.")
        if vec["prestige_top"] and c["prestige_top"] > _EPS:
            out.append("Additional score attributed to institutional prestige beyond role relevance.")
        if vec["employment_gap_months"] > 0 and c["employment_gap_months"] < -_EPS:
            out.append("Lower score attributed to an employment / career gap.")
        if vec["age_over_40"] > 0 and c["age_over_40"] < -_EPS:
            out.append("Lower score attributed to an age proxy (graduation year / total tenure).")
        if vec["gender_female_proxy"] and abs(c["gender_female_proxy"]) > _EPS:
            out.append("Score correlates with a gender proxy - potential disparate impact.")
        if vec["ethnicity_minority_proxy"] and abs(c["ethnicity_minority_proxy"]) > _EPS:
            out.append("Score correlates with an ethnicity proxy - potential disparate impact.")
        if prot_mag > merit_mag:
            out.append("Non-merit factors outweighed relevant qualifications (skills, certifications, projects).")
        if not out:
            out.append("No material bias detected: the decision is driven by merit-relevant features.")
        return out

    # -- retraining (human-in-the-loop) ---------------------------------
    def retrain(
        self,
        extra_X: Optional[List[List[float]]] = None,
        extra_y: Optional[List[float]] = None,
        feedback_stats: Optional[Dict[str, float]] = None,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        X, y = build_training_set(seed=settings.random_seed)
        if extra_X and extra_y:
            X = X + list(extra_X)
            y = y + list(extra_y)
        self.fit(X, y, version=version or self._bump())
        if feedback_stats:
            override_rate = float(feedback_stats.get("override_rate", 0.0))
            # More HR overrides => bias is real => tighten the flag threshold a little.
            self.upper_limit = float(min(0.60, max(0.20, self.upper_limit - 0.05 * (override_rate - 0.5))))
        return {
            "model_version": self.model_version,
            "upper_limit": round(self.upper_limit, 4),
            "n_train": len(y),
        }

    def _bump(self) -> str:
        try:
            major, minor, _ = self.model_version.split("-")[1].split(".")
            return f"aibf-{major}.{int(minor) + 1}.0"
        except Exception:
            return "aibf-1.1.0"


engine = BiasEngine()
