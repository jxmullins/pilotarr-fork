"""
Unit tests for radarr ENUM migration functions.

These migrations guard against a production issue where the MySQL
service_name ENUM column was created without 'radarr'. The prowlarr
migrations skip when 'prowlarr' is already present, leaving 'radarr'
potentially missing on older installs.

Tests mock inspect() and SessionLocal so no real DB is required.
"""

from unittest.mock import MagicMock, patch

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_inspector(col_type: str):
    """Return a mock inspector whose get_columns() reports the given type."""
    col = {"name": "service_name", "type": col_type}
    inspector = MagicMock()
    inspector.get_columns.return_value = [col]
    return inspector


def _patch_inspect(col_type: str):
    inspector = _make_inspector(col_type)
    return patch("app.db_migrations.inspect", return_value=inspector)


def _patch_session():
    db = MagicMock()
    return patch("app.db.SessionLocal", return_value=db), db


# ── migrate_add_radarr_to_service_configurations_enum ─────────────────────────


class TestMigrateAddRadarrToServiceConfigurations:
    def test_skips_when_radarr_already_present(self, capsys):
        from app.db_migrations import migrate_add_radarr_to_service_configurations_enum

        with _patch_inspect("ENUM('jellyfin','sonarr','radarr','prowlarr')"):
            migrate_add_radarr_to_service_configurations_enum()

        out = capsys.readouterr().out
        assert "skipping" in out
        assert "radarr" in out

    def test_skips_when_column_is_not_enum(self, capsys):
        from app.db_migrations import migrate_add_radarr_to_service_configurations_enum

        with _patch_inspect("VARCHAR(50)"):
            migrate_add_radarr_to_service_configurations_enum()

        out = capsys.readouterr().out
        assert "not an ENUM" in out

    def test_skips_when_service_name_column_missing(self, capsys):
        from app.db_migrations import migrate_add_radarr_to_service_configurations_enum

        inspector = MagicMock()
        inspector.get_columns.return_value = [{"name": "other_col", "type": "VARCHAR"}]
        with patch("app.db_migrations.inspect", return_value=inspector):
            migrate_add_radarr_to_service_configurations_enum()

        out = capsys.readouterr().out
        assert "not found" in out

    def test_executes_alter_table_when_radarr_missing(self):
        from app.db_migrations import migrate_add_radarr_to_service_configurations_enum

        db = MagicMock()
        with (
            _patch_inspect("ENUM('jellyfin','jellyseerr','sonarr','qbittorrent','prowlarr')"),
            patch("app.db.SessionLocal", return_value=db),
        ):
            migrate_add_radarr_to_service_configurations_enum()

        db.execute.assert_called_once()
        sql = str(db.execute.call_args[0][0])
        assert "ALTER TABLE service_configurations" in sql
        assert "radarr" in sql
        db.commit.assert_called_once()

    def test_rollback_on_exception(self):
        from app.db_migrations import migrate_add_radarr_to_service_configurations_enum

        db = MagicMock()
        db.execute.side_effect = Exception("DB error")
        with (
            _patch_inspect("ENUM('jellyfin','sonarr','prowlarr')"),
            patch("app.db.SessionLocal", return_value=db),
            patch("builtins.print"),  # suppress output
        ):
            try:
                migrate_add_radarr_to_service_configurations_enum()
            except Exception:
                pass

        db.rollback.assert_called_once()

    def test_closes_session_on_success(self):
        from app.db_migrations import migrate_add_radarr_to_service_configurations_enum

        db = MagicMock()
        with (
            _patch_inspect("ENUM('jellyfin','sonarr','prowlarr')"),
            patch("app.db.SessionLocal", return_value=db),
        ):
            migrate_add_radarr_to_service_configurations_enum()

        db.close.assert_called_once()

    def test_closes_session_on_exception(self):
        from app.db_migrations import migrate_add_radarr_to_service_configurations_enum

        db = MagicMock()
        db.execute.side_effect = Exception("DB error")
        with (
            _patch_inspect("ENUM('jellyfin','sonarr','prowlarr')"),
            patch("app.db.SessionLocal", return_value=db),
            patch("builtins.print"),
        ):
            try:
                migrate_add_radarr_to_service_configurations_enum()
            except Exception:
                pass

        db.close.assert_called_once()


# ── migrate_add_radarr_to_sync_metadata_enum ─────────────────────────────────


class TestMigrateAddRadarrToSyncMetadata:
    def test_skips_when_radarr_already_present(self, capsys):
        from app.db_migrations import migrate_add_radarr_to_sync_metadata_enum

        with _patch_inspect("ENUM('jellyfin','sonarr','radarr','prowlarr')"):
            migrate_add_radarr_to_sync_metadata_enum()

        out = capsys.readouterr().out
        assert "skipping" in out

    def test_skips_when_column_is_not_enum(self, capsys):
        from app.db_migrations import migrate_add_radarr_to_sync_metadata_enum

        with _patch_inspect("VARCHAR(50)"):
            migrate_add_radarr_to_sync_metadata_enum()

        out = capsys.readouterr().out
        assert "not an ENUM" in out

    def test_skips_when_service_name_column_missing(self, capsys):
        from app.db_migrations import migrate_add_radarr_to_sync_metadata_enum

        inspector = MagicMock()
        inspector.get_columns.return_value = [{"name": "other_col", "type": "VARCHAR"}]
        with patch("app.db_migrations.inspect", return_value=inspector):
            migrate_add_radarr_to_sync_metadata_enum()

        out = capsys.readouterr().out
        assert "not found" in out

    def test_executes_alter_table_when_radarr_missing(self):
        from app.db_migrations import migrate_add_radarr_to_sync_metadata_enum

        db = MagicMock()
        with (
            _patch_inspect("ENUM('jellyfin','jellyseerr','sonarr','qbittorrent','prowlarr')"),
            patch("app.db.SessionLocal", return_value=db),
        ):
            migrate_add_radarr_to_sync_metadata_enum()

        db.execute.assert_called_once()
        sql = str(db.execute.call_args[0][0])
        assert "ALTER TABLE sync_metadata" in sql
        assert "radarr" in sql
        db.commit.assert_called_once()

    def test_rollback_on_exception(self):
        from app.db_migrations import migrate_add_radarr_to_sync_metadata_enum

        db = MagicMock()
        db.execute.side_effect = Exception("DB error")
        with (
            _patch_inspect("ENUM('jellyfin','sonarr','prowlarr')"),
            patch("app.db.SessionLocal", return_value=db),
            patch("builtins.print"),
        ):
            try:
                migrate_add_radarr_to_sync_metadata_enum()
            except Exception:
                pass

        db.rollback.assert_called_once()

    def test_closes_session_on_success(self):
        from app.db_migrations import migrate_add_radarr_to_sync_metadata_enum

        db = MagicMock()
        with (
            _patch_inspect("ENUM('jellyfin','sonarr','prowlarr')"),
            patch("app.db.SessionLocal", return_value=db),
        ):
            migrate_add_radarr_to_sync_metadata_enum()

        db.close.assert_called_once()
