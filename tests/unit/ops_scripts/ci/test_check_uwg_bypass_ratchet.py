import sqlite3
from pathlib import Path

from ops_scripts.ci.check_uwg_bypass_ratchet import UwgBypassRatchetGate


_EXISTING_WRITER = "ops_scripts/ci/check_uwg_bypass_ratchet.py"


def _gate() -> UwgBypassRatchetGate:
    return UwgBypassRatchetGate(snapshot=Path(__file__))


def _make_mv_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE mv_write_sovereignty_paths (
            snapshot_id TEXT,
            edge_id INTEGER,
            writer_file TEXT,
            writer_layer TEXT,
            write_symbol TEXT,
            write_line INTEGER,
            source_file TEXT,
            is_uwg_routed INTEGER,
            is_direct_infra_write INTEGER,
            severity TEXT
        );
        """
    )
    return conn


def _insert_mv_row(
    conn: sqlite3.Connection,
    *,
    writer_file: str = _EXISTING_WRITER,
    writer_layer: str = "L2",
    write_symbol: str = "path.write_text",
    write_line: int = 42,
    is_uwg_routed: int = 0,
) -> None:
    conn.execute(
        """
        INSERT INTO mv_write_sovereignty_paths (
            snapshot_id,
            edge_id,
            writer_file,
            writer_layer,
            write_symbol,
            write_line,
            source_file,
            is_uwg_routed,
            is_direct_infra_write,
            severity
        )
        VALUES ('snap', 1, ?, ?, ?, ?, ?, ?, 0, 'warning')
        """,
        (
            writer_file,
            writer_layer,
            write_symbol,
            write_line,
            writer_file,
            is_uwg_routed,
        ),
    )


def test_s2_uses_write_sovereignty_mv_and_drops_routed_rows() -> None:
    conn = _make_mv_conn()
    _insert_mv_row(conn, is_uwg_routed=1, write_symbol="_wg.write_text", write_line=10)
    _insert_mv_row(conn, is_uwg_routed=0, write_symbol="path.write_text", write_line=20)

    violations = _gate().run(conn)

    assert len(violations) == 1
    assert violations[0].subject == f"{_EXISTING_WRITER}:20"
    assert violations[0].extra["source_surface"] == "mv_write_sovereignty_paths"


def test_s2_mv_filters_unknown_layer_and_missing_source_file() -> None:
    conn = _make_mv_conn()
    _insert_mv_row(conn, writer_layer="L_UNKNOWN", write_line=10)
    _insert_mv_row(conn, writer_file="missing/path.py", writer_layer="L2", write_line=20)
    _insert_mv_row(conn, writer_layer="L2", write_line=30)

    violations = _gate().run(conn)

    assert len(violations) == 1
    assert violations[0].subject == f"{_EXISTING_WRITER}:30"


def test_s2_falls_back_to_raw_edges_when_mv_is_absent() -> None:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            resolved_path TEXT NOT NULL,
            layer TEXT NOT NULL
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT
        );
        INSERT INTO nodes VALUES (1, 'ops_scripts/ci/check_uwg_bypass_ratchet.py', 'L2');
        INSERT INTO nodes VALUES (2, 'tests/unit/example.py', 'L_TEST');
        INSERT INTO edges VALUES (1, 1, 'writes_to', 'ops_scripts/ci/check_uwg_bypass_ratchet.py', 44, 'open');
        INSERT INTO edges VALUES (2, 2, 'writes_to', 'tests/unit/example.py', 55, 'open');
        """
    )

    violations = _gate().run(conn)

    assert len(violations) == 1
    assert violations[0].subject == f"{_EXISTING_WRITER}:44"
