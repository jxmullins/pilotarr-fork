"""
Integration tests for GET /api/dashboard/requests.

Covers:
- Returns all requests when no status filter
- Returns only matching requests when status filter is applied
- Respects limit parameter
- Returns empty list when no requests in DB
- Unknown status filter returns empty list (not an error)
"""

from app.models.enums import MediaType, RequestPriority, RequestStatus
from app.models.models import JellyseerrRequest

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_request(db, title="Movie", jellyseerr_id=1, status=RequestStatus.PENDING):
    req = JellyseerrRequest(
        jellyseerr_id=jellyseerr_id,
        title=title,
        media_type=MediaType.MOVIE,
        year=2024,
        image_url="https://example.com/poster.jpg",
        image_alt=f"{title} poster",
        status=status,
        priority=RequestPriority.MEDIUM,
        requested_by="alice",
        requested_date="2025-01-10",
        quality="HD-1080p",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


# ── GET /api/dashboard/requests ───────────────────────────────────────────────


class TestGetDashboardRequests:
    def test_returns_empty_list_when_no_requests(self, auth_client, db):
        resp = auth_client.get("/api/dashboard/requests")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_all_requests_without_filter(self, auth_client, db):
        _make_request(db, "Movie A", jellyseerr_id=1, status=RequestStatus.PENDING)
        _make_request(db, "Movie B", jellyseerr_id=2, status=RequestStatus.APPROVED)
        _make_request(db, "Movie C", jellyseerr_id=3, status=RequestStatus.DECLINED)

        resp = auth_client.get("/api/dashboard/requests")

        assert resp.status_code == 200
        titles = [r["title"] for r in resp.json()]
        assert "Movie A" in titles
        assert "Movie B" in titles
        assert "Movie C" in titles

    def test_filters_by_pending_status(self, auth_client, db):
        _make_request(db, "Pending Movie", jellyseerr_id=1, status=RequestStatus.PENDING)
        _make_request(db, "Approved Movie", jellyseerr_id=2, status=RequestStatus.APPROVED)

        resp = auth_client.get("/api/dashboard/requests?status=1")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Pending Movie"

    def test_filters_by_approved_status(self, auth_client, db):
        _make_request(db, "Pending Movie", jellyseerr_id=1, status=RequestStatus.PENDING)
        _make_request(db, "Approved Movie", jellyseerr_id=2, status=RequestStatus.APPROVED)

        resp = auth_client.get("/api/dashboard/requests?status=2")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Approved Movie"

    def test_filters_by_declined_status(self, auth_client, db):
        _make_request(db, "Declined Movie", jellyseerr_id=1, status=RequestStatus.DECLINED)
        _make_request(db, "Pending Movie", jellyseerr_id=2, status=RequestStatus.PENDING)

        resp = auth_client.get("/api/dashboard/requests?status=3")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Declined Movie"

    def test_unknown_status_returns_empty_list(self, auth_client, db):
        _make_request(db, "Some Movie", jellyseerr_id=1, status=RequestStatus.PENDING)

        resp = auth_client.get("/api/dashboard/requests?status=99")

        assert resp.status_code == 200
        assert resp.json() == []

    def test_respects_limit_parameter(self, auth_client, db):
        for i in range(5):
            _make_request(db, f"Movie {i}", jellyseerr_id=i + 1, status=RequestStatus.PENDING)

        resp = auth_client.get("/api/dashboard/requests?limit=3")

        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_limit_and_status_combined(self, auth_client, db):
        for i in range(4):
            _make_request(db, f"Pending {i}", jellyseerr_id=i + 1, status=RequestStatus.PENDING)
        _make_request(db, "Approved", jellyseerr_id=10, status=RequestStatus.APPROVED)

        resp = auth_client.get("/api/dashboard/requests?status=1&limit=2")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(r["status"] == RequestStatus.PENDING.value for r in data)

    def test_response_contains_expected_fields(self, auth_client, db):
        _make_request(db, "Test Movie", jellyseerr_id=1)

        resp = auth_client.get("/api/dashboard/requests")

        assert resp.status_code == 200
        item = resp.json()[0]
        assert "id" in item
        assert "title" in item
        assert "status" in item
        assert "media_type" in item
        assert "requested_by" in item
