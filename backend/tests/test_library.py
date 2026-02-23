"""
Integration tests for /api/library routes.

- GET  /api/library/
- GET  /api/library/{id}
- GET  /api/library/{id}/seasons-with-episodes
- PATCH /api/library/{id}/seasons/{s}/episodes/{e}/watched
- POST  /api/library/{id}/seasons/{s}/episodes/{e}/monitor
- POST  /api/library/{id}/seasons/{s}/episodes/{e}/search
"""

from unittest.mock import AsyncMock, patch

from app.models.enums import MediaType

# ── GET /api/library/ ─────────────────────────────────────────────────────────


class TestListLibrary:
    def test_empty_library(self, auth_client):
        resp = auth_client.get("/api/library/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_library_with_movie(self, auth_client, make_library_item):
        make_library_item(title="Inception", year=2010)
        resp = auth_client.get("/api/library/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Inception"
        assert data[0]["year"] == 2010

    def test_library_returns_multiple_items(self, auth_client, make_library_item):
        make_library_item(title="Movie A")
        make_library_item(title="Movie B")
        resp = auth_client.get("/api/library/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_library_with_limit(self, auth_client, make_library_item):
        for i in range(5):
            make_library_item(title=f"Movie {i}")
        resp = auth_client.get("/api/library/?limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_library_item_zero_size_excluded(self, auth_client, db):
        """Items with size=0 are filtered out."""
        from app.models.models import LibraryItem

        item = LibraryItem(
            title="Ghost",
            year=2020,
            media_type=MediaType.MOVIE,
            image_url="https://example.com/p.jpg",
            image_alt="Ghost",
            quality="720p",
            size="0",
            nb_media=0,
            watched=False,
        )
        db.add(item)
        db.commit()
        resp = auth_client.get("/api/library/")
        assert resp.status_code == 200
        assert resp.json() == []


# ── GET /api/library/{id} ─────────────────────────────────────────────────────


class TestGetLibraryItem:
    def test_get_existing_movie(self, auth_client, make_library_item):
        item = make_library_item(title="The Matrix", rating="8.7", description="A classic.")
        resp = auth_client.get(f"/api/library/{item.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "The Matrix"
        assert data["rating"] == "8.7"
        assert data["description"] == "A classic."

    def test_get_nonexistent_item(self, auth_client):
        resp = auth_client.get("/api/library/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    def test_get_item_includes_jellyfin_id(self, auth_client, make_library_item):
        item = make_library_item(jellyfin_id="jf-abc-123")
        resp = auth_client.get(f"/api/library/{item.id}")
        assert resp.status_code == 200
        assert resp.json()["jellyfin_id"] == "jf-abc-123"

    def test_get_tv_item_includes_sonarr_series_id(self, auth_client, make_tv_show):
        show, season, _ = make_tv_show(sonarr_series_id=99)
        resp = auth_client.get(f"/api/library/{show.id}")
        assert resp.status_code == 200
        assert resp.json()["sonarr_series_id"] == 99


# ── GET /api/library/{id}/seasons-with-episodes ──────────────────────────────


class TestSeasonsWithEpisodes:
    def test_returns_seasons_and_episodes(self, auth_client, make_tv_show):
        show, _, episodes = make_tv_show()
        resp = auth_client.get(f"/api/library/{show.id}/seasons-with-episodes")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        season = data[0]
        assert season["season_number"] == 1
        assert season["is_monitored"] is True
        assert len(season["episodes"]) == 2

    def test_episode_includes_sonarr_episode_id(self, auth_client, make_tv_show):
        show, _, _ = make_tv_show()
        resp = auth_client.get(f"/api/library/{show.id}/seasons-with-episodes")
        assert resp.status_code == 200
        eps = resp.json()[0]["episodes"]
        assert eps[0]["sonarr_episode_id"] == 101
        assert eps[1]["sonarr_episode_id"] == 102

    def test_episode_monitored_flag(self, auth_client, make_tv_show):
        show, _, _ = make_tv_show()
        resp = auth_client.get(f"/api/library/{show.id}/seasons-with-episodes")
        eps = resp.json()[0]["episodes"]
        assert eps[0]["monitored"] is True  # ep1
        assert eps[1]["monitored"] is False  # ep2

    def test_returns_404_for_movie(self, auth_client, make_library_item):
        movie = make_library_item()
        resp = auth_client.get(f"/api/library/{movie.id}/seasons-with-episodes")
        assert resp.status_code == 404


# ── PATCH /api/library/{id}/seasons/{s}/episodes/{e}/watched ─────────────────


class TestSetEpisodeWatched:
    def test_mark_episode_watched(self, auth_client, make_tv_show, db):
        show, _, episodes = make_tv_show()
        ep = episodes[0]
        resp = auth_client.patch(
            f"/api/library/{show.id}/seasons/1/episodes/{ep.episode_number}/watched",
            json={"watched": True},
        )
        assert resp.status_code == 200
        assert resp.json()["watched"] is True
        db.refresh(ep)
        assert ep.watched is True

    def test_mark_episode_unwatched(self, auth_client, make_tv_show, db):
        show, _, episodes = make_tv_show()
        ep = episodes[0]
        ep.watched = True
        db.commit()
        resp = auth_client.patch(
            f"/api/library/{show.id}/seasons/1/episodes/{ep.episode_number}/watched",
            json={"watched": False},
        )
        assert resp.status_code == 200
        assert resp.json()["watched"] is False

    def test_episode_not_found(self, auth_client, make_tv_show):
        show, _, _ = make_tv_show()
        resp = auth_client.patch(
            f"/api/library/{show.id}/seasons/1/episodes/999/watched",
            json={"watched": True},
        )
        assert resp.status_code == 404


# ── POST .../monitor ──────────────────────────────────────────────────────────


class TestMonitorEpisode:
    def test_monitor_episode_success(self, auth_client, make_tv_show, make_service_config, db):
        from app.models.enums import ServiceType

        make_service_config(service_name=ServiceType.SONARR)
        show, _, episodes = make_tv_show()
        ep = episodes[1]  # unmonitored episode

        with patch("app.api.routes.library.create_connector") as mock_factory:
            mock_connector = AsyncMock()
            mock_connector.monitor_episode = AsyncMock(return_value=True)
            mock_connector.close = AsyncMock()
            mock_factory.return_value = mock_connector

            resp = auth_client.post(f"/api/library/{show.id}/seasons/1/episodes/{ep.episode_number}/monitor")

        assert resp.status_code == 200
        assert resp.json()["monitored"] is True
        db.refresh(ep)
        assert ep.monitored is True

    def test_monitor_episode_no_sonarr_config(self, auth_client, make_tv_show):
        show, _, episodes = make_tv_show()
        ep = episodes[1]
        resp = auth_client.post(f"/api/library/{show.id}/seasons/1/episodes/{ep.episode_number}/monitor")
        assert resp.status_code == 503

    def test_monitor_episode_not_found(self, auth_client, make_tv_show, make_service_config):
        from app.models.enums import ServiceType

        make_service_config(service_name=ServiceType.SONARR)
        show, _, _ = make_tv_show()
        resp = auth_client.post(f"/api/library/{show.id}/seasons/1/episodes/999/monitor")
        assert resp.status_code == 404


# ── POST .../search ───────────────────────────────────────────────────────────


class TestSearchEpisode:
    def test_search_episode_success(self, auth_client, make_tv_show, make_service_config):
        from app.models.enums import ServiceType

        make_service_config(service_name=ServiceType.SONARR)
        show, _, episodes = make_tv_show()
        ep = episodes[0]

        with patch("app.api.routes.library.create_connector") as mock_factory:
            mock_connector = AsyncMock()
            mock_connector.search_episode = AsyncMock(return_value=True)
            mock_connector.close = AsyncMock()
            mock_factory.return_value = mock_connector

            resp = auth_client.post(f"/api/library/{show.id}/seasons/1/episodes/{ep.episode_number}/search")

        assert resp.status_code == 200
        assert resp.json()["searching"] is True

    def test_search_episode_no_sonarr_config(self, auth_client, make_tv_show):
        show, _, episodes = make_tv_show()
        ep = episodes[0]
        resp = auth_client.post(f"/api/library/{show.id}/seasons/1/episodes/{ep.episode_number}/search")
        assert resp.status_code == 503
