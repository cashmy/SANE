from sqlalchemy import select

from app.models import Decision


def test_list_candidates_returns_seeded_review_queue(client) -> None:
    response = client.get("/api/candidates")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 5
    assert any(
        item["classifier_signal"] == "ambiguous_source" for item in payload["items"]
    )
    assert all(
        item["processing_state"] == "pending_review" for item in payload["items"]
    )


def test_create_decision_requires_confirmation(client) -> None:
    candidates = client.get("/api/candidates").json()["items"]

    response = client.post(
        "/api/decisions",
        json={
            "candidate_id": candidates[0]["id"],
            "decision": "mark_low_value",
            "confirmed": False,
        },
    )

    decisions = client.get("/api/decisions").json()["items"]

    assert response.status_code == 400
    assert "human confirmation" in response.json()["detail"].lower()
    assert decisions == []


def test_create_decision_persists_locally(client, db_session) -> None:
    candidates = client.get("/api/candidates").json()["items"]
    candidate_id = candidates[0]["id"]

    create_response = client.post(
        "/api/decisions",
        json={
            "candidate_id": candidate_id,
            "decision": "unsubscribe_later",
            "confirmed": True,
            "note": "Recommend later action, but do not execute.",
        },
    )
    history_response = client.get("/api/decisions")

    db_session.expire_all()
    persisted_decision = db_session.scalar(
        select(Decision).where(Decision.candidate_id == candidate_id)
    )

    assert create_response.status_code == 201
    assert history_response.status_code == 200
    assert persisted_decision is not None
    assert persisted_decision.external_action_status.value == "not_executed"
    assert history_response.json()["items"][0]["candidate"]["id"] == candidate_id
    assert (
        history_response.json()["items"][0]["candidate"]["processing_state"]
        == "action_recommended"
    )


def test_candidate_response_stays_inside_stage_one_boundary(client) -> None:
    payload = client.get("/api/candidates").json()["items"][0]

    assert "account_id" not in payload
    assert "subscription_tier" not in payload
    assert "gtd_status" not in payload
