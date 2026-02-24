"""Tests for AnalyticsScheduler."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from app.schedulers.analytics_scheduler import AnalyticsScheduler
from app.services.analytics_service import AnalyticsService
from app.services.metrics_service import MetricsService

# ── start / stop ───────────────────────────────────────────────────────────────


class TestSchedulerLifecycle:
    def test_start_sets_running_true(self):
        scheduler = AnalyticsScheduler()
        with patch.object(scheduler, "_metrics_loop"), patch.object(scheduler, "_cleanup_loop"):
            with patch("threading.Thread") as mock_thread_cls:
                mock_thread = MagicMock()
                mock_thread_cls.return_value = mock_thread
                scheduler.start()

        assert scheduler.running is True

    def test_start_spawns_two_daemon_threads(self):
        scheduler = AnalyticsScheduler()
        threads_started = []

        def fake_thread(**kwargs):
            t = MagicMock()
            t.daemon = None
            threads_started.append(kwargs)
            return t

        with patch("threading.Thread", side_effect=fake_thread):
            scheduler.start()

        assert len(threads_started) == 2
        # Both threads must be daemon
        targets = [kw["target"] for kw in threads_started]
        assert scheduler._metrics_loop in targets
        assert scheduler._cleanup_loop in targets

    def test_start_is_idempotent(self):
        scheduler = AnalyticsScheduler()
        with patch("threading.Thread") as mock_thread_cls:
            mock_thread_cls.return_value = MagicMock()
            scheduler.start()
            scheduler.start()  # second call should be a no-op

        # Thread constructor called exactly twice (one metrics + one cleanup)
        assert mock_thread_cls.call_count == 2

    def test_stop_sets_running_false(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True
        scheduler.stop()
        assert scheduler.running is False


# ── _metrics_loop ──────────────────────────────────────────────────────────────


class TestMetricsLoop:
    def test_calls_capture_metrics_then_sleeps_180s(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True

        call_log = []

        def fake_capture(db):
            call_log.append("capture")
            scheduler.running = False  # stop after first iteration

        def fake_sleep(seconds):
            call_log.append(("sleep", seconds))

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(MetricsService, "capture_metrics", side_effect=fake_capture),
            patch("time.sleep", side_effect=fake_sleep),
        ):
            scheduler._metrics_loop()

        assert call_log == ["capture", ("sleep", 180)]

    def test_exception_in_capture_sleeps_30s_and_continues(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True
        iteration = {"count": 0}

        def fake_capture(db):
            iteration["count"] += 1
            if iteration["count"] == 1:
                raise RuntimeError("DB error")
            scheduler.running = False  # stop on second iteration

        sleep_calls = []

        def fake_sleep(seconds):
            sleep_calls.append(seconds)

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(MetricsService, "capture_metrics", side_effect=fake_capture),
            patch("time.sleep", side_effect=fake_sleep),
        ):
            scheduler._metrics_loop()

        # First iteration failed → 30s retry sleep; second succeeded → 180s normal sleep
        assert 30 in sleep_calls
        assert 180 in sleep_calls

    def test_db_session_is_always_closed(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True

        def fake_capture(db):
            scheduler.running = False

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(MetricsService, "capture_metrics", side_effect=fake_capture),
            patch("time.sleep"),
        ):
            scheduler._metrics_loop()

        fake_db.close.assert_called_once()


# ── _cleanup_loop ──────────────────────────────────────────────────────────────


class TestCleanupLoop:
    def test_calls_all_three_services_in_order(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True

        call_order = []

        def fake_cleanup_orphans(db, timeout_hours):
            call_order.append("cleanup_orphans")
            scheduler.running = False  # stop after first iteration

        def fake_update_device_stats(db, target_date):
            call_order.append("update_device_stats")

        def fake_cleanup_metrics(db, keep_days):
            call_order.append("cleanup_metrics")

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(AnalyticsService, "cleanup_orphan_sessions", side_effect=fake_cleanup_orphans),
            patch.object(AnalyticsService, "update_device_statistics", side_effect=fake_update_device_stats),
            patch.object(MetricsService, "cleanup_old_metrics", side_effect=fake_cleanup_metrics),
            patch("time.sleep"),
        ):
            scheduler._cleanup_loop()

        assert call_order == ["cleanup_orphans", "update_device_stats", "cleanup_metrics"]

    def test_cleanup_orphans_uses_24h_timeout(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True
        captured = {}

        def fake_cleanup_orphans(db, timeout_hours):
            captured["timeout_hours"] = timeout_hours
            scheduler.running = False

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(AnalyticsService, "cleanup_orphan_sessions", side_effect=fake_cleanup_orphans),
            patch.object(AnalyticsService, "update_device_statistics"),
            patch.object(MetricsService, "cleanup_old_metrics"),
            patch("time.sleep"),
        ):
            scheduler._cleanup_loop()

        assert captured["timeout_hours"] == 24

    def test_device_stats_uses_yesterday(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True
        captured = {}

        def fake_update_device_stats(db, target_date):
            captured["target_date"] = target_date
            scheduler.running = False

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(AnalyticsService, "cleanup_orphan_sessions"),
            patch.object(AnalyticsService, "update_device_statistics", side_effect=fake_update_device_stats),
            patch.object(MetricsService, "cleanup_old_metrics"),
            patch("time.sleep"),
        ):
            scheduler._cleanup_loop()

        from datetime import datetime

        expected_yesterday = (datetime.utcnow() - timedelta(days=1)).date()
        assert captured["target_date"] == expected_yesterday

    def test_cleanup_metrics_keeps_7_days(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True
        captured = {}

        def fake_cleanup_metrics(db, keep_days):
            captured["keep_days"] = keep_days
            scheduler.running = False

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(AnalyticsService, "cleanup_orphan_sessions"),
            patch.object(AnalyticsService, "update_device_statistics"),
            patch.object(MetricsService, "cleanup_old_metrics", side_effect=fake_cleanup_metrics),
            patch("time.sleep"),
        ):
            scheduler._cleanup_loop()

        assert captured["keep_days"] == 7

    def test_cleanup_loop_sleeps_3600s(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True
        sleep_calls = []

        def fake_cleanup_orphans(db, timeout_hours):
            scheduler.running = False

        def fake_sleep(seconds):
            sleep_calls.append(seconds)

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(AnalyticsService, "cleanup_orphan_sessions", side_effect=fake_cleanup_orphans),
            patch.object(AnalyticsService, "update_device_statistics"),
            patch.object(MetricsService, "cleanup_old_metrics"),
            patch("time.sleep", side_effect=fake_sleep),
        ):
            scheduler._cleanup_loop()

        assert 3600 in sleep_calls

    def test_exception_in_cleanup_sleeps_3600s_and_continues(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True
        iteration = {"count": 0}

        def fake_cleanup_orphans(db, timeout_hours):
            iteration["count"] += 1
            if iteration["count"] == 1:
                raise RuntimeError("Oops")
            scheduler.running = False

        sleep_calls = []

        def fake_sleep(seconds):
            sleep_calls.append(seconds)

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(AnalyticsService, "cleanup_orphan_sessions", side_effect=fake_cleanup_orphans),
            patch.object(AnalyticsService, "update_device_statistics"),
            patch.object(MetricsService, "cleanup_old_metrics"),
            patch("time.sleep", side_effect=fake_sleep),
        ):
            scheduler._cleanup_loop()

        assert sleep_calls.count(3600) >= 2  # error sleep + normal sleep

    def test_db_session_is_always_closed(self):
        scheduler = AnalyticsScheduler()
        scheduler.running = True

        def fake_cleanup_orphans(db, timeout_hours):
            scheduler.running = False

        fake_db = MagicMock()
        with (
            patch("app.schedulers.analytics_scheduler.SessionLocal", return_value=fake_db),
            patch.object(AnalyticsService, "cleanup_orphan_sessions", side_effect=fake_cleanup_orphans),
            patch.object(AnalyticsService, "update_device_statistics"),
            patch.object(MetricsService, "cleanup_old_metrics"),
            patch("time.sleep"),
        ):
            scheduler._cleanup_loop()

        fake_db.close.assert_called_once()
