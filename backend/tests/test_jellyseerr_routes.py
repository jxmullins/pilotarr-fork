"""
Integration tests for Jellyseerr approve/decline routes.

- POST /api/jellyseerr/requests/{id}/approve
- POST /api/jellyseerr/requests/{id}/decline
"""

from unittest.mock import AsyncMock, patch

from app.models.enums import MediaType, RequestPriority, RequestStatus, ServiceType
from app.models.models import JellyseerrRequest, ServiceConfiguration

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_jellyseerr_service(db, is_active=True):
    svc = ServiceConfiguration(
        service_name=ServiceType.JELLYSEERR,
        url="http://jellyseerr.local",
        port=5055,
        api_key="test-jellyseerr-key",
        is_active=is_active,
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)
    return svc


def _make_jellyseerr_request(db, jellyseerr_id=42, status=RequestStatus.PENDING):
    req = JellyseerrRequest(
        jellyseerr_id=jellyseerr_id,
        title="Inception",
        media_type=MediaType.MOVIE,
        year=2010,
        image_url="https://example.com/poster.jpg",
        image_alt="Inception poster",
        status=status,
        priority=RequestPriority.MEDIUM,
        requested_by="alice",
        requested_date="2025-01-10",
        quality="HD-1080p",
        description="A mind-bending thriller.",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def _mock_connector():
    m = AsyncMock()
    m.approve_request = AsyncMock()
    m.decline_request = AsyncMock()
    m.close = AsyncMock()
    return m


# ── POST /api/jellyseerr/requests/{id}/approve ────────────────────────────────


class TestApproveRequest:
    def test_approve_success(self, auth_client, db):
        _make_jellyseerr_service(db)
        req = _make_jellyseerr_request(db)
        connector = _mock_connector()

        with patch("app.api.routes.jellyseerr.JellyseerrConnector", return_value=connector):
            resp = auth_client.post(f"/api/jellyseerr/requests/{req.id}/approve")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

        db.refresh(req)
        assert req.status == RequestStatus.APPROVED

    def test_approve_calls_external_api_with_jellyseerr_id(self, auth_client, db):
        _make_jellyseerr_service(db)
        req = _make_jellyseerr_request(db, jellyseerr_id=99)
        connector = _mock_connector()

        with patch("app.api.routes.jellyseerr.JellyseerrConnector", return_value=connector):
            auth_client.post(f"/api/jellyseerr/requests/{req.id}/approve")

        connector.approve_request.assert_awaited_once_with(99)

    def test_approve_closes_connector(self, auth_client, db):
        _make_jellyseerr_service(db)
        req = _make_jellyseerr_request(db)
        connector = _mock_connector()

        with patch("app.api.routes.jellyseerr.JellyseerrConnector", return_value=connector):
            auth_client.post(f"/api/jellyseerr/requests/{req.id}/approve")

        connector.close.assert_awaited_once()

    def test_approve_404_when_request_not_found(self, auth_client, db):
        _make_jellyseerr_service(db)

        resp = auth_client.post("/api/jellyseerr/requests/nonexistent-id/approve")

        assert resp.status_code == 404

    def test_approve_503_when_no_service_configured(self, auth_client, db):
        req = _make_jellyseerr_request(db)

        resp = auth_client.post(f"/api/jellyseerr/requests/{req.id}/approve")

        assert resp.status_code == 503

    def test_approve_503_when_service_inactive(self, auth_client, db):
        _make_jellyseerr_service(db, is_active=False)
        req = _make_jellyseerr_request(db)

        resp = auth_client.post(f"/api/jellyseerr/requests/{req.id}/approve")

        assert resp.status_code == 503

    def test_approve_500_when_connector_raises(self, auth_client, db):
        _make_jellyseerr_service(db)
        req = _make_jellyseerr_request(db)
        connector = _mock_connector()
        connector.approve_request.side_effect = Exception("Jellyseerr unreachable")

        with patch("app.api.routes.jellyseerr.JellyseerrConnector", return_value=connector):
            resp = auth_client.post(f"/api/jellyseerr/requests/{req.id}/approve")

        assert resp.status_code == 500
        # DB status must NOT have changed
        db.refresh(req)
        assert req.status == RequestStatus.PENDING


# ── POST /api/jellyseerr/requests/{id}/decline ────────────────────────────────


class TestDeclineRequest:
    def test_decline_success(self, auth_client, db):
        _make_jellyseerr_service(db)
        req = _make_jellyseerr_request(db)
        connector = _mock_connector()

        with patch("app.api.routes.jellyseerr.JellyseerrConnector", return_value=connector):
            resp = auth_client.post(f"/api/jellyseerr/requests/{req.id}/decline")

        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

        db.refresh(req)
        assert req.status == RequestStatus.DECLINED

    def test_decline_calls_external_api_with_jellyseerr_id(self, auth_client, db):
        _make_jellyseerr_service(db)
        req = _make_jellyseerr_request(db, jellyseerr_id=77)
        connector = _mock_connector()

        with patch("app.api.routes.jellyseerr.JellyseerrConnector", return_value=connector):
            auth_client.post(f"/api/jellyseerr/requests/{req.id}/decline")

        connector.decline_request.assert_awaited_once_with(77)

    def test_decline_closes_connector(self, auth_client, db):
        _make_jellyseerr_service(db)
        req = _make_jellyseerr_request(db)
        connector = _mock_connector()

        with patch("app.api.routes.jellyseerr.JellyseerrConnector", return_value=connector):
            auth_client.post(f"/api/jellyseerr/requests/{req.id}/decline")

        connector.close.assert_awaited_once()

    def test_decline_404_when_request_not_found(self, auth_client, db):
        _make_jellyseerr_service(db)

        resp = auth_client.post("/api/jellyseerr/requests/nonexistent-id/decline")

        assert resp.status_code == 404

    def test_decline_503_when_no_service_configured(self, auth_client, db):
        req = _make_jellyseerr_request(db)

        resp = auth_client.post(f"/api/jellyseerr/requests/{req.id}/decline")

        assert resp.status_code == 503

    def test_decline_503_when_service_inactive(self, auth_client, db):
        _make_jellyseerr_service(db, is_active=False)
        req = _make_jellyseerr_request(db)

        resp = auth_client.post(f"/api/jellyseerr/requests/{req.id}/decline")

        assert resp.status_code == 503

    def test_decline_500_when_connector_raises(self, auth_client, db):
        _make_jellyseerr_service(db)
        req = _make_jellyseerr_request(db)
        connector = _mock_connector()
        connector.decline_request.side_effect = Exception("Jellyseerr unreachable")

        with patch("app.api.routes.jellyseerr.JellyseerrConnector", return_value=connector):
            resp = auth_client.post(f"/api/jellyseerr/requests/{req.id}/decline")

        assert resp.status_code == 500
        db.refresh(req)
        assert req.status == RequestStatus.PENDING
