#!/usr/bin/env python3
"""Gate G-REACH: L0-reachability of production modules (H2).

Graph-native check: every module in a production layer
(L1/L2/L3/L4/L5/L_APP/L_PG) MUST be reachable via ``imports`` edges from at
least one L0 entry node.

Rationale
    The C0 Context Engine orphan class (plan c0-context-engine-wiring-fix-9e42a1)
    is exactly a "module exists, tests import it, but no live L0 runtime path
    imports it". Edge-shape gates (SC-5, AP-14) miss this because they require
    SOME edge to fire. Graph reachability is an absence-of-good-edge check and
    serves as a 2ND INDEPENDENT SIGNAL beside J1 and G2.

Tier
    R (P0 RATCHET) — initial mode. Baseline auto-seeds on first run. New
    orphans fail the gate. Flip to BLOCK after the C0 wiring fix retires the
    known orphan cluster.

Band
    P0 (per unified_registry.py)

Source
    ADG SQLite ``nodes`` + ``edges`` tables; nx.DiGraph built in-memory.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

GATE_ID = "G_REACH_l0_reachability"

_PRODUCTION_LAYERS = ("L1", "L2", "L3", "L4", "L5", "L_APP", "L_PG")


def _source_file_exists(resolved_path: str) -> bool:
    return (REPO_ROOT / resolved_path).is_file()


def _build_import_digraph(conn: sqlite3.Connection):
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
    for src, tgt in conn.execute("SELECT src_id, dst_id FROM edges WHERE relation_type='imports'"):
        if src in g and tgt in g:
            g.add_edge(src, tgt)
    return g


class GraphReachGate(WiringGate):
    gate_id = GATE_ID
    tier = "R"
    baseline_filename = "wiring_graph_reach_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        try:
            import networkx as nx
        except ImportError:
            print(f"[{GATE_ID}] SKIP networkx unavailable", file=sys.stderr)
            return []

        g = _build_import_digraph(conn)

        l0_seeds = [
            n for n, d in g.nodes(data=True) if d.get("layer") == "L0" and d.get("entity_type") == "module"
        ]
        if not l0_seeds:
            print(
                f"[{GATE_ID}] WARN no L0 module seeds found in snapshot",
                file=sys.stderr,
            )
            return []

        reachable: set = set(l0_seeds)
        for seed in l0_seeds:
            reachable.update(nx.descendants(g, seed))

        violations: list[Violation] = []
        for node_id, data in g.nodes(data=True):
            if data.get("entity_type") != "module":
                continue
            if data.get("layer") not in _PRODUCTION_LAYERS:
                continue
            path = data.get("resolved_path") or data.get("adg_name") or f"node#{node_id}"
            if data.get("resolved_path") and not _source_file_exists(data["resolved_path"]):
                continue
            if node_id in reachable:
                continue
            violations.append(
                Violation(
                    gate_id=GATE_ID,
                    tier="R",
                    subject=path,
                    rule="l0_reachability",
                    detail=(
                        f"Module in layer {data.get('layer')} is not reachable "
                        "via 'imports' edges from any L0 entry"
                    ),
                    severity="fail",
                    extra={
                        "layer": data.get("layer"),
                        "node_id": node_id,
                        "l0_seed_count": len(l0_seeds),
                    },
                )
            )
        return violations


def main() -> int:
    gate = GraphReachGate()
    result = gate.execute()
    return cli_exit(result)


if __name__ == "__main__":
    raise SystemExit(main())
