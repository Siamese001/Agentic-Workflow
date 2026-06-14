"""Unit tests for agentic_core.L4_state.adapters.sqlite3_adapter.

W6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — P2 L4 sqlite3 adapter.
This is the ONE sanctioned sqlite3 import surface (constitutional §22).
Exercises real round-trip CRUD against tmp/in-memory databases: governed
connect() defaults (Row factory, WAL, foreign keys), the schema helpers
(ensure_schema idempotency, table_exists / table_schema / table_columns),
row counting, and the maintenance helpers (vacuum / optimize).
"""

from __future__ import annotations

import sqlite3

import pytest

from agentic_core.L4_state.adapters import sqlite3_adapter as l4_sqlite3

_CREATE = "CREATE TABLE widgets (id INTEGER PRIMARY KEY, name TEXT NOT NULL, qty INTEGER DEFAULT 0)"


@pytest.fixture()
def db_path(tmp_path) -> str:
    return str(tmp_path / "test.sqlite")


# ---------------------------------------------------------------------------
class TestReexports:
    def test_sqlite3_module_reexported(self) -> None:
        assert l4_sqlite3.sqlite3 is sqlite3

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Connection", sqlite3.Connection),
            ("Cursor", sqlite3.Cursor),
            ("Row", sqlite3.Row),
            ("IntegrityError", sqlite3.IntegrityError),
            ("OperationalError", sqlite3.OperationalError),
            ("ProgrammingError", sqlite3.ProgrammingError),
        ],
    )
    def test_type_reexports(self, name: str, expected: type) -> None:
        assert getattr(l4_sqlite3, name) is expected


# ---------------------------------------------------------------------------
class TestConnect:
    def test_row_factory_is_row(self, db_path: str) -> None:
        conn = l4_sqlite3.connect(db_path)
        try:
            assert conn.row_factory is sqlite3.Row
        finally:
            conn.close()

    def test_foreign_keys_enabled_by_default(self, db_path: str) -> None:
        conn = l4_sqlite3.connect(db_path)
        try:
            assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        finally:
            conn.close()

    def test_foreign_keys_disabled_when_requested(self, db_path: str) -> None:
        conn = l4_sqlite3.connect(db_path, foreign_keys=False)
        try:
            assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 0
        finally:
            conn.close()

    def test_wal_journal_mode_on_disk(self, db_path: str) -> None:
        conn = l4_sqlite3.connect(db_path, wal=True)
        try:
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            assert mode.lower() == "wal"
        finally:
            conn.close()

    def test_accepts_in_memory_database(self) -> None:
        conn = l4_sqlite3.connect(":memory:")
        try:
            assert conn.execute("SELECT 1").fetchone()[0] == 1
        finally:
            conn.close()


# ---------------------------------------------------------------------------
class TestConnectionContextManager:
    def test_context_yields_usable_connection(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            conn.execute("INSERT INTO widgets (name, qty) VALUES (?, ?)", ("a", 3))
            conn.commit()
            row = conn.execute("SELECT name, qty FROM widgets").fetchone()
            assert row["name"] == "a"
            assert row["qty"] == 3

    def test_connection_closed_after_context(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            pass
        # A closed connection raises ProgrammingError on further use.
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")


# ---------------------------------------------------------------------------
class TestCrudRoundTrip:
    def test_insert_update_delete_roundtrip(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            conn.execute("INSERT INTO widgets (id, name, qty) VALUES (1, 'gear', 5)")
            conn.commit()
            assert l4_sqlite3.count_rows(conn, "widgets") == 1

            conn.execute("UPDATE widgets SET qty = 9 WHERE id = 1")
            conn.commit()
            assert conn.execute("SELECT qty FROM widgets WHERE id=1").fetchone()["qty"] == 9

            conn.execute("DELETE FROM widgets WHERE id = 1")
            conn.commit()
            assert l4_sqlite3.count_rows(conn, "widgets") == 0

    def test_not_null_constraint_raises_integrity_error(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            with pytest.raises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO widgets (id, name) VALUES (1, NULL)")


# ---------------------------------------------------------------------------
class TestSchemaHelpers:
    def test_table_exists_true_and_false(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            assert l4_sqlite3.table_exists(conn, "widgets") is False
            conn.execute(_CREATE)
            assert l4_sqlite3.table_exists(conn, "widgets") is True

    def test_table_schema_returns_create_sql_or_none(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            assert l4_sqlite3.table_schema(conn, "widgets") is None
            conn.execute(_CREATE)
            schema = l4_sqlite3.table_schema(conn, "widgets")
            assert schema is not None and "CREATE TABLE widgets" in schema

    def test_table_columns(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            assert l4_sqlite3.table_columns(conn, "widgets") == ["id", "name", "qty"]

    def test_ensure_schema_creates_then_is_idempotent(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            created = l4_sqlite3.ensure_schema(conn, "widgets", _CREATE)
            assert created is True
            assert l4_sqlite3.table_exists(conn, "widgets") is True
            # Second call: table already exists -> returns False, no error.
            again = l4_sqlite3.ensure_schema(conn, "widgets", _CREATE)
            assert again is False

    def test_ensure_schema_applies_migrations_on_create(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            created = l4_sqlite3.ensure_schema(
                conn,
                "widgets",
                _CREATE,
                migrations=["ALTER TABLE widgets ADD COLUMN tag TEXT"],
            )
            assert created is True
            assert "tag" in l4_sqlite3.table_columns(conn, "widgets")

    def test_ensure_schema_swallows_existing_column_migration(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            conn.execute("ALTER TABLE widgets ADD COLUMN tag TEXT")
            # Re-running with a duplicate-column migration must not raise.
            result = l4_sqlite3.ensure_schema(
                conn,
                "widgets",
                _CREATE,
                migrations=["ALTER TABLE widgets ADD COLUMN tag TEXT"],
            )
            assert result is False


# ---------------------------------------------------------------------------
class TestCounting:
    def test_count_rows_empty(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            assert l4_sqlite3.count_rows(conn, "widgets") == 0

    def test_count_rows_multiple(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            conn.executemany(
                "INSERT INTO widgets (name) VALUES (?)", [("a",), ("b",), ("c",)]
            )
            conn.commit()
            assert l4_sqlite3.count_rows(conn, "widgets") == 3


# ---------------------------------------------------------------------------
class TestMaintenance:
    def test_vacuum_runs(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            conn.commit()
            # vacuum cannot run inside an open transaction; ensure none pending.
            l4_sqlite3.vacuum(conn)

    def test_optimize_runs(self, db_path: str) -> None:
        with l4_sqlite3.connection(db_path) as conn:
            conn.execute(_CREATE)
            l4_sqlite3.optimize(conn)
