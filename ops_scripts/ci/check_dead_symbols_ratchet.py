#!/usr/bin/env python3
"""Gate A3 — dead public symbol ratchet (plan W2.3).

Counts public symbols (not underscore-prefixed) in *used* production
modules (module fan-in > 0) that themselves have zero fan-in. High
signal for "exported but unused" API surface — a common driver of
maintenance drag and refactor regressions.

Tier: R (ratchet).

Scope:
    * entity_type = 'symbol'
    * resolved_path under PRODUCTION_ROOTS (not tests/archive/tools)
    * adg_name tail is a plain identifier that does NOT start with '_'
    * enclosing module fan-in > 0 (we don't flag symbols in an already-
      orphan module — gate A1 owns that)
    * symbol itself fan-in (on 'imports') == 0

Baseline seeded on first run. CI fails only when count > baseline.

Seed:
    python ops_scripts/ci/check_dead_symbols_ratchet.py --seed
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sys
from pathlib import Path

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


class DeadSymbolRatchetGate(WiringGate):
    gate_id = "A3_dead_public_symbol_ratchet"
    tier = "R"
    baseline_filename = "wiring_dead_symbol_ratchet.json"

    def run(self, conn) -> list[Violation]:
        # Pass 1: module fan-in totals for production modules.
        mod_fanin: dict[str, int] = {
            row[0]: row[1]
            for row in conn.execute(
                """
                SELECT dst.resolved_path, COUNT(*) AS n
                FROM edges e
                JOIN nodes dst ON dst.id = e.dst_id
                JOIN nodes src ON src.id = e.src_id
                WHERE e.relation_type = 'imports'
                  AND dst.resolved_path IS NOT NULL
                  AND src.resolved_path != dst.resolved_path
                GROUP BY dst.resolved_path
                """
            )
        }

        # Pass 2: set of symbol node ids that have ≥1 'imports' caller.
        imported_symbol_ids: set[int] = {
            row[0]
            for row in conn.execute("SELECT DISTINCT dst_id FROM edges WHERE relation_type = 'imports'")
        }

        # Pass 3: enumerate public symbols and filter.
        rows = conn.execute(
            """
            SELECT id, resolved_path, adg_name
            FROM nodes
            WHERE entity_type = 'symbol'
              AND resolved_path IS NOT NULL
            """
        ).fetchall()

        violations: list[Violation] = []
        for sym_id, path, adg_name in rows:
            if not path.startswith(PRODUCTION_ROOTS):
                continue
            if any(path.startswith(p) for p in EXCLUDE_PREFIXES):
                continue
            if mod_fanin.get(path, 0) == 0:
                continue  # A1 owns orphan modules
            short = adg_name.rsplit(".", 1)[-1] if adg_name else ""
            if not short or short.startswith("_") or short == "*":
                continue
            if sym_id in imported_symbol_ids:
                continue
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{path}::{short}",
                    rule="public_symbol_zero_fanin",
                    detail=f"public symbol never imported; module fan-in={mod_fanin.get(path, 0)}",
                    extra={"symbol": short, "module": path},
                )
            )
        return violations


def main() -> int:
    gate = DeadSymbolRatchetGate()
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
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
