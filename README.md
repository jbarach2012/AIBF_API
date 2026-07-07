# AI Bias Firewall (AIBF)

**A plug-in, explainable bias-detection layer for Applicant Tracking Systems.**
AIBF intercepts an ATS scoring decision, measures how much of it was driven by
protected-attribute proxies rather than merit, explains why in plain language,
flags biased decisions for human review, and learns from HR feedback.

![tests](https://github.com/jbarach2012/AIBF_API/actions/workflows/ci.yml/badge.svg)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Implements the OpenAPI contract in [`openapi/aibf.yaml`](openapi/aibf.yaml).

---

## Quickstart

```bash
git clone https://github.com/jbarach2012/AIBF_API
cd aibf
pip install -r requirements.txt

python -m app.services.pipeline_demo      # see a biased resume flagged, a clean one not
pytest -q                                 # run the test suite (10 checks)
uvicorn app.main:app --reload             # then open http://localhost:8000/docs
```

Demo output (abridged):

```
res_demo_biased: ATS score=... verdict=rejected
    bias_score=0.34  flagged=True
      - Lower score attributed to a non-Ivy-League / lower-prestige institution.
      - Lower score attributed to an employment / career gap.
      - Lower score attributed to an age proxy ...
res_demo_clean:  bias_score=0.0  flagged=False
      - No material bias detected: driven by merit-relevant features.
```

## How it works (one paragraph)

AIBF fits a linear reference model to historical `(features → ATS score)` data,
then attributes each decision's score to its features against a *neutral
(attribute-absent) baseline*. For a linear model these attributions are exactly
SHAP values. The **bias score** is the share of the decision's score-movement
coming from protected-proxy features; decisions above a threshold are flagged
with plain-language explanations. HR feedback retrains the model and recalibrates
the threshold. Full method: [`docs/01-methodology.md`](docs/01-methodology.md).

## API surface

| Method & path | Purpose |
|---|---|
| `POST /api/resumes` | submit a resume; runs ATS + AIBF; returns decision + flag |
| `GET  /api/resumes` | list resumes (`?status=flagged\|active`) |
| `POST /api/ats/evaluate` | ATS score + data points |
| `POST /api/aibf/analyze` | bias score + explanation + attribution |
| `POST /api/admin/feedback` | HR accept/override feedback |
| `POST /api/model-training/retrain` | refit + recalibrate |
| `GET  /api/admin/flagged` | flagged-decision review feed |
| `GET  /health` | status + model version |

Curl examples: [`docs/03-api.md`](docs/03-api.md).

## How this helps people

- **HR-tech vendors / teams** get a drop-in audit layer that turns each opaque
  ATS decision into an explainable, flaggable artifact — without changing the ATS.
- **HR reviewers** get plain-language reasons and a correction path, not a black box.
- **Candidates** benefit from decisions that can be contested and corrected.
- **The community** gets an open, Apache-2.0, method-documented bias detector
  built on synthetic data, so the approach can be adopted and improved rather
  than rebuilt behind closed doors.

## Data & privacy

No real candidate data ships with this project. Training and demo data are
synthetic and deterministic (`app/services/seed_data.py`). Demographic signals
are used **only** to measure disparate impact, never to score. See
[`docs/00-overview.md`](docs/00-overview.md).

## Docs

[Overview](docs/00-overview.md) · [Methodology](docs/01-methodology.md) ·
[Architecture](docs/02-architecture.md) · [API guide](docs/03-api.md) ·
[Roadmap](ROADMAP.md)

## License

[Apache 2.0](LICENSE). See [`CITATION.cff`](CITATION.cff) to cite the project.

> **Note:** AIBF produces a *signal for human review*, not a legal determination
> of discrimination. The bundled ATS scorer is simulated so the detector has a
> realistic decision to audit; in production, feed AIBF a real ATS's outputs.
