"""
Integration tests for /api/prowlarr routes.

Covers:
- GET  /api/prowlarr/indexers
- PATCH /api/prowlarr/indexers/{id}
- GET  /api/prowlarr/history
- GET  /api/prowlarr/search
- POST /api/prowlarr/grab

Each route is tested for:
- 503 when Prowlarr service is not configured / inactive
- Happy path (connector mocked)
- Error path (connector returns failure / raises)
"""

from unittest.mock import AsyncMock, patch

from app.models.enums import ServiceType

MOCK_INDEXER = {
    "id": 1,
    "name": "NZBgeek",
    "enable": True,
    "protocol": "usenet",
    "privacy": "private",
    "capabilities": {"categories": ["Movies", "TV"]},
    "stats": {
        "numberOfQueries": 50,
        "numberOfFailedQueries": 2,
        "numberOfGrabs": 10,
        "numberOfFailedGrabs": 0,
        "averageResponseTime": 300,
    },
}

MOCK_HISTORY_ITEM = {
    "id": 1,
    "date": "2024-01-15T10:00:00Z",
    "indexer": "NZBgeek",
    "query": "Breaking Bad",
    "categories": ["5000"],
    "eventType": "grabRelease",
    "successful": True,
    "source": "Sonarr",
}

MOCK_SEARCH_RESULT = {
    "guid": "magnet:?xt=urn:btih:abc",
    "title": "Breaking Bad S01E01",
    "indexer": "NZBgeek",
    "indexerId": 1,
    "size": 1_500_000_000,
    "seeders": 42,
    "leechers": 5,
    "protocol": "torrent",
    "publishDate": "2024-01-10T00:00:00Z",
    "categories": ["TV"],
    "downloadUrl": "http://example.com/dl",
    "magnetUrl": "magnet:?xt=urn:btih:abc",
}


_SENTINEL = object()


def _mock_connector(
    indexers=_SENTINEL,
    history=_SENTINEL,
    search_results=_SENTINEL,
    toggle_ok=True,
    grab_ok=True,
):
    m = AsyncMock()
    m.get_indexers_with_stats = AsyncMock(return_value=[MOCK_INDEXER] if indexers is _SENTINEL else indexers)
    m.toggle_indexer = AsyncMock(return_value=toggle_ok)
    m.get_history = AsyncMock(return_value=[MOCK_HISTORY_ITEM] if history is _SENTINEL else history)
    m.search = AsyncMock(return_value=[MOCK_SEARCH_RESULT] if search_results is _SENTINEL else search_results)
    m.grab = AsyncMock(return_value=grab_ok)
    m.close = AsyncMock()
    return m


# ── GET /api/prowlarr/indexers ────────────────────────────────────────────────


class TestGetIndexers:
    def test_no_service_returns_503(self, auth_client):
        resp = auth_client.get("/api/prowlarr/indexers")
        assert resp.status_code == 503

    def test_inactive_service_returns_503(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR, is_active=False)
        resp = auth_client.get("/api/prowlarr/indexers")
        assert resp.status_code == 503

    def test_returns_indexers(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector()):
            resp = auth_client.get("/api/prowlarr/indexers")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "NZBgeek"
        assert data[0]["stats"]["numberOfQueries"] == 50

    def test_returns_empty_list_when_no_indexers(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector(indexers=[])):
            resp = auth_client.get("/api/prowlarr/indexers")
        assert resp.status_code == 200
        assert resp.json() == []


# ── PATCH /api/prowlarr/indexers/{id} ────────────────────────────────────────


class TestToggleIndexer:
    def test_no_service_returns_503(self, auth_client):
        resp = auth_client.patch("/api/prowlarr/indexers/1", json={"enable": True})
        assert resp.status_code == 503

    def test_toggle_enable_returns_success(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector(toggle_ok=True)):
            resp = auth_client.patch("/api/prowlarr/indexers/1", json={"enable": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["id"] == 1
        assert data["enable"] is True

    def test_toggle_disable_reflects_in_response(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector(toggle_ok=True)):
            resp = auth_client.patch("/api/prowlarr/indexers/5", json={"enable": False})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 5
        assert data["enable"] is False

    def test_connector_failure_returns_502(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector(toggle_ok=False)):
            resp = auth_client.patch("/api/prowlarr/indexers/1", json={"enable": True})
        assert resp.status_code == 502


# ── GET /api/prowlarr/history ─────────────────────────────────────────────────


class TestGetHistory:
    def test_no_service_returns_503(self, auth_client):
        resp = auth_client.get("/api/prowlarr/history")
        assert resp.status_code == 503

    def test_returns_history_items(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector()):
            resp = auth_client.get("/api/prowlarr/history")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["indexer"] == "NZBgeek"
        assert data[0]["query"] == "Breaking Bad"

    def test_default_limit_is_15(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        mock = _mock_connector()
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=mock):
            auth_client.get("/api/prowlarr/history")
        mock.get_history.assert_called_once_with(page_size=15)

    def test_custom_limit_passed_to_connector(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        mock = _mock_connector()
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=mock):
            auth_client.get("/api/prowlarr/history?limit=50")
        mock.get_history.assert_called_once_with(page_size=50)

    def test_limit_too_large_returns_422(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        resp = auth_client.get("/api/prowlarr/history?limit=999")
        assert resp.status_code == 422

    def test_limit_zero_returns_422(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        resp = auth_client.get("/api/prowlarr/history?limit=0")
        assert resp.status_code == 422


# ── GET /api/prowlarr/search ──────────────────────────────────────────────────


class TestSearch:
    def test_no_service_returns_503(self, auth_client):
        resp = auth_client.get("/api/prowlarr/search?query=test")
        assert resp.status_code == 503

    def test_returns_search_results(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector()):
            resp = auth_client.get("/api/prowlarr/search?query=Breaking+Bad")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Breaking Bad S01E01"
        assert data[0]["seeders"] == 42

    def test_missing_query_returns_422(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        resp = auth_client.get("/api/prowlarr/search")
        assert resp.status_code == 422

    def test_empty_query_returns_422(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        resp = auth_client.get("/api/prowlarr/search?query=")
        assert resp.status_code == 422

    def test_passes_type_param_to_connector(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        mock = _mock_connector()
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=mock):
            auth_client.get("/api/prowlarr/search?query=test&type=movie")
        mock.search.assert_called_once_with("test", "movie")

    def test_empty_results_returns_empty_list(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector(search_results=[])):
            resp = auth_client.get("/api/prowlarr/search?query=nothing")
        assert resp.status_code == 200
        assert resp.json() == []


# ── POST /api/prowlarr/grab ───────────────────────────────────────────────────


class TestGrab:
    def test_no_service_returns_503(self, auth_client):
        resp = auth_client.post("/api/prowlarr/grab", json={"guid": "abc", "indexerId": 1})
        assert resp.status_code == 503

    def test_success_returns_ok(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector(grab_ok=True)):
            resp = auth_client.post("/api/prowlarr/grab", json={"guid": "magnet:abc", "indexerId": 1})
        assert resp.status_code == 200
        assert resp.json() == {"success": True}

    def test_connector_failure_returns_502(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        with patch("app.api.routes.prowlarr.ProwlarrConnector", return_value=_mock_connector(grab_ok=False)):
            resp = auth_client.post("/api/prowlarr/grab", json={"guid": "magnet:abc", "indexerId": 1})
        assert resp.status_code == 502

    def test_missing_guid_returns_422(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        resp = auth_client.post("/api/prowlarr/grab", json={"indexerId": 1})
        assert resp.status_code == 422

    def test_missing_indexer_id_returns_422(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.PROWLARR)
        resp = auth_client.post("/api/prowlarr/grab", json={"guid": "abc"})
        assert resp.status_code == 422
