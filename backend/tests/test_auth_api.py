from app.core.security import OAUTH_STATE_COOKIE_NAME, SESSION_COOKIE_NAME


def test_me_returns_401_when_unauthenticated(client) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_returns_current_user(auth_client) -> None:
    response = auth_client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "local-alpha@sane.local"
    assert response.json()["is_local_alpha"] is True


def test_logout_clears_the_current_session(auth_client) -> None:
    response = auth_client.post("/api/auth/logout")
    auth_client.cookies.clear()
    follow_up = auth_client.get("/api/auth/me")

    assert response.status_code == 204
    assert "Max-Age=0" in response.headers.get("set-cookie", "")
    assert follow_up.status_code == 401


def test_google_login_returns_501_when_not_configured(client) -> None:
    response = client.get("/api/auth/google/login", follow_redirects=False)

    assert response.status_code == 501


def test_google_callback_sets_session_cookie_and_redirects(client, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routers.auth.exchange_google_code",
        lambda code: {"id_token": f"token-for-{code}"},
    )
    monkeypatch.setattr(
        "app.routers.auth.verify_google_id_token",
        lambda _token: {
            "sub": "google-sub-5",
            "email": "person@example.com",
            "email_verified": True,
            "name": "Person Example",
        },
    )

    client.cookies.set(OAUTH_STATE_COOKIE_NAME, "signed-state")
    response = client.get(
        "/api/auth/google/callback?code=abc123&state=signed-state",
        follow_redirects=False,
    )

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "http://localhost:5173"
    assert SESSION_COOKIE_NAME in response.headers.get("set-cookie", "")
