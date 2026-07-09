from __future__ import annotations

import sqlite3

from ops_scripts.ci.check_w6_new_orphans_delta import _orphan_set


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            entity_type TEXT NOT NULL,
            layer TEXT NOT NULL,
            resolved_path TEXT
        );
        CREATE TABLE edges (
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL
        );
        """
    )
    return conn


def test_orphan_set_counts_symbol_imports_as_module_fan_in() -> None:
    conn = _conn()
    conn.executemany(
        "INSERT INTO nodes (id, entity_type, layer, resolved_path) VALUES (?, ?, ?, ?)",
        [
            (1, "module", "L_APP", "apps_rg/runtime/sections/live_binding.py"),
            (2, "symbol", "L_APP", "apps_rg/runtime/sections/live_binding.py"),
            (3, "module", "L_APP", "apps_rg/runtime/spine/consumer.py"),
        ],
    )
    conn.execute("INSERT INTO edges VALUES (3, 2, 'imports')")

    assert "apps_rg/runtime/sections/live_binding.py" not in _orphan_set(conn)


def test_orphan_set_ignores_same_file_symbol_edges() -> None:
    conn = _conn()
    conn.executemany(
        "INSERT INTO nodes (id, entity_type, layer, resolved_path) VALUES (?, ?, ?, ?)",
        [
            (1, "module", "L_APP", "apps_rg/runtime/sections/local_only.py"),
            (2, "symbol", "L_APP", "apps_rg/runtime/sections/local_only.py"),
        ],
    )
    conn.execute("INSERT INTO edges VALUES (1, 2, 'imports')")

    assert _orphan_set(conn) == {"apps_rg/runtime/sections/local_only.py": "L_APP"}


def test_orphan_set_keeps_modules_without_import_fan_in() -> None:
    conn = _conn()
    conn.execute(
        "INSERT INTO nodes (id, entity_type, layer, resolved_path) VALUES (?, ?, ?, ?)",
        (1, "module", "L_APP", "apps_rg/runtime/sections/unreferenced.py"),
    )

    assert _orphan_set(conn) == {"apps_rg/runtime/sections/unreferenced.py": "L_APP"}
