"""
Unit tests for user authentication schema migrations.
"""

from unittest.mock import MagicMock, patch


class TestMigrateAddTokenVersionToUsers:
    def test_executes_alter_table_when_token_version_missing(self):
        from app.db_migrations import migrate_add_token_version_to_users

        inspector = MagicMock()
        inspector.get_columns.return_value = [
            {"name": "id", "type": "VARCHAR(36)"},
            {"name": "username", "type": "VARCHAR(100)"},
        ]
        db = MagicMock()

        with (
            patch("app.db_migrations.inspect", return_value=inspector),
            patch("app.db.SessionLocal", return_value=db),
        ):
            migrate_add_token_version_to_users()

        db.execute.assert_called_once()
        sql = str(db.execute.call_args[0][0])
        assert "ALTER TABLE users" in sql
        assert "token_version" in sql
        db.commit.assert_called_once()
