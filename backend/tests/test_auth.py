"""
Integration tests for /api/auth routes.

- POST /api/auth/login
- GET  /api/auth/me
- POST /api/auth/change-password
"""

from types import SimpleNamespace

import app.services.auth_service as auth_service
from app.models.models import User
from app.services.auth_service import hash_password

# ── Helpers ───────────────────────────────────────────────────────────────────


def _seed_user(db, username="alice", password="alicepass"):
    user = User(
        username=username,
        hashed_password=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── POST /api/auth/login ──────────────────────────────────────────────────────


class TestLogin:
    def test_login_success(self, client, db):
        _seed_user(db)
        resp = client.post("/api/auth/login", json={"username": "alice", "password": "alicepass"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data
        assert data["username"] == "alice"

    def test_login_wrong_password(self, client, db):
        _seed_user(db)
        resp = client.post("/api/auth/login", json={"username": "alice", "password": "wrongpass"})
        assert resp.status_code == 401

    def test_login_unknown_user(self, client, db):
        resp = client.post("/api/auth/login", json={"username": "nobody", "password": "x"})
        assert resp.status_code == 401

    def test_login_inactive_user(self, client, db):
        user = _seed_user(db)
        user.is_active = False
        db.commit()
        resp = client.post("/api/auth/login", json={"username": "alice", "password": "alicepass"})
        assert resp.status_code == 401


# ── GET /api/auth/me ──────────────────────────────────────────────────────────


class TestMe:
    def test_me_authenticated(self, auth_client):
        resp = auth_client.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["is_active"] is True

    def test_me_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 403  # HTTPBearer returns 403 when no header


# ── POST /api/auth/change-password ────────────────────────────────────────────


class TestChangePassword:
    def test_change_password_success(self, auth_client):
        resp = auth_client.post(
            "/api/auth/change-password",
            json={
                "current_password": "testpass",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123",
            },
        )
        assert resp.status_code == 204

    def test_change_password_wrong_current(self, auth_client):
        resp = auth_client.post(
            "/api/auth/change-password",
            json={
                "current_password": "wrongpass",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123",
            },
        )
        assert resp.status_code == 400

    def test_change_password_too_short(self, auth_client):
        resp = auth_client.post(
            "/api/auth/change-password",
            json={
                "current_password": "testpass",
                "new_password": "short",
                "confirm_password": "short",
            },
        )
        assert resp.status_code == 422

    def test_change_password_mismatch_confirm(self, auth_client):
        resp = auth_client.post(
            "/api/auth/change-password",
            json={
                "current_password": "testpass",
                "new_password": "newpassword123",
                "confirm_password": "different123",
            },
        )
        assert resp.status_code == 422

    def test_change_password_revokes_existing_token(self, client, db):
        _seed_user(db, username="alice", password="alicepass123")

        login_resp = client.post("/api/auth/login", json={"username": "alice", "password": "alicepass123"})
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        change_resp = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "alicepass123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123",
            },
            headers=headers,
        )
        assert change_resp.status_code == 204

        stale_token_resp = client.get("/api/auth/me", headers=headers)
        assert stale_token_resp.status_code == 401

        old_login_resp = client.post("/api/auth/login", json={"username": "alice", "password": "alicepass123"})
        assert old_login_resp.status_code == 401

        fresh_login_resp = client.post("/api/auth/login", json={"username": "alice", "password": "newpassword123"})
        assert fresh_login_resp.status_code == 200
        fresh_headers = {"Authorization": f"Bearer {fresh_login_resp.json()['access_token']}"}

        fresh_token_resp = client.get("/api/auth/me", headers=fresh_headers)
        assert fresh_token_resp.status_code == 200


class TestBootstrapAdmin:
    def test_init_default_user_skips_without_explicit_bootstrap_credentials(self, db, monkeypatch):
        monkeypatch.setattr(
            auth_service,
            "settings",
            SimpleNamespace(
                BOOTSTRAP_ADMIN_USERNAME=None,
                BOOTSTRAP_ADMIN_PASSWORD=None,
            ),
        )

        auth_service.init_default_user(db)

        assert db.query(User).count() == 0

    def test_init_default_user_uses_explicit_bootstrap_credentials(self, db, monkeypatch):
        monkeypatch.setattr(
            auth_service,
            "settings",
            SimpleNamespace(
                BOOTSTRAP_ADMIN_USERNAME="bootstrap-admin",
                BOOTSTRAP_ADMIN_PASSWORD="super-secret-pass",
            ),
        )

        auth_service.init_default_user(db)

        user = db.query(User).one()
        assert user.username == "bootstrap-admin"
        assert auth_service.verify_password("super-secret-pass", user.hashed_password)

    def test_init_default_user_skips_bootstrap_when_user_already_exists(self, db, monkeypatch):
        _seed_user(db, username="existing-admin", password="existingpass123")
        monkeypatch.setattr(
            auth_service,
            "settings",
            SimpleNamespace(
                BOOTSTRAP_ADMIN_USERNAME="bootstrap-admin",
                BOOTSTRAP_ADMIN_PASSWORD="super-secret-pass",
            ),
        )

        auth_service.init_default_user(db)

        users = db.query(User).all()
        assert len(users) == 1
        assert users[0].username == "existing-admin"
