from tests.conftest import BIASED


def test_submit_hr_feedback(client):
    sub = client.post("/api/resumes", json={"resume_id": "res_fb_1", "features": BIASED}).json()
    an = client.post("/api/aibf/analyze",
                     json={"ats_decision_id": sub["ats_decision_id"], "resume_id": "res_fb_1"}).json()
    r = client.post("/api/admin/feedback", json={
        "feedback_type": "override", "hr_id": "hr_1",
        "ats_decision_id": sub["ats_decision_id"], "aibf_decision_id": an["aibf_decision_id"],
        "feedback_details": "Agree with AIBF; overriding ATS rejection.",
        "final_verdict": "override",
    })
    assert r.status_code == 201
    assert r.json()["model_training_feedback_id"].startswith("mtf_")
    assert r.json()["training_outcome"] == "recorded"
