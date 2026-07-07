def test_ats_evaluate_returns_data_points(client):
    client.post("/api/resumes", json={"resume_id": "res_ats_1", "candidate_id": "c1"})
    r = client.post("/api/ats/evaluate",
                    json={"resume_id": "res_ats_1", "job_description": "python sql aws ml role"})
    assert r.status_code == 200
    body = r.json()
    assert body["ats_decision_id"].startswith("ats_")
    assert "contributions" in body["data_points"]
    assert 0 <= body["score"] <= 100
