"""Micro-evals for ADG SQLite hardening and WAL checkpoint targeting."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv  # noqa: E402
from tools.generate.sqlite_hardening import (  # noqa: E402
    harden_sqlite_connection,
    seal_sqlite_connection,
    seal_sqlite_path,
)
from tools.generate.utils import file_utils  # noqa: E402


def _make_db(tmp_path: Path, *, invalid_fk: bool = False) -> Path:
    path = tmp_path / "adg_indexed_test.sqlite"
    with sqlite3.connect(path) as conn:
        conn.executescript("""
            PRAGMA foreign_keys=OFF;
            CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO meta VALUES ('commit_sha', 'test');

            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                adg_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                layer TEXT NOT NULL,
                resolved_path TEXT NOT NULL
            );

            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER NOT NULL REFERENCES nodes(id),
                dst_id INTEGER NOT NULL REFERENCES nodes(id),
                relation_type TEXT NOT NULL,
                source_file TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                bucket TEXT NOT NULL,
                resolution_status TEXT NOT NULL,
                authority_status TEXT NOT NULL
            );

            CREATE TABLE violations (
                id INTEGER PRIMARY KEY,
                file_path TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                disposition TEXT NOT NULL
            );

            INSERT INTO nodes VALUES
                (1, 'ADG::Module::a', 'module', 'L1', 'agentic_core/a.py'),
                (2, 'ADG::Module::b', 'module', 'L2', 'agentic_core/b.py');
            """)
        dst_id = 999 if invalid_fk else 2
        conn.execute(
            "INSERT INTO edges VALUES "
            "(1, 1, ?, 'imports', 'agentic_core/a.py', 1, "
            "'static', 'VERIFIED_MODULE', 'AUTHORITATIVE')",
            (dst_id,),
        )
        conn.execute(
            "INSERT INTO violations VALUES " "(1, 'agentic_core/a.py', 1, 'test', 'HIGH', 'untriaged')"
        )
    return path


class TestSQLiteHardening:
    def test_installs_query_indexes_and_integrity_meta(self, tmp_path: Path) -> None:
        path = _make_db(tmp_path)

        with sqlite3.connect(path) as conn:
            report = harden_sqlite_connection(conn)

        assert report.quick_check == "ok"
        assert report.foreign_key_violation_count == 0
        assert report.application_id == 0x41444731
        assert report.user_version == 2
        assert report.indexes_created >= 6

        with sqlite3.connect(path) as conn:
            index_names = {
                row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
            }
            meta = dict(conn.execute("SELECT key, value FROM meta"))

            assert conn.execute("PRAGMA application_id").fetchone()[0] == 0x41444731
            assert conn.execute("PRAGMA user_version").fetchone()[0] == 2

        assert "idx_edges_src_relation" in index_names
        assert "idx_edges_dst_relation" in index_names
        assert "idx_edges_relation_source_line" in index_names
        assert "idx_nodes_path_entity" in index_names
        assert "idx_violations_disposition_severity_category_file" in index_names
        assert meta["sqlite_quick_check"] == "ok"
        assert meta["sqlite_foreign_key_violation_count"] == "0"
        assert meta["sqlite_optimizer"] == "pragma_optimize"
        assert meta["sqlite_hardening_contract"] == "adg-sqlite-v2"

    def test_query_planner_uses_dominant_composite_indexes(self, tmp_path: Path) -> None:
        path = _make_db(tmp_path)
        with sqlite3.connect(path) as conn:
            harden_sqlite_connection(conn)
            edge_plan = " ".join(
                str(row[3])
                for row in conn.execute(
                    "EXPLAIN QUERY PLAN " "SELECT id FROM edges WHERE src_id=? AND relation_type=?",
                    (1, "imports"),
                )
            )
            violation_plan = " ".join(
                str(row[3])
                for row in conn.execute(
                    "EXPLAIN QUERY PLAN "
                    "SELECT id FROM violations "
                    "WHERE disposition=? AND severity=? AND category=?",
                    ("untriaged", "HIGH", "test"),
                )
            )

        assert "idx_edges_src_relation" in edge_plan
        assert "idx_violations_disposition_severity_category_file" in violation_plan

    def test_idempotent_second_pass_creates_no_new_indexes(self, tmp_path: Path) -> None:
        path = _make_db(tmp_path)
        with sqlite3.connect(path) as conn:
            first = harden_sqlite_connection(conn)
            second = harden_sqlite_connection(conn)

        assert first.indexes_created > 0
        assert second.indexes_created == 0
        assert second.index_count == first.index_count

    def test_fk_violations_are_measured_without_default_migration_break(self, tmp_path: Path) -> None:
        path = _make_db(tmp_path, invalid_fk=True)

        with sqlite3.connect(path) as conn:
            report = harden_sqlite_connection(conn, strict_foreign_keys=False)
            stored = conn.execute(
                "SELECT value FROM meta WHERE key='sqlite_foreign_key_violation_count'"
            ).fetchone()[0]

        assert report.foreign_key_violation_count == 1
        assert stored == "1"

    def test_strict_fk_mode_fails_after_recording_evidence(self, tmp_path: Path) -> None:
        path = _make_db(tmp_path, invalid_fk=True)

        with sqlite3.connect(path) as conn:
            with pytest.raises(RuntimeError, match="foreign_key_check failed"):
                harden_sqlite_connection(conn, strict_foreign_keys=True)

        with sqlite3.connect(path) as conn:
            stored = conn.execute(
                "SELECT value FROM meta WHERE key='sqlite_foreign_key_violation_count'"
            ).fetchone()[0]
        assert stored == "1"

    def test_reduced_fixture_skips_incompatible_indexes(self, tmp_path: Path) -> None:
        path = tmp_path / "reduced.sqlite"
        with sqlite3.connect(path) as conn:
            conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
            conn.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY)")
            report = harden_sqlite_connection(conn)

        assert report.quick_check == "ok"
        assert report.indexes_created == 0


class TestMVConnection:
    def test_enables_foreign_keys_and_bounded_busy_timeout(self, tmp_path: Path) -> None:
        path = _make_db(tmp_path)
        conn = connect_sqlite_for_mv(path, timeout=2.5)
        try:
            assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
            assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == 2500
            assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
            assert conn.execute("PRAGMA cache_size").fetchone()[0] == -65536
            assert conn.execute("PRAGMA trusted_schema").fetchone()[0] == 0
        finally:
            conn.close()


class TestSQLiteSeal:
    def test_truncate_checkpoint_publishes_all_frames_to_main_database(self, tmp_path: Path) -> None:
        path = _make_db(tmp_path)
        conn = connect_sqlite_for_mv(path)
        try:
            conn.execute("INSERT INTO meta VALUES ('late_write', 'visible')")
            conn.commit()
            report = seal_sqlite_connection(conn)

            assert report.quick_check == "ok"
            assert report.wal_busy == 0
            assert report.journal_mode == "wal"
            wal_path = Path(f"{path}-wal")
            assert not wal_path.exists() or wal_path.stat().st_size == 0
        finally:
            conn.close()

        wal_path = Path(f"{path}-wal")
        assert not wal_path.exists() or wal_path.stat().st_size == 0
        with sqlite3.connect(path) as verify:
            meta = dict(verify.execute("SELECT key, value FROM meta"))
        assert meta["late_write"] == "visible"
        assert meta["sqlite_seal_contract"] == "wal-checkpointed-main-db-v1"

    def test_path_seal_handles_late_generator_writes(self, tmp_path: Path) -> None:
        path = _make_db(tmp_path)
        with connect_sqlite_for_mv(path) as conn:
            conn.execute("INSERT INTO meta VALUES ('post_enrichment', '1')")
            conn.commit()

        report = seal_sqlite_path(path)

        assert report.quick_check == "ok"
        assert report.wal_busy == 0
        with sqlite3.connect(path) as verify:
            assert verify.execute("SELECT value FROM meta WHERE key='post_enrichment'").fetchone()[0] == "1"


class _FakeCheckpointCursor:
    def fetchone(self) -> tuple[int, int, int]:
        return (0, 7, 7)


class _FakeCheckpointConnection:
    def __init__(self, path: str, calls: list[str]) -> None:
        self._path = path
        self._calls = calls

    def __enter__(self) -> _FakeCheckpointConnection:
        self._calls.append(self._path)
        return self

    def __exit__(self, *_args: Any) -> None:
        return None

    def execute(self, _sql: str) -> _FakeCheckpointCursor:
        return _FakeCheckpointCursor()


class TestWALCheckpointTargeting:
    def test_concrete_sqlite_file_is_checkpointed(self, tmp_path: Path, monkeypatch) -> None:
        path = tmp_path / "adg_indexed_one.sqlite"
        path.touch()
        calls: list[str] = []

        monkeypatch.setattr(
            file_utils.sqlite3,
            "connect",
            lambda target, timeout=5.0: _FakeCheckpointConnection(str(target), calls),
        )
        monkeypatch.setattr(file_utils.time, "sleep", lambda _seconds: None)

        file_utils._perform_wal_checkpoint(path)

        assert calls == [str(path.resolve())]

    def test_directory_targets_indexed_and_graph_databases(
        self,
        tmp_path: Path,
        monkeypatch,
    ) -> None:
        indexed = tmp_path / "adg_indexed_one.sqlite"
        graph = tmp_path / "adg_graph_one.sqlite"
        ignored = tmp_path / "other.sqlite"
        for path in (indexed, graph, ignored):
            path.touch()
        calls: list[str] = []

        monkeypatch.setattr(
            file_utils.sqlite3,
            "connect",
            lambda target, timeout=5.0: _FakeCheckpointConnection(str(target), calls),
        )
        monkeypatch.setattr(file_utils.time, "sleep", lambda _seconds: None)

        file_utils._perform_wal_checkpoint(tmp_path)

        assert calls == sorted([str(indexed.resolve()), str(graph.resolve())])
