"""
Shared pytest fixtures for Pilotarr backend tests.

Strategy:
- SQLite in-memory replaces MySQL — no Docker required.
- get_db dependency is overridden per-test with a fresh session.
- get_current_user is overridden with a fixture user (no JWT round-trip needed
  for protected routes, unless we're specifically testing auth).
- The lifespan schedulers and MySQL health-check are patched out.
"""

import os
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── Set required env vars BEFORE any app import ──────────────────────────────
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pilotarr-testing-only!")
os.environ.setdefault("API_KEY", "test-api-key")
os.environ.setdefault("WEBHOOK_SECRET", "test-webhook-secret")

# ── App imports (after env vars are set) ─────────────────────────────────────
from app.core.security import get_current_user  # noqa: E402
from app.db import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.enums import MediaType, ServiceType  # noqa: E402
from app.models.models import Episode, LibraryItem, Season, ServiceConfiguration, User  # noqa: E402
from app.services.auth_service import create_access_token, hash_password  # noqa: E402

# ── SQLite in-memory engine ───────────────────────────────────────────────────
SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Core DB fixture ───────────────────────────────────────────────────────────


@pytest.fixture()
def db():
    """Fresh SQLite session per test; tables created and dropped around each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ── TestClient fixture ────────────────────────────────────────────────────────


@pytest.fixture()
def client(db):
    """
    TestClient with:
    - get_db overridden to use the in-memory SQLite session.
    - lifespan patched (no MySQL check, no scheduler start).
    - get_current_user NOT overridden here — use `auth_client` for that.
    """

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    with (
        patch("app.main.check_db_connection", return_value=False),
        patch("app.main.app_scheduler"),
        patch("app.main.analytics_scheduler"),
    ):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def auth_client(client, db):
    """
    TestClient where get_current_user returns a real User from the test DB.
    Use this for all JWT-protected routes.
    """
    user = User(
        username="testuser",
        hashed_password=hash_password("testpass"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


# ── Auth helpers ──────────────────────────────────────────────────────────────


@pytest.fixture()
def auth_headers(db):
    """
    Return Bearer headers built from a real JWT for 'testuser'.
    Useful when you need an actual token (e.g., testing the auth routes themselves).
    """
    user = User(
        username="testuser",
        hashed_password=hash_password("testpass"),
        is_active=True,
    )
    db.add(user)
    db.commit()

    token = create_access_token("testuser")
    return {"Authorization": f"Bearer {token}"}


# ── Data factories ────────────────────────────────────────────────────────────


@pytest.fixture()
def make_library_item(db):
    """Factory: create and persist a LibraryItem."""

    def _make(
        title="Test Movie",
        year=2024,
        media_type=MediaType.MOVIE,
        quality="1080p",
        size="4.2 GB",
        rating="7.5",
        description="A test description.",
        jellyfin_id=None,
        nb_media=1,
        watched=False,
    ):
        item = LibraryItem(
            title=title,
            year=year,
            media_type=media_type,
            image_url="https://example.com/poster.jpg",
            image_alt=title,
            quality=quality,
            size=size,
            rating=rating,
            description=description,
            jellyfin_id=jellyfin_id,
            nb_media=nb_media,
            watched=watched,
            created_at=datetime(2025, 1, 15, 10, 0, 0),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    return _make


@pytest.fixture()
def make_service_config(db):
    """Factory: create and persist a ServiceConfiguration."""

    def _make(
        service_name=ServiceType.SONARR,
        url="http://localhost",
        port=8989,
        api_key="test-api-key",
        is_active=True,
    ):
        svc = ServiceConfiguration(
            service_name=service_name,
            url=url,
            port=port,
            api_key=api_key,
            is_active=is_active,
        )
        db.add(svc)
        db.commit()
        db.refresh(svc)
        return svc

    return _make


@pytest.fixture()
def make_tv_show(db, make_library_item):
    """Factory: create a TV LibraryItem with one Season and two Episodes."""

    def _make(title="Test Show", sonarr_series_id=42):
        show = make_library_item(title=title, media_type=MediaType.TV, size="10 GB")

        season = Season(
            library_item_id=show.id,
            sonarr_series_id=sonarr_series_id,
            season_number=1,
            monitored=True,
            episode_count=2,
            episode_file_count=1,
            total_episode_count=2,
        )
        db.add(season)
        db.flush()

        ep1 = Episode(
            season_id=season.id,
            library_item_id=show.id,
            sonarr_episode_id=101,
            sonarr_series_id=sonarr_series_id,
            season_number=1,
            episode_number=1,
            title="Pilot",
            monitored=True,
            has_file=True,
            downloaded=True,
            watched=False,
        )
        ep2 = Episode(
            season_id=season.id,
            library_item_id=show.id,
            sonarr_episode_id=102,
            sonarr_series_id=sonarr_series_id,
            season_number=1,
            episode_number=2,
            title="Episode 2",
            monitored=False,
            has_file=False,
            downloaded=False,
            watched=False,
        )
        db.add_all([ep1, ep2])
        db.commit()
        db.refresh(show)
        return show, season, [ep1, ep2]

    return _make
