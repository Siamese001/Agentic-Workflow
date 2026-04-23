#!/usr/bin/env python3
"""Gate G_REACH_ARCHIVAL — subset of G_REACH orphans that are real cleanup candidates.

Wraps ``check_graph_reach.py`` logic but filters the orphan set through
``config/wiring_dynamic_dispatch_anchors.yaml`` to separate:

    * dynamic  — orphans whose path matches a dynamic-dispatch anchor
                 (plugin registries, CLI scripts, hooks, entry points).
                 These are legitimate "indirect use" targets, NOT dead code.
    * archival — orphans that do NOT match any dynamic anchor.
                 These are the real deletion / archival candidates.

Tier
    R (ratchet) with monotone auto-tighten + R->B auto-promotion enabled
    via W1 harness behaviour. Separate baseline from G_REACH so a single
    actionable metric drives cleanup.
"""

from __future__ import annotations

import fnmatch
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


GATE_ID = "G_REACH_ARCHIVAL_orphans"
ANCHORS_FILE = REPO_ROOT / "config" / "wiring_dynamic_dispatch_anchors.yaml"
_PRODUCTION_LAYERS = ("L1", "L2", "L3", "L4", "L5", "L_APP", "L_PG")


def load_anchors(path: Path | None = None) -> list[str]:
    """Return the list of glob patterns from the anchors YAML."""
    src = path or ANCHORS_FILE
    if not src.exists() or yaml is None:
        return []
    try:
        data = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    if not isinstance(data, dict):
        return []
    anchors = data.get("anchors", []) or []
    patterns: list[str] = []
    for entry in anchors:
        if isinstance(entry, dict):
            pat = entry.get("pattern")
            if isinstance(pat, str) and pat:
                patterns.append(pat)
    return patterns


def matches_anchor(path: str, patterns: list[str]) -> bool:
    """Return True if path matches any glob in patterns (fnmatch semantics)."""
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def _build_import_digraph(conn: sqlite3.Connection) -> Any:
    import networkx as nx

    g = nx.DiGraph()
    for node_id, layer, entity_type, resolved_path, adg_name in conn.execute(
        "SELECT id, layer, entity_type, resolved_path, adg_name FROM nodes"
    ):
        g.add_node(
            node_id,
            layer=layer or "",
            entity_type=entity_type or "",
            resolved_path=resolved_path or "",
            adg_name=adg_name or "",
        )
    for src, tgt in conn.execute(
        "SELECT src_id, dst_id FROM edges WHERE relation_type='imports'"
    ):
        if src in g and tgt in g:
            g.add_edge(src, tgt)
    return g


def find_archival_orphans(
    conn: sqlite3.Connection, anchor_patterns: list[str]
) -> list[tuple[int, str, str]]:
    """Return (node_id, resolved_path, layer) for each archival orphan."""
    try:
        import networkx as nx
    except ImportError:
        return []
    g = _build_import_digraph(conn)
    l0_seeds = [
        n for n, d in g.nodes(data=True)
        if d.get("layer") == "L0" and d.get("entity_type") == "module"
    ]
    if not l0_seeds:
        return []
    reachable: set = set(l0_seeds)
    for seed in l0_seeds:
        reachable.update(nx.descendants(g, seed))
    out: list[tuple[int, str, str]] = []
    for node_id, data in g.nodes(data=True):
        if data.get("entity_type") != "module":
            continue
        if data.get("layer") not in _PRODUCTION_LAYERS:
            continue
        if node_id in reachable:
            continue
        rp = data.get("resolved_path") or ""
        if matches_anchor(rp, anchor_patterns):
            continue
        out.append((node_id, rp, data.get("layer", "")))
    return out


class GraphReachArchivalGate(WiringGate):
    gate_id = GATE_ID
    tier = "R"
    baseline_filename = "wiring_graph_reach_archival_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        anchors = load_anchors()
        orphans = find_archival_orphans(conn, anchors)
        return [
            Violation(
                gate_id=GATE_ID,
                tier="R",
                subject=rp or f"node#{node_id}",
                rule="archival_orphan",
                detail=(
                    f"Module in layer {layer} is L0-unreachable via imports "
                    "and does not match any dynamic-dispatch anchor; "
                    "real archival/deletion candidate"
                ),
                extra={"layer": layer, "node_id": node_id},
            )
            for node_id, rp, layer in orphans
        ]


def main(argv: list[str] | None = None) -> int:  # noqa: ARG001
    result = GraphReachArchivalGate().execute()
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
