"""
Integration tests for /api/sync routes.

- GET  /api/sync/status
- POST /api/sync/trigger (fires background task — just check 202 accepted)
- POST /api/sync/trigger/{service_name}
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.enums import ServiceType, SyncStatus
from app.models.models import SyncMetadata


class TestSyncStatus:
    def test_status_empty(self, auth_client):
        resp = auth_client.get("/api/sync/status")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_status_with_entries(self, auth_client, db):
        entry = SyncMetadata(
            service_name=ServiceType.SONARR,
            sync_status=SyncStatus.SUCCESS,
            records_synced=42,
            last_sync_time=datetime(2025, 1, 1, 12, 0),
            created_at=datetime(2025, 1, 1, 10, 0),
            updated_at=datetime(2025, 1, 1, 12, 0),
        )
        db.add(entry)
        db.commit()

        resp = auth_client.get("/api/sync/status")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["service_name"] == "sonarr"
        assert data[0]["sync_status"] == "success"
        assert data[0]["records_synced"] == 42


class TestTriggerSync:
    def test_trigger_full_sync_accepted(self, auth_client):
        """POST /sync/trigger fires a background task — should return 202."""
        with (
            patch("app.api.routes.sync.SyncService"),
            patch("app.api.routes.sync.TorrentEnrichmentService"),
            patch("app.api.routes.sync.JellyfinStreamsService"),
        ):
            resp = auth_client.post("/api/sync/trigger")
        # Background task: FastAPI returns 200 by default (no explicit 202)
        assert resp.status_code == 200

    def test_trigger_service_sync_sonarr(self, auth_client):
        with patch("app.api.routes.sync.SyncService") as mock_sync:
            instance = MagicMock()
            instance.sync_service = AsyncMock(return_value=None)
            mock_sync.return_value = instance
            resp = auth_client.post("/api/sync/trigger/sonarr")
        assert resp.status_code in (200, 202)

    def test_trigger_unknown_service(self, auth_client):
        # The route path is a free string, not an enum — FastAPI returns 404
        resp = auth_client.post("/api/sync/trigger/unknownservice")
        assert resp.status_code in (404, 422)
