"""Runtime configuration. Overridable via environment variables."""
from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "AI Bias Firewall (AIBF)"
    version: str = "1.0.0"
    database_url: str = os.getenv("AIBF_DATABASE_URL", "sqlite:///./aibf.db")
    # Fraction of an ATS decision's score-movement that may come from protected
    # proxies before the decision is flagged (see docs/01-methodology.md).
    bias_upper_limit: float = float(os.getenv("AIBF_BIAS_UPPER", "0.30"))
    bias_lower_limit: float = float(os.getenv("AIBF_BIAS_LOWER", "0.15"))
    random_seed: int = int(os.getenv("AIBF_SEED", "42"))
    seed_demo_data: bool = os.getenv("AIBF_SEED_DEMO", "1") == "1"


settings = Settings()
