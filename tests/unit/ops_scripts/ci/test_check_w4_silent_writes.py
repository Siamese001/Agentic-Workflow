import sqlite3

from ops_scripts.ci.check_w4_silent_writes import SilentWritesGate


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            layer TEXT NOT NULL,
            identity_kind TEXT NOT NULL,
            confidence TEXT NOT NULL,
            resolved_path TEXT NOT NULL
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL
        );
        """
    )
    return conn


def _node(conn: sqlite3.Connection, node_id: int, path: str, layer: str = "L2") -> None:
    conn.execute(
        """
        INSERT INTO nodes (
            id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path
        )
        VALUES (?, ?, 'module', ?, 'module', 'high', ?)
        """,
        (node_id, f"ADG::Module::{path}", layer, path),
    )


def _edge(conn: sqlite3.Connection, edge_id: int, src_id: int, dst_id: int, relation: str) -> None:
    conn.execute(
        "INSERT INTO edges (id, src_id, dst_id, relation_type) VALUES (?, ?, ?, ?)",
        (edge_id, src_id, dst_id, relation),
    )


def test_c3_accepts_side_effect_edges_targeting_writer_module() -> None:
    conn = _make_conn()
    _node(conn, 1, "agentic_core/L2_execution/example_writer.py")
    _node(conn, 2, "state/store.json", "L4")
    _node(conn, 3, "", "L2")
    _edge(conn, 1, 1, 2, "writes_to")
    _edge(conn, 2, 3, 1, "emits_side_effect")

    assert SilentWritesGate().run(conn) == []


def test_c3_still_flags_writes_without_same_surface_side_effect() -> None:
    conn = _make_conn()
    _node(conn, 1, "agentic_core/L2_execution/silent_writer.py")
    _node(conn, 2, "state/store.json", "L4")
    _node(conn, 3, "agentic_core/L2_execution/other_writer.py")
    _edge(conn, 1, 1, 2, "writes_to")
    _edge(conn, 2, 3, 2, "emits_side_effect")

    violations = SilentWritesGate().run(conn)

    assert len(violations) == 1
    assert violations[0].subject == "agentic_core/L2_execution/silent_writer.py"
