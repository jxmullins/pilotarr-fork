"""Unit tests for MetricsService."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.models.models import ServerMetric
from app.services.metrics_service import MetricsService

# ── determine_status ───────────────────────────────────────────────────────────


class TestDetermineStatus:
    def test_below_warning_threshold_is_success(self):
        assert MetricsService.determine_status(50.0, 70, 90) == "success"

    def test_at_warning_threshold_is_warning(self):
        assert MetricsService.determine_status(70.0, 70, 90) == "warning"

    def test_between_warning_and_error_is_warning(self):
        assert MetricsService.determine_status(80.0, 70, 90) == "warning"

    def test_at_error_threshold_is_error(self):
        assert MetricsService.determine_status(90.0, 70, 90) == "error"

    def test_above_error_threshold_is_error(self):
        assert MetricsService.determine_status(95.0, 70, 90) == "error"

    def test_zero_value_is_success(self):
        assert MetricsService.determine_status(0.0, 70, 90) == "success"


# ── capture_metrics ────────────────────────────────────────────────────────────


class TestCaptureMetrics:
    def _mock_psutil(
        self, cpu=25.0, mem_used_gb=8.0, mem_total_gb=16.0, disk_used_tb=2.0, disk_total_tb=10.0, bandwidth_mbps=50.0
    ):
        cpu_patch = patch.object(MetricsService, "get_cpu_usage", return_value=cpu)
        mem_patch = patch.object(MetricsService, "get_memory_usage", return_value=(mem_used_gb, mem_total_gb))
        disk_patch = patch.object(MetricsService, "get_disk_usage", return_value=(disk_used_tb, disk_total_tb))
        bw_patch = patch.object(MetricsService, "get_network_bandwidth", return_value=bandwidth_mbps)
        return cpu_patch, mem_patch, disk_patch, bw_patch

    def test_creates_server_metric_record(self, db):
        patches = self._mock_psutil()
        with patches[0], patches[1], patches[2], patches[3]:
            metric = MetricsService.capture_metrics(db)

        assert metric.id is not None
        assert metric.cpu_usage_percent == pytest.approx(25.0)
        assert metric.memory_usage_gb == pytest.approx(8.0)
        assert metric.memory_total_gb == pytest.approx(16.0)
        assert metric.storage_used_tb == pytest.approx(2.0)
        assert metric.storage_total_tb == pytest.approx(10.0)
        assert metric.bandwidth_mbps == pytest.approx(50.0)

    def test_cpu_status_set_correctly(self, db):
        patches = self._mock_psutil(cpu=95.0)  # > 90 → error
        with patches[0], patches[1], patches[2], patches[3]:
            metric = MetricsService.capture_metrics(db)

        assert metric.cpu_status == "error"

    def test_memory_status_set_correctly(self, db):
        # 12 GB used / 16 GB total = 75% → warning
        patches = self._mock_psutil(mem_used_gb=12.0, mem_total_gb=16.0)
        with patches[0], patches[1], patches[2], patches[3]:
            metric = MetricsService.capture_metrics(db)

        assert metric.memory_status == "warning"

    def test_storage_status_set_correctly(self, db):
        # 9.5 TB / 10 TB = 95% → error (threshold: 80/95)
        patches = self._mock_psutil(disk_used_tb=9.5, disk_total_tb=10.0)
        with patches[0], patches[1], patches[2], patches[3]:
            metric = MetricsService.capture_metrics(db)

        assert metric.storage_status == "error"

    def test_bandwidth_warning_above_100mbps(self, db):
        patches = self._mock_psutil(bandwidth_mbps=150.0)
        with patches[0], patches[1], patches[2], patches[3]:
            metric = MetricsService.capture_metrics(db)

        assert metric.bandwidth_status == "warning"

    def test_bandwidth_error_above_500mbps(self, db):
        patches = self._mock_psutil(bandwidth_mbps=600.0)
        with patches[0], patches[1], patches[2], patches[3]:
            metric = MetricsService.capture_metrics(db)

        assert metric.bandwidth_status == "error"

    def test_counts_active_sessions(self, db, make_playback_session):
        make_playback_session(media_id="a", is_active=True)
        make_playback_session(media_id="b", is_active=True)
        make_playback_session(media_id="c", is_active=False)

        patches = self._mock_psutil()
        with patches[0], patches[1], patches[2], patches[3]:
            metric = MetricsService.capture_metrics(db)

        assert metric.active_sessions_count == 2

    def test_counts_active_transcoding(self, db, make_playback_session):
        make_playback_session(media_id="t1", is_active=True, transcoding_progress=45)
        make_playback_session(media_id="t2", is_active=True, transcoding_progress=0)
        make_playback_session(media_id="t3", is_active=False, transcoding_progress=80)

        patches = self._mock_psutil()
        with patches[0], patches[1], patches[2], patches[3]:
            metric = MetricsService.capture_metrics(db)

        assert metric.active_transcoding_count == 1

    def test_metric_is_persisted(self, db):
        patches = self._mock_psutil()
        with patches[0], patches[1], patches[2], patches[3]:
            MetricsService.capture_metrics(db)

        count = db.query(ServerMetric).count()
        assert count == 1


# ── cleanup_old_metrics ────────────────────────────────────────────────────────


class TestCleanupOldMetrics:
    def test_deletes_metrics_older_than_keep_days(self, db, make_server_metric):
        old_metric = make_server_metric()
        # Backdating the recorded_at column
        old_metric.recorded_at = datetime.utcnow() - timedelta(days=10)
        db.commit()

        MetricsService.cleanup_old_metrics(db, keep_days=7)

        assert db.query(ServerMetric).count() == 0

    def test_keeps_recent_metrics(self, db, make_server_metric):
        make_server_metric()  # recorded_at defaults to now

        MetricsService.cleanup_old_metrics(db, keep_days=7)

        assert db.query(ServerMetric).count() == 1

    def test_partial_cleanup(self, db, make_server_metric):
        recent = make_server_metric()
        old = make_server_metric()
        old.recorded_at = datetime.utcnow() - timedelta(days=30)
        db.commit()

        MetricsService.cleanup_old_metrics(db, keep_days=7)

        assert db.query(ServerMetric).count() == 1
        assert db.query(ServerMetric).first().id == recent.id

    def test_no_metrics_to_cleanup(self, db):
        # Should not raise
        MetricsService.cleanup_old_metrics(db, keep_days=7)
        assert db.query(ServerMetric).count() == 0
