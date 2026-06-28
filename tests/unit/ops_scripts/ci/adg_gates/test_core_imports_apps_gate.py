from __future__ import annotations

import sqlite3
from pathlib import Path

from ops_scripts.ci.adg_gates.gate_p0_core_imports_apps import CoreImportsAppsGate
from ops_scripts.ci.adg_gates.unified_registry import get_spec


def _create_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "adg.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE meta (key TEXT, value TEXT)")
    conn.execute("INSERT INTO meta VALUES ('commit_sha', 'test-snapshot')")
    conn.execute(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            entity_type TEXT,
            layer TEXT,
            identity_kind TEXT,
            resolved_path TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT
        )
        """
    )
    conn.commit()
    conn.close()
    return db_path


def _node(conn: sqlite3.Connection, node_id: int, path: str, layer: str) -> None:
    conn.execute(
        "INSERT INTO nodes (id, adg_name, entity_type, layer, identity_kind, resolved_path) "
        "VALUES (?, ?, 'module', ?, 'repo_module', ?)",
        (node_id, f"ADG::Module::{path}", layer, path),
    )


def _edge(conn: sqlite3.Connection, src_id: int, dst_id: int, source_file: str, line_no: int) -> None:
    conn.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, source_file, line_no, symbol) "
        "VALUES (?, ?, 'imports', ?, ?, 'apps_demo')",
        (src_id, dst_id, source_file, line_no),
    )


def test_core_imports_apps_gate_blocks_on_fallback_query(tmp_path: Path) -> None:
    db_path = _create_db(tmp_path)
    conn = sqlite3.connect(str(db_path))
    _node(conn, 1, "agentic_core/L0_routing/gates/app_gate.py", "L0")
    _node(conn, 2, "apps_demo/runtime/binding.py", "L_APP")
    _edge(conn, 1, 2, "agentic_core/L0_routing/gates/app_gate.py", 18)
    conn.commit()
    conn.close()

    result = CoreImportsAppsGate(sqlite_path=db_path).run(emit_artifacts=False)

    assert result.status == "blocked"
    assert result.summary["total_violations"] == 1
    assert result.summary["by_app"] == {"apps_demo": 1}
    assert result.violations[0].first_illegal_hop == "agentic_core->apps_demo"


def test_core_imports_apps_gate_passes_for_app_to_core_import(tmp_path: Path) -> None:
    db_path = _create_db(tmp_path)
    conn = sqlite3.connect(str(db_path))
    _node(conn, 1, "apps_demo/runtime/binding.py", "L_APP")
    _node(conn, 2, "agentic_core/runtime/contracts.py", "L2")
    _edge(conn, 1, 2, "apps_demo/runtime/binding.py", 7)
    conn.commit()
    conn.close()

    result = CoreImportsAppsGate(sqlite_path=db_path).run(emit_artifacts=False)

    assert result.status == "passed"
    assert result.violations == []


def test_core_imports_apps_gate_is_registered_as_p0_block() -> None:
    spec = get_spec("13_core_imports_apps")

    assert spec is not None
    assert spec.band.value == "P0"
    assert spec.enforcement.value == "block"
    assert spec.gate_class == "CoreImportsAppsGate"
