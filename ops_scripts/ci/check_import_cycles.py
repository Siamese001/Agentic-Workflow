#!/usr/bin/env python3
"""Gate A6 — import cycle detector (plan wiring-ci / ADR-034).

Builds a **module-level** directed graph from ADG ``imports`` edges (aggregating
symbol targets to ``resolved_path``), then runs Tarjan SCC. Any strongly
connected component with size > 1, plus any explicit self-edge, is a
violation.

Tier: **R** (ratchet) — CI fails only when the active SCC count **exceeds**
the sealed baseline in ``ops_scripts/ci/baselines/wiring_import_cycle_ratchet.json``.

ADR-034 originally labeled A6 as tier **B** (absolute zero). The canonical
script was missing from the tree for an extended period (``run_contract_gates``
invoked a nonexistent path). Re-introducing the gate as a **ratchet** matches
the wiring-CI plane’s operational pattern for accumulated graph debt (A1, A3,
L1, …): freeze the current SCC inventory, then burn down without regressions.

Operators: refresh baseline after an audited cycle-removal pass:

    python ops_scripts/ci/check_import_cycles.py --seed

References:
    ADR-034 docs/architecture/adr/ADR-034-wiring-ci-gate-plane-and-uwg-allowlist.md
"""

from __future__ import annotations

__adg_consumer_mode__ = "inventory"

import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
    connect_snapshot,
    latest_snapshot,
)

PRODUCTION_ROOTS = (
    "agentic_core/",
    "apps_eval/",
    "apps_exec/",
    "apps_lic/",
    "apps_research/",
    "apps_rg/",
    "apps_shared/",
    "apps_underwriting_ai/",
    "system_learning/",
    "infrastructure/",
)
EXCLUDE_PREFIXES = (
    "tests/",
    "tools/archive/",
    "tools/bench/",
    "tools/debug/",
    "tools/diag/",
    "archives/",
)

_IMPORT_EDGE_SQL = """
    SELECT DISTINCT src.resolved_path AS src_path, dst.resolved_path AS dst_path
    FROM edges e
    JOIN nodes dst ON dst.id = e.dst_id
    JOIN nodes src ON src.id = e.src_id
    WHERE e.relation_type = 'imports'
      AND src.resolved_path IS NOT NULL
      AND dst.resolved_path IS NOT NULL
"""


def _in_production_scope(path: str) -> bool:
    if not path.startswith(PRODUCTION_ROOTS):
        return False
    return not any(path.startswith(p) for p in EXCLUDE_PREFIXES)


def _tarjan_sccs(adj: DefaultDict[str, set[str]]) -> list[list[str]]:
    """Return list of SCCs (each a list of vertices). Order is Tarjan order."""
    index = 0
    stack: list[str] = []
    onstack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    sccs: list[list[str]] = []

    def strongconnect(v: str) -> None:
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        onstack.add(v)
        for w in adj.get(v, ()):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in onstack:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                onstack.discard(w)
                comp.append(w)
                if w == v:
                    break
            sccs.append(comp)

    for v in adj:
        if v not in indices:
            strongconnect(v)
    return sccs


class ImportCycleGate(WiringGate):
    gate_id = "A6_import_cycle"
    tier = "R"
    baseline_filename = "wiring_import_cycle_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        raw_edges: set[tuple[str, str]] = set()
        for src_path, dst_path in conn.execute(_IMPORT_EDGE_SQL):
            if not _in_production_scope(src_path) or not _in_production_scope(dst_path):
                continue
            raw_edges.add((src_path, dst_path))

        violations: list[Violation] = []

        for src_path, dst_path in sorted(raw_edges):
            if src_path == dst_path:
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=src_path,
                        rule="import_self_cycle",
                        detail="module imports itself on the module-level imports projection",
                        extra={"cycle": [src_path]},
                    )
                )

        adj: DefaultDict[str, set[str]] = defaultdict(set)
        edge_nodes: set[str] = set()
        for src_path, dst_path in raw_edges:
            if src_path == dst_path:
                continue
            adj[src_path].add(dst_path)
            edge_nodes.add(src_path)
            edge_nodes.add(dst_path)
        for v in edge_nodes:
            _ = adj[v]  # ensure Tarjan visits in-only vertices

        for comp in _tarjan_sccs(adj):
            if len(comp) <= 1:
                continue
            ordered = sorted(comp)
            canon = ordered[0]
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=canon,
                    rule="import_scc",
                    detail=f"SCC size={len(comp)} members={ordered}",
                    extra={"cycle": ordered, "scc_size": len(comp)},
                )
            )

        violations.sort(key=lambda v: (v.subject, v.rule, v.detail))
        return violations


def main() -> int:
    gate = ImportCycleGate()
    if "--seed" in sys.argv:
        conn = connect_snapshot(latest_snapshot())
        try:
            raw = gate.run(conn)
        finally:
            conn.close()
        gate.seed_baseline(len(raw))
        print(f"[{gate.gate_id}] baseline seeded: count={len(raw)}")
        return 0
    result = gate.execute()
    if result.baseline_count is not None:
        print(
            f"[{gate.gate_id}] current={len(result.violations)} "
            f"baseline={result.baseline_count}"
        )
    return cli_exit(result)


if __name__ == "__main__":
    raise SystemExit(main())
