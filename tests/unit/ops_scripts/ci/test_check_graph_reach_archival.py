"""Tests for ops_scripts/ci/check_graph_reach_archival.py (W4)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from ops_scripts.ci import check_graph_reach_archival as mod


# ---- anchor helpers ----------------------------------------------------


def test_matches_anchor_basic_globs() -> None:
    patterns = [
        "tests/**/*.py",
        ".codex/governance/scripts/post_agent_*.py",
        "**/__init__.py",
    ]
    assert mod.matches_anchor("tests/unit/foo.py", patterns)
    assert mod.matches_anchor(".codex/governance/scripts/post_agent_bar.py", patterns)
    assert mod.matches_anchor("agentic_core/__init__.py", patterns)
    assert not mod.matches_anchor("agentic_core/foo.py", patterns)


def test_load_anchors_from_file(tmp_path: Path) -> None:
    yaml_src = (
        "version: 1\n"
        "anchors:\n"
        "  - pattern: 'a/**.py'\n"
        "    reason: test\n"
        "  - pattern: 'b/*.py'\n"
        "    reason: test\n"
    )
    p = tmp_path / "anchors.yaml"
    p.write_text(yaml_src, encoding="utf-8")
    assert mod.load_anchors(p) == ["a/**.py", "b/*.py"]


def test_load_anchors_missing_file(tmp_path: Path) -> None:
    assert mod.load_anchors(tmp_path / "absent.yaml") == []


def test_load_anchors_malformed(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("this: is: invalid: yaml: [unterminated", encoding="utf-8")
    assert mod.load_anchors(p) == []


def test_load_anchors_ignores_non_dict_entries(tmp_path: Path) -> None:
    p = tmp_path / "mixed.yaml"
    p.write_text(
        "anchors:\n"
        "  - pattern: 'ok/*.py'\n"
        "    reason: ok\n"
        "  - not-a-dict\n"
        "  - pattern: 42\n"  # non-string
        "    reason: bad\n",
        encoding="utf-8",
    )
    assert mod.load_anchors(p) == ["ok/*.py"]


# ---- ADG graph reachability --------------------------------------------


def _mk_snapshot(path: Path, nodes: list[dict], edges: list[dict]) -> None:
    conn = sqlite3.connect(str(path))
    conn.execute("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            adg_name TEXT,
            entity_type TEXT,
            layer TEXT,
            resolved_path TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT
        )
    """)
    for n in nodes:
        conn.execute(
            "INSERT INTO nodes (id, adg_name, entity_type, layer, resolved_path) VALUES (?, ?, ?, ?, ?)",
            (
                n["id"],
                n.get("adg_name", ""),
                n.get("entity_type", ""),
                n.get("layer", ""),
                n.get("resolved_path", ""),
            ),
        )
    for i, e in enumerate(edges):
        conn.execute(
            "INSERT INTO edges (id, src_id, dst_id, relation_type) VALUES (?, ?, ?, ?)",
            (i + 1, e["src"], e["dst"], e.get("rel", "imports")),
        )
    conn.commit()
    conn.close()


def test_find_archival_orphans_filters_anchors(tmp_path: Path) -> None:
    snap = tmp_path / "adg_indexed_test.sqlite"
    _mk_snapshot(
        snap,
        nodes=[
            {
                "id": 1,
                "entity_type": "module",
                "layer": "L0",
                "resolved_path": "agentic_core/L0_routing/boot.py",
            },
            {
                "id": 2,
                "entity_type": "module",
                "layer": "L2",
                "resolved_path": "agentic_core/L2_execution/reachable.py",
            },
            {
                "id": 3,
                "entity_type": "module",
                "layer": "L2",
                "resolved_path": "agentic_core/L2_execution/dead_module.py",
            },
            {
                "id": 4,
                "entity_type": "module",
                "layer": "L2",
                "resolved_path": "tests/unit/test_something.py",
            },
            {
                "id": 5,
                "entity_type": "module",
                "layer": "L2",
                "resolved_path": ".codex/governance/scripts/post_agent_something.py",
            },
        ],
        edges=[
            {"src": 1, "dst": 2},  # L0 -> L2 module (reachable)
        ],
    )
    conn = sqlite3.connect(str(snap))
    try:
        orphans = mod.find_archival_orphans(
            conn,
            anchor_patterns=[
                "tests/**/*.py",
                ".codex/governance/scripts/post_agent_*.py",
            ],
        )
    finally:
        conn.close()
    # Node 2 is reachable; 4 + 5 are anchored; only 3 remains.
    paths = [rp for _, rp, _ in orphans]
    assert paths == ["agentic_core/L2_execution/dead_module.py"]


def test_find_archival_orphans_without_l0_seeds(tmp_path: Path) -> None:
    snap = tmp_path / "adg_indexed_noseed.sqlite"
    _mk_snapshot(
        snap,
        nodes=[
            {"id": 1, "entity_type": "module", "layer": "L2", "resolved_path": "agentic_core/L2/foo.py"},
        ],
        edges=[],
    )
    conn = sqlite3.connect(str(snap))
    try:
        orphans = mod.find_archival_orphans(conn, anchor_patterns=[])
    finally:
        conn.close()
    # Without L0 seeds, nothing is reachable, but the gate short-circuits
    # to return empty list to avoid false alarms on a malformed snapshot.
    assert orphans == []


def test_orphan_in_anchor_pattern_is_excluded(tmp_path: Path) -> None:
    snap = tmp_path / "adg_indexed_anchor.sqlite"
    _mk_snapshot(
        snap,
        nodes=[
            {
                "id": 1,
                "entity_type": "module",
                "layer": "L0",
                "resolved_path": "agentic_core/L0_routing/boot.py",
            },
            {"id": 2, "entity_type": "module", "layer": "L2", "resolved_path": "tools/debug/_adhoc.py"},
        ],
        edges=[],
    )
    conn = sqlite3.connect(str(snap))
    try:
        orphans = mod.find_archival_orphans(conn, anchor_patterns=["tools/debug/*.py"])
    finally:
        conn.close()
    assert orphans == []


def test_non_production_layers_ignored(tmp_path: Path) -> None:
    snap = tmp_path / "adg_indexed_layer.sqlite"
    _mk_snapshot(
        snap,
        nodes=[
            {
                "id": 1,
                "entity_type": "module",
                "layer": "L0",
                "resolved_path": "agentic_core/L0_routing/boot.py",
            },
            {"id": 2, "entity_type": "module", "layer": "L_TOOLS", "resolved_path": "tools/foo.py"},
            {"id": 3, "entity_type": "module", "layer": "L_TEST", "resolved_path": "tests/foo.py"},
            {"id": 4, "entity_type": "module", "layer": "L_OPS", "resolved_path": "ops_scripts/foo.py"},
        ],
        edges=[],
    )
    conn = sqlite3.connect(str(snap))
    try:
        orphans = mod.find_archival_orphans(conn, anchor_patterns=[])
    finally:
        conn.close()
    # None of these layers are in _PRODUCTION_LAYERS -> filtered out.
    assert orphans == []
