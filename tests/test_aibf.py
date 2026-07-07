from tests.conftest import BIASED, CLEAN


def _analyze(client, resume_id, features):
    sub = client.post("/api/resumes", json={"resume_id": resume_id, "features": features}).json()
    return client.post("/api/aibf/analyze",
                       json={"ats_decision_id": sub["ats_decision_id"], "resume_id": resume_id}).json()


def test_biased_resume_is_flagged_with_explanations(client):
    res = _analyze(client, "res_bias_1", BIASED)
    assert res["flagged"] is True
    assert res["bias_score"] > res["bias_threshold_limits"]["upper_limit"]
    assert len(res["explanations"]) >= 2
    assert "attributions" in res


def test_clean_resume_is_not_flagged(client):
    res = _analyze(client, "res_clean_1", CLEAN)
    assert res["flagged"] is False
    assert res["bias_score"] <= res["bias_threshold_limits"]["upper_limit"]


def test_admin_flagged_feed(client):
    _analyze(client, "res_bias_2", BIASED)
    feed = client.get("/api/admin/flagged").json()
    assert any(item["bias_score"] > 0 for item in feed)
