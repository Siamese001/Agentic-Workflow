from __future__ import annotations

import sqlite3
import time
from pathlib import Path


def _mk_sqlite(path: Path) -> None:
    conn = sqlite3.connect(str(path))
    conn.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE IF NOT EXISTS edges (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE IF NOT EXISTS violations (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT, value TEXT)")
    conn.commit()
    conn.close()


def test_latest_sqlite_ignores_invalid_timestamp_files(tmp_path, monkeypatch):
    from tools.adg.shared_modules.path_resolver import latest_sqlite

    adg_dir = tmp_path / "adg"
    adg_dir.mkdir()

    valid_old = adg_dir / "adg_indexed_04182026_2044.sqlite"
    valid_new = adg_dir / "adg_indexed_04192026_0657.sqlite"
    invalid_sentinel = adg_dir / "adg_indexed_99999999_9999.sqlite"

    _mk_sqlite(valid_old)
    time.sleep(0.01)
    _mk_sqlite(valid_new)
    time.sleep(0.01)
    _mk_sqlite(invalid_sentinel)

    monkeypatch.setenv("ADG_DIR", str(adg_dir))
    monkeypatch.setenv("ADG_ALLOW_EXTERNAL_DIR", "1")
    resolved = latest_sqlite()
    assert resolved is not None
    assert resolved.name == "adg_indexed_04192026_0657.sqlite"


def test_redis_ingest_finds_latest_valid_snapshot(tmp_path):
    from tools.adg.adg_redis_ingest import _find_latest_sqlite

    adg_dir = tmp_path / "adg"
    adg_dir.mkdir()

    valid = adg_dir / "adg_indexed_04192026_0657.sqlite"
    invalid = adg_dir / "adg_indexed_99999999_9999.sqlite"

    _mk_sqlite(valid)
    time.sleep(0.01)
    _mk_sqlite(invalid)

    resolved = _find_latest_sqlite(adg_dir)
    assert resolved.name == "adg_indexed_04192026_0657.sqlite"


def test_sqlite_backend_connect_uses_latest_valid_snapshot(tmp_path, monkeypatch):
    from tools.adg.core.sqlite_backend import SQLiteBackend

    adg_dir = tmp_path / "adg"
    adg_dir.mkdir()

    valid = adg_dir / "adg_indexed_04192026_0657.sqlite"
    invalid = adg_dir / "adg_indexed_99999999_9999.sqlite"

    _mk_sqlite(valid)
    time.sleep(0.01)
    _mk_sqlite(invalid)

    monkeypatch.setenv("ADG_DIR", str(adg_dir))
    monkeypatch.setenv("ADG_ALLOW_EXTERNAL_DIR", "1")
    backend = SQLiteBackend(use_graph_store=False)
    try:
        status = backend.get_status()
        assert status["timestamp"] == "04192026_0657"
    finally:
        backend.close()
