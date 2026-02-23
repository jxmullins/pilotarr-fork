"""
Integration tests for /api/torrents routes.

- GET /api/torrents/all
- GET /api/torrents/item/{library_item_id}
"""

from unittest.mock import AsyncMock, patch

from app.models.enums import ServiceType

MOCK_TORRENT = {
    "id": "abc123",
    "name": "Test.Movie.2024.1080p",
    "status": "seeding",
    "size": 4_294_967_296,
    "progress": 1.0,
    "dlSpeed": 0,
    "ulSpeed": 1024,
    "seeds": 10,
    "peers": 2,
    "ratio": 1.5,
    "eta": 0,
    "tracker": "tracker.example.com",
    "tags": [],
    "category": "movies",
    "downloaded": 4_294_967_296,
    "uploaded": 6_442_450_944,
    "addedOn": "2024-01-01T00:00:00+00:00",
    "completedOn": "2024-01-02T00:00:00+00:00",
    "savePath": "/downloads/movies",
    "errorMessage": None,
}

MOCK_TRANSFER = {"dl_speed": 0, "ul_speed": 1024, "connection_status": "connected"}


class TestGetAllTorrents:
    def test_no_qbittorrent_config_returns_404(self, auth_client):
        resp = auth_client.get("/api/torrents/all")
        assert resp.status_code == 404

    def test_returns_torrents_with_mocked_connector(self, auth_client, make_service_config):
        make_service_config(
            service_name=ServiceType.QBITTORRENT,
            url="http://localhost",
            port=8080,
            api_key=None,
        )

        with patch("app.api.routes.torrents.create_connector") as mock_factory:
            mock_connector = AsyncMock()
            mock_connector.login = AsyncMock(return_value=True)
            mock_connector.get_all_torrents = AsyncMock(return_value=[MOCK_TORRENT])
            mock_connector.get_transfer_info = AsyncMock(return_value=MOCK_TRANSFER)
            mock_connector.close = AsyncMock()
            mock_factory.return_value = mock_connector

            resp = auth_client.get("/api/torrents/all")

        assert resp.status_code == 200
        data = resp.json()
        assert data["client"] == "qbittorrent"
        assert len(data["torrents"]) == 1
        assert data["torrents"][0]["name"] == "Test.Movie.2024.1080p"
        assert data["transfer"]["dl_speed"] == 0

    def test_login_failure_returns_503(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.QBITTORRENT)

        with patch("app.api.routes.torrents.create_connector") as mock_factory:
            mock_connector = AsyncMock()
            mock_connector.login = AsyncMock(return_value=False)
            mock_connector.close = AsyncMock()
            mock_factory.return_value = mock_connector

            resp = auth_client.get("/api/torrents/all")

        assert resp.status_code == 503

    def test_torrent_has_added_on_field(self, auth_client, make_service_config):
        make_service_config(service_name=ServiceType.QBITTORRENT)

        with patch("app.api.routes.torrents.create_connector") as mock_factory:
            mock_connector = AsyncMock()
            mock_connector.login = AsyncMock(return_value=True)
            mock_connector.get_all_torrents = AsyncMock(return_value=[MOCK_TORRENT])
            mock_connector.get_transfer_info = AsyncMock(return_value=MOCK_TRANSFER)
            mock_connector.close = AsyncMock()
            mock_factory.return_value = mock_connector

            resp = auth_client.get("/api/torrents/all")

        torrent = resp.json()["torrents"][0]
        assert "addedOn" in torrent
        assert torrent["addedOn"] == "2024-01-01T00:00:00+00:00"


class TestGetItemTorrents:
    def test_returns_empty_list_for_unknown_item(self, auth_client):
        resp = auth_client.get("/api/torrents/item/nonexistent-id")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_torrent_rows_for_known_item(self, auth_client, make_library_item, db):
        from app.models.models import LibraryItemTorrent

        item = make_library_item()
        torrent_row = LibraryItemTorrent(
            library_item_id=item.id,
            torrent_hash="abc" * 13 + "a",
            torrent_info={"ratio": 1.2, "status": "seeding"},
        )
        db.add(torrent_row)
        db.commit()

        resp = auth_client.get(f"/api/torrents/item/{item.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["hash"] == torrent_row.torrent_hash
