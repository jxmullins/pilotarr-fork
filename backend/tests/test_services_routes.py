"""
Integration tests for /api/services routes.

- GET  /api/services/
- GET  /api/services/{name}
- POST /api/services/
- PUT  /api/services/{name}
- DELETE /api/services/{name}
- POST /api/services/{name}/test
"""

from unittest.mock import AsyncMock, patch

from app.models.enums import ServiceType

# ── GET /api/services/ ────────────────────────────────────────────────────────


class TestListServices:
    def test_empty(self, auth_client):
        resp = auth_client.get("/api/services/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_with_one_service(self, auth_client, make_service_config):
        make_service_config()
        resp = auth_client.get("/api/services/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


# ── GET /api/services/{name} ──────────────────────────────────────────────────


class TestGetService:
    def test_get_existing(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.RADARR, url="http://radarr", port=7878)
        resp = auth_client.get("/api/services/radarr")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service_name"] == "radarr"
        assert data["url"] == "http://radarr"
        assert data["port"] == 7878

    def test_get_nonexistent(self, auth_client):
        resp = auth_client.get("/api/services/sonarr")
        assert resp.status_code == 404


# ── POST /api/services/ ───────────────────────────────────────────────────────


class TestCreateService:
    def test_create_new_service(self, auth_client):
        payload = {
            "service_name": "sonarr",
            "url": "http://sonarr",
            "api_key": "sonarr-key",
            "port": 8989,
            "is_active": True,
        }
        resp = auth_client.post("/api/services/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["service_name"] == "sonarr"
        assert data["url"] == "http://sonarr"

    def test_create_duplicate_service(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.SONARR)
        payload = {
            "service_name": "sonarr",
            "url": "http://sonarr2",
            "api_key": "key2",
            "is_active": True,
        }
        resp = auth_client.post("/api/services/", json=payload)
        assert resp.status_code == 409


# ── PUT /api/services/{name} ──────────────────────────────────────────────────


class TestUpdateService:
    def test_update_existing_service(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.SONARR, url="http://old-url")
        resp = auth_client.put(
            "/api/services/sonarr",
            json={"url": "http://new-url", "api_key": "new-key", "is_active": True},
        )
        assert resp.status_code == 200
        assert resp.json()["url"] == "http://new-url"

    def test_upsert_creates_if_missing(self, auth_client):
        """PUT should create the record if it doesn't exist yet."""
        resp = auth_client.put(
            "/api/services/radarr",
            json={"url": "http://radarr", "api_key": "radarr-key", "is_active": False},
        )
        assert resp.status_code == 200
        assert resp.json()["service_name"] == "radarr"


# ── DELETE /api/services/{name} ───────────────────────────────────────────────


class TestDeleteService:
    def test_delete_existing(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.QBITTORRENT)
        resp = auth_client.delete("/api/services/qbittorrent")
        assert resp.status_code == 204
        # Confirm it's gone
        assert auth_client.get("/api/services/qbittorrent").status_code == 404

    def test_delete_nonexistent(self, auth_client):
        resp = auth_client.delete("/api/services/sonarr")
        assert resp.status_code == 404


# ── POST /api/services/{name}/test ───────────────────────────────────────────


class TestTestServiceConnection:
    def test_connection_success(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.SONARR)

        with patch("app.api.routes.services.SonarrConnector") as mock_connector:
            instance = AsyncMock()
            instance.test_connection = AsyncMock(return_value=(True, "Connected to Sonarr v4"))
            instance.close = AsyncMock()
            mock_connector.return_value = instance

            resp = auth_client.post("/api/services/sonarr/test")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "Sonarr" in data["message"]

    def test_connection_failure(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.SONARR)

        with patch("app.api.routes.services.SonarrConnector") as mock_connector:
            instance = AsyncMock()
            instance.test_connection = AsyncMock(return_value=(False, "Connection refused"))
            instance.close = AsyncMock()
            mock_connector.return_value = instance

            resp = auth_client.post("/api/services/sonarr/test")

        assert resp.status_code == 200
        assert resp.json()["success"] is False

    def test_test_nonexistent_service(self, auth_client):
        resp = auth_client.post("/api/services/sonarr/test")
        assert resp.status_code == 404
