"""Regression tests for ADG SQLite referential-integrity hardening."""

from __future__ import annotations

import sqlite3

import pytest

from agentic_core.adg.artifact.sqlite_schema import DDL
from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv
from tools.generate.validation.integrity import _check_sqlite_integrity, _connect_sqlite


def _create_required_schema(path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(DDL)
        conn.commit()
    finally:
        conn.close()


def _insert_node(conn: sqlite3.Connection, node_id: int) -> None:
    conn.execute(
        """
        INSERT INTO nodes(
            id, adg_name, entity_type, layer, identity_kind,
            confidence, resolved_path
        ) VALUES (?, ?, 'module', 'L2', 'internal_module', 'high', ?)
        """,
        (node_id, f"node_{node_id}", f"node_{node_id}.py"),
    )

def test_validation_connection_enables_foreign_keys(tmp_path):
    sqlite_path = tmp_path / "adg.sqlite"
    _create_required_schema(sqlite_path)

    conn = _connect_sqlite(sqlite_path)
    try:
        assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
    finally:
        conn.close()


def test_materialized_view_connection_enables_foreign_keys(tmp_path):
    sqlite_path = tmp_path / "adg.sqlite"
    _create_required_schema(sqlite_path)

    conn = connect_sqlite_for_mv(sqlite_path)
    try:
        assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
    finally:
        conn.close()


def test_integrity_check_rejects_orphaned_edges(tmp_path):
    sqlite_path = tmp_path / "adg.sqlite"
    _create_required_schema(sqlite_path)

    # Simulate a legacy or externally-mutated candidate produced without FK
    # enforcement. Certification must still discover and reject the orphan.
    conn = sqlite3.connect(sqlite_path)
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        conn.execute(
            """
            INSERT INTO edges(
                id, src_id, dst_id, relation_type, edge_kind,
                source_file, line_no
            ) VALUES (1, 100, 200, 'imports', 'static', 'orphan.py', 1)
            """
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(SystemExit) as exc_info:
        _check_sqlite_integrity(sqlite_path)

    assert exc_info.value.code == 1


def test_integrity_check_accepts_referentially_sound_database(tmp_path):
    sqlite_path = tmp_path / "adg.sqlite"
    _create_required_schema(sqlite_path)

    conn = sqlite3.connect(sqlite_path)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        _insert_node(conn, 1)
        _insert_node(conn, 2)
        conn.execute(
            """
            INSERT INTO edges(
                id, src_id, dst_id, relation_type, edge_kind,
                source_file, line_no
            ) VALUES (1, 1, 2, 'imports', 'static', 'sound.py', 1)
            """
        )
        conn.execute(
            "INSERT INTO violations(id, edge_id, category) "
            "VALUES (1, 1, 'test')"
        )
        conn.commit()
    finally:
        conn.close()

    _check_sqlite_integrity(sqlite_path)
