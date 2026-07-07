def test_submit_resume_returns_ats_decision(client):
    r = client.post("/api/resumes", json={"candidate_id": "cand_x", "file_url": "s3://x"})
    assert r.status_code == 201
    body = r.json()
    assert body["ats_decision_id"].startswith("ats_")
    assert 0 <= body["score"] <= 100
    assert body["final_verdict"] in {"accepted", "review", "rejected"}


def test_list_resumes_includes_seeded(client):
    r = client.get("/api/resumes")
    assert r.status_code == 200
    ids = {x["resume_id"] for x in r.json()}
    assert "res_demo_biased" in ids and "res_demo_clean" in ids


def test_flagged_filter_returns_biased_only(client):
    flagged = client.get("/api/resumes", params={"status": "flagged"}).json()
    ids = {x["resume_id"] for x in flagged}
    assert "res_demo_biased" in ids
    assert "res_demo_clean" not in ids
