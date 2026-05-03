from sqlalchemy import select

from app.models import Decision, User
from app.models.email_account import EmailAccount
from app.models.enums import EmailAccountProvider


def test_list_sources_returns_paginated_source_rows(auth_client) -> None:
    response = auth_client.get("/api/sources?page=1&page_size=3")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"]["page"] == 1
    assert payload["pagination"]["page_size"] == 3
    assert payload["pagination"]["total_items"] == 8
    assert payload["pagination"]["total_pages"] == 3
    assert len(payload["items"]) == 3
    assert payload["items"][0]["email_count"] >= payload["items"][1]["email_count"]
    assert len(payload["items"][0]["sender_emails"]) >= 1
    assert any(
        item["classifier_signal"] == "ambiguous_source" for item in payload["items"]
    )
    assert all(
        item["processing_state"] == "pending_review" for item in payload["items"]
    )


def test_source_pagination_respects_page_size_and_page(auth_client) -> None:
    first_page = auth_client.get("/api/sources?page=1&page_size=2")
    second_page = auth_client.get("/api/sources?page=2&page_size=2")

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    first_payload = first_page.json()
    second_payload = second_page.json()
    assert len(first_payload["items"]) == 2
    assert len(second_payload["items"]) == 2
    assert first_payload["items"][0]["id"] != second_payload["items"][0]["id"]
    assert second_payload["pagination"]["page"] == 2


def test_create_decision_requires_confirmation(auth_client) -> None:
    sources = auth_client.get("/api/sources").json()["items"]

    response = auth_client.post(
        "/api/decisions",
        json={
            "source_id": sources[0]["id"],
            "decision": "mark_low_value",
            "confirmed": False,
        },
    )

    decisions = auth_client.get("/api/decisions").json()["items"]

    assert response.status_code == 400
    assert "human confirmation" in response.json()["detail"].lower()
    assert decisions == []


def test_create_decision_persists_locally(auth_client, db_session) -> None:
    sources = auth_client.get("/api/sources").json()["items"]
    source_id = sources[0]["id"]

    create_response = auth_client.post(
        "/api/decisions",
        json={
            "source_id": source_id,
            "decision": "unsubscribe_later",
            "confirmed": True,
            "note": "Recommend later action, but do not execute.",
        },
    )
    history_response = auth_client.get("/api/decisions")

    db_session.expire_all()
    persisted_decision = db_session.scalar(
        select(Decision).where(Decision.candidate_id == source_id)
    )
    owner = db_session.scalar(select(User).where(User.is_local_alpha.is_(True)))

    assert create_response.status_code == 201
    assert history_response.status_code == 200
    assert persisted_decision is not None
    assert owner is not None
    assert persisted_decision.user_id == owner.id
    assert persisted_decision.external_action_status.value == "not_executed"
    assert history_response.json()["pagination"]["page"] == 1
    assert history_response.json()["pagination"]["page_size"] == 5
    assert history_response.json()["items"][0]["source"]["id"] == source_id
    assert (
        history_response.json()["items"][0]["source"]["processing_state"]
        == "action_recommended"
    )
    assert history_response.json()["items"][0]["is_current"] is True


def test_repeating_the_same_decision_returns_the_current_history_event(
    auth_client,
) -> None:
    sources = auth_client.get("/api/sources").json()["items"]
    source_id = sources[0]["id"]

    first = auth_client.post(
        "/api/decisions",
        json={
            "source_id": source_id,
            "decision": "mark_low_value",
            "confirmed": True,
        },
    )
    second = auth_client.post(
        "/api/decisions",
        json={
            "source_id": source_id,
            "decision": "mark_low_value",
            "confirmed": True,
        },
    )
    history = auth_client.get("/api/decisions").json()

    assert first.status_code == 201
    assert second.status_code == 200
    assert len(history["items"]) == 1
    assert history["pagination"]["total_items"] == 1
    assert history["items"][0]["decision"] == "mark_low_value"


def test_revision_appends_a_new_history_event(auth_client) -> None:
    sources = auth_client.get("/api/sources").json()["items"]
    source_id = sources[0]["id"]

    first = auth_client.post(
        "/api/decisions",
        json={
            "source_id": source_id,
            "decision": "keep_for_now",
            "confirmed": True,
        },
    )
    second = auth_client.post(
        "/api/decisions",
        json={
            "source_id": source_id,
            "decision": "mark_low_value",
            "confirmed": True,
        },
    )
    history = auth_client.get("/api/decisions").json()["items"]

    assert first.status_code == 201
    assert second.status_code == 201
    assert len(history) == 2
    assert history[0]["decision"] == "mark_low_value"
    assert history[0]["is_revision"] is True
    assert history[0]["is_current"] is True
    assert history[0]["revised_from_decision_id"] == history[1]["id"]
    assert history[1]["is_current"] is False


def test_decisions_pagination_respects_page_size_and_page(auth_client) -> None:
    sources = auth_client.get("/api/sources?page=1&page_size=3").json()["items"]

    for source in sources:
        response = auth_client.post(
            "/api/decisions",
            json={
                "source_id": source["id"],
                "decision": "mark_low_value",
                "confirmed": True,
            },
        )
        assert response.status_code == 201

    first_page = auth_client.get("/api/decisions?page=1&page_size=2")
    second_page = auth_client.get("/api/decisions?page=2&page_size=2")

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    first_payload = first_page.json()
    second_payload = second_page.json()
    assert len(first_payload["items"]) == 2
    assert len(second_payload["items"]) == 1
    assert first_payload["pagination"]["page"] == 1
    assert first_payload["pagination"]["page_size"] == 2
    assert first_payload["pagination"]["total_items"] == 3
    assert first_payload["items"][0]["id"] != second_payload["items"][0]["id"]


def test_source_and_decision_lists_accept_email_account_filter(
    auth_client, db_session
) -> None:
    seed_response = auth_client.get("/api/sources?page=1&page_size=1")
    assert seed_response.status_code == 200

    account = db_session.scalar(
        select(EmailAccount).where(
            EmailAccount.provider == EmailAccountProvider.local_alpha
        )
    )
    assert account is not None

    sources = auth_client.get(
        f"/api/sources?email_account_id={account.id}&page=1&page_size=2"
    )
    assert sources.status_code == 200
    assert len(sources.json()["items"]) == 2

    source_id = sources.json()["items"][0]["id"]
    create_response = auth_client.post(
        "/api/decisions",
        json={
            "source_id": source_id,
            "decision": "keep_for_now",
            "confirmed": True,
        },
    )
    assert create_response.status_code == 201

    decisions = auth_client.get(
        f"/api/decisions?email_account_id={account.id}&page=1&page_size=5"
    )
    assert decisions.status_code == 200
    assert decisions.json()["pagination"]["total_items"] == 1
    assert decisions.json()["items"][0]["source"]["id"] == source_id

    missing_sources = auth_client.get("/api/sources?email_account_id=999999")
    missing_decisions = auth_client.get("/api/decisions?email_account_id=999999")

    assert missing_sources.status_code == 200
    assert missing_sources.json()["items"] == []
    assert missing_sources.json()["pagination"]["total_items"] == 0
    assert missing_decisions.status_code == 200
    assert missing_decisions.json()["items"] == []
    assert missing_decisions.json()["pagination"]["total_items"] == 0


def test_batch_decision_requires_confirmation_and_stays_local(auth_client) -> None:
    sources = auth_client.get("/api/sources?page=1&page_size=3").json()["items"]
    source_ids = [item["id"] for item in sources[:2]]

    rejected = auth_client.post(
        "/api/decisions/batch",
        json={
            "source_ids": source_ids,
            "decision": "mark_low_value",
            "confirmed": False,
        },
    )
    applied = auth_client.post(
        "/api/decisions/batch",
        json={
            "source_ids": source_ids,
            "decision": "mark_low_value",
            "confirmed": True,
            "note": "Apply the same local state change to the selected sources.",
        },
    )
    history = auth_client.get("/api/decisions").json()

    assert rejected.status_code == 400
    assert applied.status_code == 200
    assert len(applied.json()["applied"]) == 2
    assert applied.json()["unchanged"] == []
    assert len(history["items"]) == 2
    assert history["pagination"]["total_items"] == 2
    assert all(
        item["external_action_status"] == "not_executed" for item in history["items"]
    )


def test_source_response_stays_inside_stage_one_boundary(auth_client) -> None:
    payload = auth_client.get("/api/sources").json()["items"][0]

    assert "user_id" not in payload
    assert "owner_id" not in payload
    assert "account_id" not in payload
    assert "email_account_id" not in payload
    assert "subscription_tier" not in payload
    assert "gtd_status" not in payload


def test_sources_unauthenticated_returns_401(client) -> None:
    response = client.get("/api/sources")

    assert response.status_code == 401


def test_decisions_unauthenticated_returns_401(client) -> None:
    response = client.get("/api/decisions")

    assert response.status_code == 401


def test_create_decision_unauthenticated_returns_401(client) -> None:
    response = client.post(
        "/api/decisions",
        json={"source_id": 1, "decision": "mark_low_value", "confirmed": True},
    )

    assert response.status_code == 401


def test_batch_decision_unauthenticated_returns_401(client) -> None:
    response = client.post(
        "/api/decisions/batch",
        json={"source_ids": [1], "decision": "mark_low_value", "confirmed": True},
    )

    assert response.status_code == 401
