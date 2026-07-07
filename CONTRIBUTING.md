# Contributing

Thanks for helping make automated hiring fairer and more transparent.

## Ground rules
- Contributions are under **Apache 2.0** (`LICENSE` / `NOTICE`).
- **Never commit real candidate data.** Use `app/services/seed_data.py`
  (synthetic, deterministic). Demographic fields are audit-only signals.
- Keep the method **defensible**: if you change scoring or attribution, update
  `docs/01-methodology.md` and add/adjust tests.

## Dev setup
```bash
pip install -r requirements.txt
pytest -q
python -m app.services.pipeline_demo
```

## Good first issues
- A kernel/tree SHAP explainer for a non-linear reference model.
- Impact-ratio (four-fifths rule) reporting on top of the bias score.
- An adapter that ingests a real ATS's decision payload.
- Rendering the Mermaid diagrams to committed SVG/PNG.

## Pull requests
1. Add/adjust a test for any behavioural change (`pytest -q` must stay green).
2. Note which endpoint or method your change touches.
