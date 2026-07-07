# 01 — Bias-Detection Methodology

This is the defensible core of the project. It explains exactly how AIBF turns
an ATS decision into a bias score, an explanation, and a flag.

## 1. Feature model

Each resume is encoded into two disjoint groups of features
(`app/services/features.py`):

- **Merit features** — a fair scorer *may* use these:
  `skill_match`, `relevant_experience`, `certifications`, `projects`.
- **Protected-proxy features** — a fair scorer must *not* let these drive the
  outcome: `prestige_top`, `prestige_low` (institution prestige),
  `employment_gap_months`, `age_over_40` (age proxy), and two demographic
  proxies (`gender_female_proxy`, `ethnicity_minority_proxy`) used **only** to
  measure disparate impact.

## 2. Reference model

AIBF fits a linear reference model on historical `(features → ATS score)` data:

```
score ≈ b + Σ_i  w_i · x_i
```

Because the relationship is linear, the fit recovers the effective weight the
ATS places on each feature — including the weight on protected proxies. (In the
bundled demo the reference model recovers the simulated ATS weights to within
~1%.)

## 3. Attribution (explainability)

For a given decision, AIBF attributes the score to each feature against a
**neutral reference — the absence of the attribute**:

```
contribution_i = w_i · x_i
```

For a linear model, these are exactly the **SHAP values with respect to the
zero/absent baseline** — the SHAP/LIME explainability the AIBF design calls for.
A population-mean baseline is deliberately *not* used: it would attribute
"bias" to a candidate simply for being demographically advantaged, which is not
the harm this tool audits.

## 4. Bias score

```
bias_score = |protected contributions| / ( |protected| + |merit| )      ∈ [0, 1]
```

It answers: *what share of this decision's score-movement came from
protected-proxy features?* A resume the ATS scored purely on merit has
`bias_score ≈ 0`; a resume penalised (or boosted) largely through protected
proxies has a high `bias_score`.

## 5. Flagging

A decision is **flagged** when `bias_score > upper_limit` (default `0.30`,
configurable). The `lower_limit` marks a "watch" band. Thresholds are
recalibrated during retraining from HR feedback.

## 6. Explanations

From the signed protected-feature contributions, AIBF emits plain-language
reasons, e.g. *"Lower score attributed to a non-Ivy-League / lower-prestige
institution"* or *"Score correlates with an age proxy."* These map directly to
the "Generated Summaries" surface in the AIBF prototype.

## 7. Human-in-the-loop retraining

HR accept/override decisions are stored. `retrain`:
1. refits the reference model on the seed set plus accumulated logged decisions;
2. recalibrates `upper_limit` from the HR **override rate** (more overrides ⇒ the
   flags were right ⇒ tighten the threshold), bounded to `[0.20, 0.60]`;
3. bumps the model version.

## Assumptions & limits (stated honestly)

- **Linearity.** The zero-baseline SHAP identity holds exactly only for the
  linear reference model. A non-linear ATS would need kernel/tree SHAP; the
  attribution *interface* is unchanged but the exactness claim weakens.
- **Proxy coverage.** AIBF audits the proxies it encodes. Unmodeled proxies
  (e.g. name-based inferences, zip code) are not covered unless added.
- **Demographic inference.** Real deployments should prefer self-reported,
  consented demographic data over inference for disparate-impact measurement.
- **Not a legal determination.** A high bias score is a signal for human review,
  not a finding of unlawful discrimination.
