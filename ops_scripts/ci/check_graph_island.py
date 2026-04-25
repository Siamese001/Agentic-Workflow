#!/usr/bin/env python3
"""Gate G-ISLAND: non-giant connected components ratchet (H2).

Graph-native check: the ADG should be substantially one giant component under
undirected projection of ``imports`` edges. Small disconnected components
("islands") of 2+ modules represent suspicious wiring: a subsystem that talks
to itself but nothing outside.

Rationale
    C0 was effectively an island. So are shadow SSOTs and accidentally-forked
    utilities. Counting non-giant components with more than 1 node is a cheap,
    high-signal structural invariant.

Algorithm
    1. Build nx.Graph (undirected) from edges WHERE relation_type='imports'
    2. components = nx.connected_components
    3. giant = max by size
    4. islands = [c for c in components if c is not giant and |c| > 1]
    5. Ratchet on sum(|c| for c in islands); fail if > baseline

Tier: R (P1 RATCHET)
Band: P1
Source: ADG SQLite + nx.Graph projection
"""

from __future__ import annotations

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

GATE_ID = "G_ISLAND_connected_components"


def _build_undirected(conn: sqlite3.Connection):
    import networkx as nx

    g = nx.Graph()
    for node_id, layer, resolved_path, adg_name in conn.execute(
        "SELECT id, layer, resolved_path, adg_name FROM nodes WHERE entity_type='module'"
    ):
        g.add_node(
            node_id,
            layer=layer or "",
            resolved_path=resolved_path or "",
            adg_name=adg_name or "",
        )
    for src, dst in conn.execute("SELECT src_id, dst_id FROM edges WHERE relation_type='imports'"):
        if src in g and dst in g:
            g.add_edge(src, dst)
    return g


class GraphIslandGate(WiringGate):
    gate_id = GATE_ID
    tier = "R"
    baseline_filename = "wiring_graph_island_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        try:
            import networkx as nx
        except ImportError:
            print(f"[{GATE_ID}] SKIP networkx unavailable", file=sys.stderr)
            return []

        g = _build_undirected(conn)
        components = list(nx.connected_components(g))
        if not components:
            return []

        giant = max(components, key=len)
        islands = [c for c in components if c is not giant and len(c) > 1]

        violations: list[Violation] = []
        for idx, comp in enumerate(sorted(islands, key=len, reverse=True), start=1):
            members = sorted(
                (g.nodes[n].get("resolved_path") or g.nodes[n].get("adg_name") or f"node#{n}") for n in comp
            )
            subject = members[0]
            violations.append(
                Violation(
                    gate_id=GATE_ID,
                    tier="R",
                    subject=subject,
                    rule="non_giant_component",
                    detail=(
                        f"Connected component #{idx} has {len(comp)} modules "
                        f"disconnected from the giant component. Representative: {subject}."
                    ),
                    severity="fail",
                    extra={
                        "component_size": len(comp),
                        "members": members[:10],
                        "members_truncated": len(members) > 10,
                    },
                )
            )
        return violations


def main() -> int:
    gate = GraphIslandGate()
    result = gate.execute()
    return cli_exit(result)


if __name__ == "__main__":
    raise SystemExit(main())
