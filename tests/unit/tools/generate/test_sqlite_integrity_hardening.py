"""Regression tests for ADG SQLite referential-integrity hardening."""

from __future__ import annotations

import sqlite3

import pytest

from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv
from tools.generate.validation.integrity import _check_sqlite_integrity, _connect_sqlite


def _create_required_schema(path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY
            );
            CREATE TABLE edges (
                id INTEGER PRIMARY KEY,
                src_id INTEGER NOT NULL REFERENCES nodes(id),
                dst_id INTEGER NOT NULL REFERENCES nodes(id)
            );
            CREATE TABLE violations (
                id INTEGER PRIMARY KEY,
                edge_id INTEGER REFERENCES edges(id)
            );
            CREATE TABLE meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


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
        conn.execute("INSERT INTO edges(id, src_id, dst_id) VALUES (1, 100, 200)")
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
        conn.executemany("INSERT INTO nodes(id) VALUES (?)", [(1,), (2,)])
        conn.execute("INSERT INTO edges(id, src_id, dst_id) VALUES (1, 1, 2)")
        conn.execute("INSERT INTO violations(id, edge_id) VALUES (1, 1)")
        conn.commit()
    finally:
        conn.close()

    _check_sqlite_integrity(sqlite_path)
