#!/usr/bin/env python3
"""Gate C5 — unresolved callsite ratchet (plan W4.5).

Counts ``resolves_callsite`` edges where the target side is NULL
(i.e. the static analyzer could not resolve the callee). A growing
population of unresolved callsites erodes dependency-analysis
precision and masks architectural drift.

Tier: R (ratchet).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from tqdm import tqdm

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


class UnresolvedCallsitesGate(WiringGate):
    gate_id = "C5_unresolved_callsites_ratchet"
    tier = "R"
    baseline_filename = "wiring_unresolved_callsites_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        query = """
            SELECT
                COALESCE(src.resolved_path, '<unknown>') AS caller_path,
                COALESCE(src.layer, 'UNKNOWN')          AS caller_layer,
                e.symbol                                AS call_symbol,
                e.line_no                               AS line_no
            FROM edges e
            LEFT JOIN nodes src ON src.id = e.src_id
            WHERE e.relation_type = 'resolves_callsite'
              AND (e.dst_id IS NULL OR e.dst_id = 0)
        """
        rows = list(conn.execute(query))
        violations: list[Violation] = []
        for caller_path, caller_layer, call_symbol, line_no in tqdm(
            rows, desc="C5_unresolved_calls", unit="edge"
        ):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{caller_path}:{line_no}",
                    rule="callsite_unresolved",
                    detail=f"{caller_layer}: unresolved call to {call_symbol}",
                    extra={
                        "caller_path": caller_path,
                        "caller_layer": caller_layer,
                        "call_symbol": call_symbol,
                        "line_no": line_no,
                    },
                )
            )
        return violations


def main() -> int:
    gate = UnresolvedCallsitesGate()
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
