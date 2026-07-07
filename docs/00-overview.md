# 00 — Overview

## What AIBF is

The **AI Bias Firewall (AIBF)** is a plug-in bias-detection layer for Applicant
Tracking Systems. It intercepts an ATS's scoring decision for a candidate,
measures how much of that decision was driven by **protected-attribute proxies**
(institutional prestige, employment gaps, an age proxy, and demographic
proxies) rather than merit, produces a **bias score** with a plain-language
**explanation**, and **flags** decisions that cross a threshold for human review.
HR feedback on flagged decisions is fed back to **retrain and recalibrate** the
detector.

It is designed to sit alongside an ATS through a small HTTP API (see
`openapi/aibf.yaml`) without requiring changes to the ATS itself.

## Why it matters

Opaque, unaudited AI screening is the most legally active risk area in HR-tech:
documented cases include age, sex, race, and disability discrimination by
automated screeners, with almost no transparency to candidates. The recurring
gap is that bias testing is self-reported, point-in-time, and non-comparable.
AIBF turns each individual decision into an auditable, explainable artifact and
provides a human-in-the-loop correction path.

## The pipeline

```
Candidate ─▶ ATS evaluate ─▶ AIBF analyze ─▶ flagged? ─▶ HR review ─▶ retrain
             (score,          (bias score,     if yes      (accept /    (model +
              verdict,         explanation,                 override)    threshold
              data points)     attribution)                              recalibrated)
```

## What's in this repo

```
app/            the runnable service (FastAPI) implementing openapi/aibf.yaml
  services/     the analytical core: features, ATS engine, bias engine, seed data
  routers/      the five API endpoints + an admin flagged-feed
openapi/        the API contract (unchanged from the project's original spec)
docs/           methodology, architecture, API guide, diagrams
tests/          end-to-end tests (biased resume flags, clean resume does not)
```

## Data & privacy stance

AIBF ships with **no real candidate data**. All training and demo data is
synthetic (`app/services/seed_data.py`) and deterministic. Demographic signals
are used **only** to measure disparate impact — never as an input to any score.
This mirrors the standard practice for fairness tooling: demonstrate on
synthetic / public-benchmark data, keep any real candidate data private.

## Honest scope

This is a **reference implementation with a defensible method**, not a
production compliance product. The ATS scorer here is simulated so the detector
has a realistic decision to audit; in production AIBF consumes a real ATS's
outputs. See `docs/01-methodology.md` for the method, its assumptions, and its
limits.
