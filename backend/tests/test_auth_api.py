from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.security import OAUTH_STATE_COOKIE_NAME, SESSION_COOKIE_NAME
from app.models.auth_identity import AuthIdentity
from app.models.email_account import EmailAccount
from app.models.enums import EmailAccountProvider
from app.models.ingestion_run import IngestionRun
from app.models.user import User
from app.services.auth_service import GoogleIdTokenClockSkewError
from app.services.ownership import get_or_create_local_alpha_user


def _set_auth_settings(
    monkeypatch,
    *,
    auth_mode: str = "google_oauth",
    debug: bool = True,
    google_client_id: str | None = None,
    google_client_secret: str | None = None,
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "auth_mode", auth_mode)
    monkeypatch.setattr(settings, "debug", debug)
    monkeypatch.setattr(settings, "google_client_id", google_client_id)
    monkeypatch.setattr(settings, "google_client_secret", google_client_secret)


def test_auth_config_hides_local_dev_and_reports_missing_google(
    client, monkeypatch
) -> None:
    _set_auth_settings(monkeypatch)

    response = client.get("/api/auth/config")

    assert response.status_code == 200
    assert response.json() == {
        "auth_mode": "google_oauth",
        "local_dev_enabled": False,
        "google_oauth_enabled": False,
        "google_oauth_message": "Google OAuth is not configured for this local environment.",
    }


def test_local_dev_login_issues_a_valid_session_when_enabled(
    client,
    monkeypatch,
) -> None:
    _set_auth_settings(monkeypatch, auth_mode="local_dev", debug=True)

    response = client.post("/api/auth/local-dev/login")
    follow_up = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "local-alpha@sane.local"
    assert response.json()["is_local_alpha"] is True
    assert SESSION_COOKIE_NAME in response.headers.get("set-cookie", "")
    assert follow_up.status_code == 200
    assert follow_up.json()["display_name"] == "Local ALPHA User"


def test_local_dev_login_returns_404_when_disabled(client, monkeypatch) -> None:
    _set_auth_settings(monkeypatch, auth_mode="google_oauth", debug=True)

    response = client.post("/api/auth/local-dev/login")

    assert response.status_code == 404


def test_local_dev_login_returns_403_in_production_mode(client, monkeypatch) -> None:
    _set_auth_settings(monkeypatch, auth_mode="local_dev", debug=False)

    response = client.post("/api/auth/local-dev/login")

    assert response.status_code == 403


def test_local_dev_login_reuses_local_alpha_without_creating_gmail_or_runs(
    client,
    db_session,
    monkeypatch,
) -> None:
    _set_auth_settings(monkeypatch, auth_mode="local_dev", debug=True)
    user = get_or_create_local_alpha_user(db_session)
    db_session.commit()

    response = client.post("/api/auth/local-dev/login")

    db_session.expire_all()
    local_alpha_users = db_session.scalars(
        select(User).where(User.is_local_alpha.is_(True))
    ).all()
    gmail_account_count = db_session.scalar(
        select(func.count())
        .select_from(EmailAccount)
        .where(
            EmailAccount.user_id == user.id,
            EmailAccount.provider == EmailAccountProvider.gmail,
        )
    )
    run_count = db_session.scalar(
        select(func.count())
        .select_from(IngestionRun)
        .where(IngestionRun.user_id == user.id)
    )

    assert response.status_code == 200
    assert len(local_alpha_users) == 1
    assert local_alpha_users[0].id == user.id
    assert gmail_account_count == 0
    assert run_count == 0


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


def test_google_login_returns_501_when_oauth_values_are_placeholders(
    client, monkeypatch
) -> None:
    _set_auth_settings(
        monkeypatch,
        google_client_id="YOUR_GOOGLE_CLIENT_ID",
        google_client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    )

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


def test_google_callback_redirects_with_clock_skew_error_without_side_effects(
    client,
    db_session,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.routers.auth.exchange_google_code",
        lambda code: {"id_token": f"token-for-{code}"},
    )

    def raise_clock_skew(_token: str):
        raise GoogleIdTokenClockSkewError(
            "Google sign-in could not be completed because this device clock appears out of sync. Sync your system time and try again."
        )

    monkeypatch.setattr("app.routers.auth.verify_google_id_token", raise_clock_skew)

    client.cookies.set(OAUTH_STATE_COOKIE_NAME, "signed-state")
    response = client.get(
        "/api/auth/google/callback?code=abc123&state=signed-state",
        follow_redirects=False,
    )

    db_session.expire_all()

    assert response.status_code in {302, 307}
    assert (
        response.headers["location"]
        == "http://localhost:5173?auth_error=device_clock_out_of_sync"
    )
    assert SESSION_COOKIE_NAME not in response.headers.get("set-cookie", "")
    assert db_session.scalar(select(func.count()).select_from(User)) == 0
    assert db_session.scalar(select(func.count()).select_from(AuthIdentity)) == 0
    assert db_session.scalar(select(func.count()).select_from(EmailAccount)) == 0
    assert db_session.scalar(select(func.count()).select_from(IngestionRun)) == 0
