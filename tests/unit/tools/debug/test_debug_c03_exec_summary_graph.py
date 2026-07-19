from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tools.governance_legacy.debug_c03_exec_summary_graph import (
    _open_debug_connection,
)


def test_debug_graph_reader_uses_query_only_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "graph.sqlite"
    seed = sqlite3.connect(db_path)
    try:
        seed.execute("CREATE TABLE graph_nodes(node_id TEXT PRIMARY KEY)")
        seed.commit()
    finally:
        seed.close()

    conn = _open_debug_connection(db_path=db_path)
    try:
        assert conn.execute("PRAGMA query_only").fetchone()[0] == 1
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            conn.execute("INSERT INTO graph_nodes(node_id) VALUES ('forbidden')")
    finally:
        conn.close()

    verify = sqlite3.connect(db_path)
    try:
        assert verify.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0] == 0
    finally:
        verify.close()
