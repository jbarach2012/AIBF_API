def test_retrain_bumps_model_version(client):
    before = client.get("/health").json()["model_version"]
    r = client.post("/api/model-training/retrain", json={"feedback_id": None})
    assert r.status_code == 200
    body = r.json()
    assert body["training_outcome"] == "success"
    assert body["model_training_feedback_id"].startswith("mtf_")
    after = client.get("/health").json()["model_version"]
    assert after != before  # version advanced


def test_retrain_with_explicit_version(client):
    r = client.post("/api/model-training/retrain", json={"model_version": "aibf-2.0.0"})
    assert r.status_code == 200
    assert client.get("/health").json()["model_version"] == "aibf-2.0.0"
