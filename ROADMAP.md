# Roadmap

## Phase 0 — Foundation (this release, v1.0)
- [x] OpenAPI contract implemented end-to-end (`openapi/aibf.yaml`)
- [x] Feature model splitting merit vs protected-proxy signals
- [x] Linear reference model + zero-baseline (SHAP) attributions
- [x] Bias score, thresholds, plain-language explanations, flagging
- [x] HR feedback + human-in-the-loop retraining and threshold recalibration
- [x] Synthetic, deterministic training/demo data (no real PII)
- [x] Test suite + runnable pipeline demo

## Phase 1 — Explainability depth (v1.1)
- [ ] Pluggable non-linear reference models with kernel/tree SHAP.
- [ ] Counterfactual explanations ("would not have been flagged if …").
- [ ] Proxy-variable detection for name/zip-code style leakage.

## Phase 2 — Standards mapping (v1.2)
- [ ] Map bias scores to the four-fifths (80%) rule and impact-ratio reporting.
- [ ] Exportable, machine-readable audit reports (JSON + human summary).
- [ ] Alignment notes for NYC Local Law 144 and EU AI Act Article 10 obligations.

## Phase 3 — Integrations (v1.3)
- [ ] Adapters to consume real ATS outputs (Greenhouse/Lever/iCIMS-style APIs).
- [ ] Consented, self-reported demographic ingestion (replacing inference).
- [ ] Reviewer UI for the flagged-decision feed.

## Phase 4 — Continuous auditing (v2.0)
- [ ] Scheduled re-audits with model-drift and protected-class coverage checks.
- [ ] Dashboards for population-level disparate-impact trends over time.

## Non-goals
- Making legal determinations of discrimination.
- Shipping or storing real candidate PII in the open-source core.
