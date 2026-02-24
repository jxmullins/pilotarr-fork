"""Unit tests for AnalyticsService."""

from datetime import date, datetime, timedelta

import pytest

from app.models.enums import DeviceType, MediaType, PlaybackMethod, SessionStatus, VideoQuality
from app.models.models import DailyAnalytic, DeviceStatistic, PlaybackSession
from app.services.analytics_service import AnalyticsService

# ── map_device_type ────────────────────────────────────────────────────────────


class TestMapDeviceType:
    def test_chrome_is_web_browser(self):
        assert AnalyticsService.map_device_type("Chrome", "Desktop") == DeviceType.WEB_BROWSER

    def test_firefox_is_web_browser(self):
        assert AnalyticsService.map_device_type("Firefox", "PC") == DeviceType.WEB_BROWSER

    def test_safari_is_web_browser(self):
        assert AnalyticsService.map_device_type("Safari", "Mac") == DeviceType.WEB_BROWSER

    def test_edge_is_web_browser(self):
        assert AnalyticsService.map_device_type("Edge", "Desktop") == DeviceType.WEB_BROWSER

    def test_jellyfin_web_is_web_browser(self):
        assert AnalyticsService.map_device_type("Jellyfin Web", "") == DeviceType.WEB_BROWSER

    def test_android_client_is_mobile(self):
        assert AnalyticsService.map_device_type("Jellyfin Android", "Pixel 7") == DeviceType.MOBILE_APP

    def test_iphone_device_is_mobile(self):
        assert AnalyticsService.map_device_type("Infuse", "iPhone 14") == DeviceType.MOBILE_APP

    def test_ipad_device_is_mobile(self):
        assert AnalyticsService.map_device_type("Jellyfin", "iPad Pro") == DeviceType.MOBILE_APP

    def test_ios_client_is_mobile(self):
        assert AnalyticsService.map_device_type("Jellyfin iOS", "iPhone") == DeviceType.MOBILE_APP

    def test_chromecast_is_streaming_device(self):
        assert AnalyticsService.map_device_type("Jellyfin", "Chromecast Ultra") == DeviceType.STREAMING_DEVICE

    def test_roku_is_streaming_device(self):
        assert AnalyticsService.map_device_type("Jellyfin", "Roku Express") == DeviceType.STREAMING_DEVICE

    def test_fire_stick_is_streaming_device(self):
        assert AnalyticsService.map_device_type("Jellyfin", "Fire Stick 4K") == DeviceType.STREAMING_DEVICE

    def test_firestick_no_space_is_streaming_device(self):
        assert AnalyticsService.map_device_type("Jellyfin", "Firestick") == DeviceType.STREAMING_DEVICE

    def test_samsung_tv_is_smart_tv(self):
        assert AnalyticsService.map_device_type("Jellyfin", "Samsung TV") == DeviceType.SMART_TV

    def test_apple_tv_is_smart_tv(self):
        assert AnalyticsService.map_device_type("Infuse", "Apple TV") == DeviceType.SMART_TV

    def test_windows_client_is_desktop(self):
        assert AnalyticsService.map_device_type("Jellyfin Windows", "Desktop") == DeviceType.DESKTOP_APP

    def test_macos_client_is_desktop(self):
        assert AnalyticsService.map_device_type("Jellyfin macOS", "MacBook") == DeviceType.DESKTOP_APP

    def test_linux_client_is_desktop(self):
        assert AnalyticsService.map_device_type("Jellyfin Linux", "PC") == DeviceType.DESKTOP_APP

    def test_xbox_is_game_console(self):
        assert AnalyticsService.map_device_type("Jellyfin", "Xbox Series X") == DeviceType.GAME_CONSOLE

    def test_playstation_is_game_console(self):
        assert AnalyticsService.map_device_type("Jellyfin", "PlayStation 5") == DeviceType.GAME_CONSOLE

    def test_ps5_is_game_console(self):
        assert AnalyticsService.map_device_type("Jellyfin", "PS5") == DeviceType.GAME_CONSOLE

    def test_ps4_is_game_console(self):
        assert AnalyticsService.map_device_type("Jellyfin", "PS4 Pro") == DeviceType.GAME_CONSOLE

    def test_unknown_client_and_device_is_other(self):
        assert AnalyticsService.map_device_type("Unknown", "Unknown Device") == DeviceType.OTHER

    def test_empty_strings_is_other(self):
        assert AnalyticsService.map_device_type("", "") == DeviceType.OTHER

    def test_none_values_is_other(self):
        assert AnalyticsService.map_device_type(None, None) == DeviceType.OTHER


# ── map_video_quality ──────────────────────────────────────────────────────────


class TestMapVideoQuality:
    def test_4k_hdr_lowercase(self):
        assert AnalyticsService.map_video_quality("4k hdr") == VideoQuality.FOUR_K_HDR

    def test_4k_hdr_uppercase(self):
        assert AnalyticsService.map_video_quality("4K HDR") == VideoQuality.FOUR_K_HDR

    def test_4k_only(self):
        assert AnalyticsService.map_video_quality("4k") == VideoQuality.FOUR_K

    def test_2160p_is_4k(self):
        assert AnalyticsService.map_video_quality("2160p") == VideoQuality.FOUR_K

    def test_1080p_is_full_hd(self):
        assert AnalyticsService.map_video_quality("1080p") == VideoQuality.FULL_HD

    def test_full_hd_string(self):
        assert AnalyticsService.map_video_quality("full hd") == VideoQuality.FULL_HD

    def test_720p_is_hd(self):
        assert AnalyticsService.map_video_quality("720p") == VideoQuality.HD

    def test_hd_string(self):
        assert AnalyticsService.map_video_quality("hd") == VideoQuality.HD

    def test_480p_is_sd(self):
        assert AnalyticsService.map_video_quality("480p") == VideoQuality.SD

    def test_360p_is_low(self):
        assert AnalyticsService.map_video_quality("360p") == VideoQuality.LOW

    def test_unknown_string(self):
        assert AnalyticsService.map_video_quality("8k") == VideoQuality.UNKNOWN

    def test_none_is_unknown(self):
        assert AnalyticsService.map_video_quality(None) == VideoQuality.UNKNOWN

    def test_empty_string_is_unknown(self):
        assert AnalyticsService.map_video_quality("") == VideoQuality.UNKNOWN


# ── map_playback_method ────────────────────────────────────────────────────────


class TestMapPlaybackMethod:
    def test_transcoding_returns_transcoded(self):
        assert AnalyticsService.map_playback_method(True, False) == PlaybackMethod.TRANSCODED

    def test_transcoding_takes_precedence_over_direct_play(self):
        assert AnalyticsService.map_playback_method(True, True) == PlaybackMethod.TRANSCODED

    def test_direct_playing_returns_direct_play(self):
        assert AnalyticsService.map_playback_method(False, True) == PlaybackMethod.DIRECT_PLAY

    def test_neither_returns_direct_stream(self):
        assert AnalyticsService.map_playback_method(False, False) == PlaybackMethod.DIRECT_STREAM


# ── start_session ──────────────────────────────────────────────────────────────


class TestStartSession:
    def test_creates_session_with_correct_fields(self, db):
        data = {
            "media_id": "m001",
            "media_title": "Inception",
            "media_type": "movie",
            "user_id": "u001",
            "user_name": "alice",
            "client_name": "Jellyfin Web",
            "device_name": "Desktop",
            "video_quality": "1080p",
            "is_transcoding": False,
            "is_direct_playing": True,
            "duration_seconds": 3600,
        }
        session = AnalyticsService.start_session(db, data)

        assert session.id is not None
        assert session.media_title == "Inception"
        assert session.media_type == MediaType.MOVIE
        assert session.device_type == DeviceType.WEB_BROWSER
        assert session.video_quality == VideoQuality.FULL_HD
        assert session.playback_method == PlaybackMethod.DIRECT_PLAY
        assert session.status == SessionStatus.ACTIVE
        assert session.is_active is True
        assert session.watched_seconds == 0
        assert session.duration_seconds == 3600

    def test_transcoded_session_uses_correct_method(self, db):
        data = {
            "media_id": "m002",
            "media_title": "Avatar",
            "media_type": "movie",
            "user_id": "u002",
            "user_name": "bob",
            "client_name": "Jellyfin",
            "device_name": "Desktop",
            "video_quality": "4k hdr",
            "is_transcoding": True,
            "is_direct_playing": False,
        }
        session = AnalyticsService.start_session(db, data)

        assert session.playback_method == PlaybackMethod.TRANSCODED
        assert session.video_quality == VideoQuality.FOUR_K_HDR

    def test_tv_episode_session_maps_media_type(self, db):
        data = {
            "media_id": "ep001",
            "media_title": "Breaking Bad",
            "media_type": "tv",
            "episode_info": "S01E01",
            "user_id": "u003",
            "user_name": "carol",
            "client_name": "Jellyfin Android",
            "device_name": "Pixel 7",
            "video_quality": "720p",
            "is_transcoding": False,
            "is_direct_playing": True,
        }
        session = AnalyticsService.start_session(db, data)

        assert session.media_type == MediaType.TV
        assert session.episode_info == "S01E01"
        assert session.device_type == DeviceType.MOBILE_APP

    def test_session_is_persisted_in_db(self, db):
        data = {
            "media_id": "m003",
            "media_title": "Dune",
            "media_type": "movie",
            "user_id": "u004",
            "user_name": "dan",
            "client_name": "Firefox",
            "device_name": "PC",
            "video_quality": "4k",
            "is_transcoding": False,
            "is_direct_playing": True,
        }
        session = AnalyticsService.start_session(db, data)
        fetched = db.query(PlaybackSession).filter_by(id=session.id).first()
        assert fetched is not None
        assert fetched.media_title == "Dune"


# ── stop_session ───────────────────────────────────────────────────────────────


class TestStopSession:
    def test_stops_active_session(self, db, make_playback_session):
        make_playback_session(media_id="m1", user_id="u1", duration_seconds=3600)
        result = AnalyticsService.stop_session(db, "m1", "u1", watched_seconds=1800)

        assert result is not None
        assert result.status == SessionStatus.STOPPED
        assert result.is_active is False
        assert result.watched_seconds == 1800
        assert result.end_time is not None

    def test_nonexistent_session_returns_none(self, db):
        result = AnalyticsService.stop_session(db, "ghost", "u99", watched_seconds=100)
        assert result is None

    def test_fallback_to_elapsed_when_no_watched_seconds(self, db, make_playback_session):
        start = datetime.utcnow() - timedelta(seconds=500)
        make_playback_session(media_id="m2", user_id="u2", start_time=start, duration_seconds=3600)
        result = AnalyticsService.stop_session(db, "m2", "u2", watched_seconds=0)

        assert result.watched_seconds > 0
        assert result.watched_seconds <= 500

    def test_elapsed_capped_at_duration(self, db, make_playback_session):
        start = datetime.utcnow() - timedelta(seconds=10000)
        make_playback_session(media_id="m3", user_id="u3", start_time=start, duration_seconds=3600)
        result = AnalyticsService.stop_session(db, "m3", "u3", watched_seconds=0)

        assert result.watched_seconds == 3600

    def test_marks_movie_as_watched_above_30_percent(self, db, make_playback_session, make_library_item):
        movie = make_library_item(title="Inception", media_type=MediaType.MOVIE)
        make_playback_session(
            media_id="m4",
            user_id="u4",
            media_type=MediaType.MOVIE,
            duration_seconds=3600,
            library_item_id=movie.id,
        )
        AnalyticsService.stop_session(db, "m4", "u4", watched_seconds=2000)  # ~55 %

        db.refresh(movie)
        assert movie.watched is True

    def test_does_not_mark_movie_below_30_percent(self, db, make_playback_session, make_library_item):
        movie = make_library_item(title="Avatar", media_type=MediaType.MOVIE)
        make_playback_session(
            media_id="m5",
            user_id="u5",
            media_type=MediaType.MOVIE,
            duration_seconds=3600,
            library_item_id=movie.id,
        )
        AnalyticsService.stop_session(db, "m5", "u5", watched_seconds=500)  # ~13 %

        db.refresh(movie)
        assert movie.watched is False

    def test_marks_tv_episode_as_watched_above_threshold(self, db, make_playback_session, make_tv_show):
        show, _, episodes = make_tv_show()
        ep = episodes[0]  # S01E01

        make_playback_session(
            media_id="ep1",
            user_id="u6",
            media_type=MediaType.TV,
            episode_info="S01E01",
            duration_seconds=2400,
            library_item_id=show.id,
        )
        AnalyticsService.stop_session(db, "ep1", "u6", watched_seconds=1500)  # ~62 %

        db.refresh(ep)
        assert ep.watched is True

    def test_does_not_mark_tv_episode_below_threshold(self, db, make_playback_session, make_tv_show):
        show, _, episodes = make_tv_show()
        ep = episodes[0]  # S01E01

        make_playback_session(
            media_id="ep2",
            user_id="u7",
            media_type=MediaType.TV,
            episode_info="S01E01",
            duration_seconds=2400,
            library_item_id=show.id,
        )
        AnalyticsService.stop_session(db, "ep2", "u7", watched_seconds=300)  # ~12 %

        db.refresh(ep)
        assert ep.watched is False

    def test_stop_triggers_daily_analytics_update(self, db, make_playback_session):
        make_playback_session(media_id="m6", user_id="u8", duration_seconds=3600)
        AnalyticsService.stop_session(db, "m6", "u8", watched_seconds=1800)

        daily = db.query(DailyAnalytic).first()
        assert daily is not None
        assert daily.total_plays == 1

    def test_inactive_session_is_not_stopped_again(self, db, make_playback_session):
        make_playback_session(
            media_id="m7",
            user_id="u9",
            is_active=False,
            status=SessionStatus.STOPPED,
        )
        result = AnalyticsService.stop_session(db, "m7", "u9", watched_seconds=100)
        assert result is None


# ── pause_session ──────────────────────────────────────────────────────────────


class TestPauseSession:
    def test_pause_active_session(self, db, make_playback_session):
        make_playback_session(media_id="m1", user_id="u1")
        result = AnalyticsService.pause_session(db, "m1", "u1")

        assert result is not None
        assert result.status == SessionStatus.PAUSED
        assert result.is_active is True  # still active while paused

    def test_pause_nonexistent_returns_none(self, db):
        result = AnalyticsService.pause_session(db, "ghost", "u1")
        assert result is None

    def test_pause_is_persisted(self, db, make_playback_session):
        ps = make_playback_session(media_id="m2", user_id="u2")
        AnalyticsService.pause_session(db, "m2", "u2")

        db.refresh(ps)
        assert ps.status == SessionStatus.PAUSED


# ── resume_session ─────────────────────────────────────────────────────────────


class TestResumeSession:
    def test_resume_paused_session(self, db, make_playback_session):
        make_playback_session(media_id="m1", user_id="u1", status=SessionStatus.PAUSED)
        result = AnalyticsService.resume_session(db, "m1", "u1")

        assert result is not None
        assert result.status == SessionStatus.ACTIVE

    def test_resume_nonexistent_returns_none(self, db):
        result = AnalyticsService.resume_session(db, "ghost", "u1")
        assert result is None

    def test_resume_is_persisted(self, db, make_playback_session):
        ps = make_playback_session(media_id="m2", user_id="u2", status=SessionStatus.PAUSED)
        AnalyticsService.resume_session(db, "m2", "u2")

        db.refresh(ps)
        assert ps.status == SessionStatus.ACTIVE


# ── update_daily_analytics ─────────────────────────────────────────────────────


class TestUpdateDailyAnalytics:
    def test_creates_new_daily_analytic_for_movie(self, db, make_playback_session):
        ps = make_playback_session(
            watched_seconds=3600,
            media_type=MediaType.MOVIE,
            playback_method=PlaybackMethod.DIRECT_PLAY,
        )
        AnalyticsService.update_daily_analytics(db, ps)

        daily = db.query(DailyAnalytic).first()
        assert daily is not None
        assert daily.total_plays == 1
        assert daily.hours_watched == pytest.approx(1.0)
        assert daily.movies_played == 1
        assert daily.tv_episodes_played == 0
        assert daily.direct_play_count == 1
        assert daily.transcoded_count == 0

    def test_creates_new_daily_analytic_for_tv(self, db, make_playback_session):
        ps = make_playback_session(
            media_type=MediaType.TV,
            watched_seconds=1800,
            playback_method=PlaybackMethod.TRANSCODED,
        )
        AnalyticsService.update_daily_analytics(db, ps)

        daily = db.query(DailyAnalytic).first()
        assert daily.tv_episodes_played == 1
        assert daily.movies_played == 0
        assert daily.transcoded_count == 1
        assert daily.direct_play_count == 0

    def test_increments_existing_daily_analytic(self, db, make_playback_session):
        ps1 = make_playback_session(media_id="a", user_id="u1", watched_seconds=3600, media_type=MediaType.MOVIE)
        AnalyticsService.update_daily_analytics(db, ps1)
        ps2 = make_playback_session(media_id="b", user_id="u2", watched_seconds=1800, media_type=MediaType.TV)
        AnalyticsService.update_daily_analytics(db, ps2)

        daily = db.query(DailyAnalytic).first()
        assert daily.total_plays == 2
        assert daily.movies_played == 1
        assert daily.tv_episodes_played == 1
        assert daily.hours_watched == pytest.approx(1.5)

    def test_unique_users_deduplicated(self, db, make_playback_session):
        ps1 = make_playback_session(media_id="a", user_id="same_user", watched_seconds=100)
        AnalyticsService.update_daily_analytics(db, ps1)
        ps2 = make_playback_session(media_id="b", user_id="same_user", watched_seconds=100)
        AnalyticsService.update_daily_analytics(db, ps2)

        daily = db.query(DailyAnalytic).first()
        assert daily.unique_users == 1

    def test_unique_media_deduplicated(self, db, make_playback_session):
        ps1 = make_playback_session(media_id="same_media", user_id="u1", watched_seconds=100)
        AnalyticsService.update_daily_analytics(db, ps1)
        ps2 = make_playback_session(media_id="same_media", user_id="u2", watched_seconds=100)
        AnalyticsService.update_daily_analytics(db, ps2)

        daily = db.query(DailyAnalytic).first()
        assert daily.unique_media == 1

    def test_hours_watched_conversion(self, db, make_playback_session):
        ps = make_playback_session(watched_seconds=5400)  # 1.5 hours
        AnalyticsService.update_daily_analytics(db, ps)

        daily = db.query(DailyAnalytic).first()
        assert daily.hours_watched == pytest.approx(1.5)


# ── get_active_sessions ────────────────────────────────────────────────────────


class TestGetActiveSessions:
    def test_returns_only_active_sessions(self, db, make_playback_session):
        make_playback_session(media_id="active", is_active=True)
        make_playback_session(media_id="stopped", is_active=False, status=SessionStatus.STOPPED)

        sessions = AnalyticsService.get_active_sessions(db)
        assert len(sessions) == 1
        assert sessions[0].media_id == "active"

    def test_returns_empty_list_when_none_active(self, db):
        sessions = AnalyticsService.get_active_sessions(db)
        assert sessions == []

    def test_ordered_by_start_time_desc(self, db, make_playback_session):
        t1 = datetime.utcnow() - timedelta(minutes=10)
        t2 = datetime.utcnow() - timedelta(minutes=5)
        make_playback_session(media_id="older", start_time=t1)
        make_playback_session(media_id="newer", start_time=t2)

        sessions = AnalyticsService.get_active_sessions(db)
        assert sessions[0].media_id == "newer"
        assert sessions[1].media_id == "older"


# ── cleanup_orphan_sessions ────────────────────────────────────────────────────


class TestCleanupOrphanSessions:
    def test_cleans_sessions_older_than_timeout(self, db, make_playback_session):
        old_start = datetime.utcnow() - timedelta(hours=30)
        make_playback_session(media_id="old", start_time=old_start)

        count = AnalyticsService.cleanup_orphan_sessions(db, timeout_hours=24)

        assert count == 1
        session = db.query(PlaybackSession).filter_by(media_id="old").first()
        assert session.is_active is False
        assert session.status == SessionStatus.STOPPED
        assert session.end_time is not None

    def test_does_not_clean_recent_sessions(self, db, make_playback_session):
        recent_start = datetime.utcnow() - timedelta(hours=2)
        make_playback_session(media_id="recent", start_time=recent_start)

        count = AnalyticsService.cleanup_orphan_sessions(db, timeout_hours=24)

        assert count == 0
        session = db.query(PlaybackSession).filter_by(media_id="recent").first()
        assert session.is_active is True

    def test_returns_zero_when_no_orphans(self, db):
        count = AnalyticsService.cleanup_orphan_sessions(db)
        assert count == 0

    def test_cleans_multiple_orphans(self, db, make_playback_session):
        old = datetime.utcnow() - timedelta(hours=48)
        make_playback_session(media_id="orphan1", start_time=old)
        make_playback_session(media_id="orphan2", start_time=old)
        make_playback_session(media_id="recent", start_time=datetime.utcnow())

        count = AnalyticsService.cleanup_orphan_sessions(db, timeout_hours=24)
        assert count == 2

    def test_does_not_estimate_watched_seconds(self, db, make_playback_session):
        old_start = datetime.utcnow() - timedelta(hours=30)
        make_playback_session(media_id="orphan", start_time=old_start, watched_seconds=0)

        AnalyticsService.cleanup_orphan_sessions(db, timeout_hours=24)

        session = db.query(PlaybackSession).filter_by(media_id="orphan").first()
        assert session.watched_seconds == 0  # not estimated for orphans


# ── update_device_statistics ───────────────────────────────────────────────────


class TestUpdateDeviceStatistics:
    def test_creates_device_stat_for_target_date(self, db, make_playback_session):
        target = date.today()
        start_of_day = datetime(target.year, target.month, target.day, 12, 0, 0)

        make_playback_session(
            media_id="a",
            user_id="u1",
            device_type=DeviceType.WEB_BROWSER,
            start_time=start_of_day,
            is_active=False,
            status=SessionStatus.STOPPED,
            watched_seconds=600,
        )

        AnalyticsService.update_device_statistics(db, target)

        stat = db.query(DeviceStatistic).filter_by(device_type=DeviceType.WEB_BROWSER).first()
        assert stat is not None
        assert stat.session_count == 1
        assert stat.total_duration_seconds == 600
        assert stat.unique_users == 1
        assert stat.period_start == target
        assert stat.period_end == target

    def test_skips_device_types_with_no_sessions(self, db):
        AnalyticsService.update_device_statistics(db, date.today())
        stats = db.query(DeviceStatistic).all()
        assert stats == []

    def test_updates_existing_device_stat(self, db, make_playback_session, make_device_statistic):
        target = date.today()
        existing = make_device_statistic(
            device_type=DeviceType.WEB_BROWSER,
            period_start=target,
            period_end=target,
            session_count=99,  # will be overwritten
        )

        start_of_day = datetime(target.year, target.month, target.day, 12, 0, 0)
        make_playback_session(
            media_id="new",
            user_id="u99",
            device_type=DeviceType.WEB_BROWSER,
            start_time=start_of_day,
            is_active=False,
            status=SessionStatus.STOPPED,
            watched_seconds=1200,
        )

        AnalyticsService.update_device_statistics(db, target)
        db.refresh(existing)

        assert existing.session_count == 1  # overwritten with current count
        assert existing.total_duration_seconds == 1200

    def test_multiple_users_aggregated(self, db, make_playback_session):
        target = date.today()
        start_of_day = datetime(target.year, target.month, target.day, 10, 0, 0)

        make_playback_session(
            media_id="a",
            user_id="u1",
            device_type=DeviceType.MOBILE_APP,
            start_time=start_of_day,
            is_active=False,
            status=SessionStatus.STOPPED,
            watched_seconds=300,
        )
        make_playback_session(
            media_id="b",
            user_id="u2",
            device_type=DeviceType.MOBILE_APP,
            start_time=start_of_day,
            is_active=False,
            status=SessionStatus.STOPPED,
            watched_seconds=600,
        )

        AnalyticsService.update_device_statistics(db, target)

        stat = db.query(DeviceStatistic).filter_by(device_type=DeviceType.MOBILE_APP).first()
        assert stat.session_count == 2
        assert stat.total_duration_seconds == 900
        assert stat.unique_users == 2

    def test_uses_yesterday_when_no_date_given(self, db, make_playback_session):
        yesterday = date.today() - timedelta(days=1)
        start_of_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 12, 0, 0)

        make_playback_session(
            media_id="y",
            user_id="u1",
            device_type=DeviceType.DESKTOP_APP,
            start_time=start_of_yesterday,
            is_active=False,
            status=SessionStatus.STOPPED,
            watched_seconds=200,
        )

        AnalyticsService.update_device_statistics(db)  # no date → uses yesterday

        stat = db.query(DeviceStatistic).filter_by(device_type=DeviceType.DESKTOP_APP).first()
        assert stat is not None
        assert stat.period_start == yesterday
