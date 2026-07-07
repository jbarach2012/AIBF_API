# 02 — Architecture

## Components

```
                         ┌──────────────────────────────────────────┐
  HTTP (openapi/aibf.yaml)│               FastAPI app                │
  ─────────────────────▶ │  routers/  resumes · ats · aibf · admin  │
                         │            · model-training              │
                         └───────┬───────────────┬──────────────────┘
                                 │               │
                    ┌────────────▼───┐   ┌───────▼─────────────────┐
                    │  services/     │   │  SQLAlchemy models      │
                    │  features.py   │   │  Resume · ATSDecision   │
                    │  ats_engine.py │   │  AIBFDecision           │
                    │  bias_engine.py│   │  HRFeedback             │
                    │  seed_data.py  │   │  ModelTrainingFeedback  │
                    └────────────────┘   └───────┬─────────────────┘
                                                 │
                                          SQLite / any SQL DB
```

Diagrams (Mermaid source in `docs/diagrams/`, rendered natively by GitHub):
`pipeline.mmd`, `sequence.mmd`.

## Request flow (submit a resume)

1. `POST /api/resumes` stores the resume and its (possibly synthesized) features.
2. The **ATS engine** scores it → `ATSDecision` (score, verdict, data points).
3. The **bias engine** analyses it → `AIBFDecision` (bias score, flag,
   explanations, attributions).
4. The response returns the ATS decision plus the AIBF flag.

`POST /api/ats/evaluate` and `POST /api/aibf/analyze` expose steps 2 and 3
individually, matching the OpenAPI contract.

## Persistence

Five tables track the full lineage from resume to retraining, so every flag is
auditable (who, which decision, which explanation, which model version). SQLite
by default; point `AIBF_DATABASE_URL` at Postgres/MySQL for production.

## Configuration (env vars)

| Variable | Default | Meaning |
|----------|---------|---------|
| `AIBF_DATABASE_URL` | `sqlite:///./aibf.db` | database connection |
| `AIBF_BIAS_UPPER` | `0.30` | flag threshold |
| `AIBF_BIAS_LOWER` | `0.15` | watch-band threshold |
| `AIBF_SEED` | `42` | RNG seed (determinism) |
| `AIBF_SEED_DEMO` | `1` | seed two demo resumes on startup |

## Swappable pieces

- The **ATS engine** is simulated; in production, delete it and feed AIBF a real
  ATS's score + data points via `POST /api/aibf/analyze`.
- The linear **reference model** can be replaced with a tree/kernel model plus
  the corresponding SHAP explainer without changing the API surface.
