# 03 — API Guide

Contract: `openapi/aibf.yaml`. Interactive docs at `/docs` when the server runs.
Base URL below assumes local `http://localhost:8000`.

## Submit a resume (runs the full pipeline)
```bash
curl -s -X POST localhost:8000/api/resumes -H 'content-type: application/json' -d '{
  "resume_id": "res_1", "candidate_id": "cand_1",
  "job_description": "python sql aws docker ml engineer",
  "features": {"skills":["python","sql","aws"],"relevant_experience":9,
               "certifications":3,"projects":4,"education_tier":3,
               "employment_gap_months":18,"age":55,"gender":"F","ethnicity":"black"}
}'
# -> { ats_decision_id, candidate_id, score, final_verdict, flagged, bias_score }
```
> `features` and `job_description` are optional extensions beyond the base spec;
> omit them and AIBF synthesizes deterministic features from `resume_id`.

## Evaluate ATS only
```bash
curl -s -X POST localhost:8000/api/ats/evaluate -H 'content-type: application/json' \
  -d '{"resume_id":"res_1","job_description":"python sql aws ml"}'
# -> { ats_decision_id, candidate_id, data_points, score, final_verdict }
```

## Analyze bias only
```bash
curl -s -X POST localhost:8000/api/aibf/analyze -H 'content-type: application/json' \
  -d '{"ats_decision_id":"ats_...","resume_id":"res_1"}'
# -> { aibf_decision_id, bias_score, bias_threshold_limits, flagged, explanations, attributions }
```

## HR feedback
```bash
curl -s -X POST localhost:8000/api/admin/feedback -H 'content-type: application/json' -d '{
  "feedback_type":"override","hr_id":"hr_1",
  "ats_decision_id":"ats_...","aibf_decision_id":"aibf_...",
  "feedback_details":"Agree with AIBF; overriding ATS rejection.","final_verdict":"override"
}'
# -> { model_training_feedback_id, ats_output, aibf_output, training_outcome }
```

## Retrain
```bash
curl -s -X POST localhost:8000/api/model-training/retrain -H 'content-type: application/json' \
  -d '{"feedback_id":null}'
# -> { model_training_feedback_id, ats_output, aibf_output, training_outcome }
```

## Convenience / meta
- `GET /api/resumes` — list resumes; `?status=flagged|active` to filter
- `GET /api/admin/flagged` — flagged decisions with explanations (review feed)
- `GET /health` — status + current model version
