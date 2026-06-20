#!/usr/bin/env python3
"""Gate S4 — unused-import ratchet (plan W4.4).

Counts `unused_import` edges (edge_kind='dead_import') originating from
production modules. Dead imports inflate load time, hide refactor risk,
and silently document intent that no longer matches behavior.

Tier: R (ratchet).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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

EXCLUDE_LAYERS = ("L_TEST", "L_TOOLS")


class UnusedImportsRatchetGate(WiringGate):
    gate_id = "S4_unused_imports_ratchet"
    tier = "R"
    baseline_filename = "wiring_unused_imports_ratchet.json"

    def run(self, conn) -> list[Violation]:
        rows = conn.execute(
            """
            SELECT e.source_file, e.line_no, src.layer, e.symbol
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            WHERE e.relation_type = 'unused_import'
            """
        ).fetchall()

        violations: list[Violation] = []
        for source_file, line_no, layer, symbol in rows:
            if layer in EXCLUDE_LAYERS:
                continue
            loc = f"{source_file}:{line_no}" if source_file else "<unknown>:?"
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=loc,
                    rule="unused_import",
                    detail=f"layer={layer}; symbol={symbol}",
                    extra={"layer": layer, "symbol": symbol},
                )
            )
        return violations


def main() -> int:
    gate = UnusedImportsRatchetGate()
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
