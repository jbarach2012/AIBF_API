# Changelog

Semantic versioning.

## [1.0.0]
### Added
- OpenAPI contract implemented end-to-end (resumes, ATS evaluate, AIBF analyze,
  HR feedback, model retraining) plus an admin flagged-feed and health check.
- Bias-detection engine: linear reference model, zero-baseline SHAP attributions,
  bias score, thresholds, explanations, flagging.
- Human-in-the-loop retraining with feedback-driven threshold recalibration.
- Synthetic, deterministic training/demo data (no real PII).
- Test suite (10 checks), runnable pipeline demo, Docker/Compose, docs.
