"""Test fixtures. A fresh temp SQLite DB per test session; the app lifespan
trains the model and seeds the two demo resumes."""
import os
import tempfile

import pytest


@pytest.fixture(scope="session")
def client():
    tmpdir = tempfile.mkdtemp()
    os.environ["AIBF_DATABASE_URL"] = f"sqlite:///{tmpdir}/test.db"
    os.environ["AIBF_SEED_DEMO"] = "1"
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:  # entering the context runs the lifespan startup
        yield c


# strongly biased vs clean resume payloads reused across tests
BIASED = {
    "skills": ["python", "sql", "aws", "docker", "ml"],
    "relevant_experience": 9, "certifications": 3, "projects": 4,
    "education_tier": 3, "employment_gap_months": 18,
    "age": 55, "gender": "F", "ethnicity": "black",
}
CLEAN = {
    "skills": ["python", "sql", "aws"],
    "relevant_experience": 6, "certifications": 2, "projects": 3,
    "education_tier": 2, "employment_gap_months": 0,
    "age": 31, "gender": "M", "ethnicity": "white",
}
