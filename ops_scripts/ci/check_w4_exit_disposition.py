#!/usr/bin/env python3
"""Gate I1 — L5↔L6 exit-disposition parity (plan W4.6).

Reads ``mv_exit_disposition_coverage`` — each row with ``gap_flag=1``
or ``is_terminal_covered=0`` is a terminal node without a recorded
exit disposition (pass/fail/abort/retry), breaking the L5→L6 audit
trail.

Tier: R (ratchet).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


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


class ExitDispositionGate(WiringGate):
    gate_id = "I1_exit_disposition_ratchet"
    tier = "R"
    baseline_filename = "wiring_exit_disposition_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        rows = list(
            conn.execute(
                """
                SELECT file, layer, outgoing_terminal_count, is_terminal_covered, gap_type
                FROM mv_exit_disposition_coverage
                WHERE is_terminal_covered = 0
                """
            )
        )
        violations: list[Violation] = []
        for file_path, layer, out_count, covered, gap_type in tqdm(
            rows, desc="I1_exit_disposition", unit="node"
        ):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=file_path,
                    rule="exit_disposition_missing",
                    detail=f"{layer}: {gap_type}; terminal_out={out_count}",
                    extra={
                        "file": file_path,
                        "layer": layer,
                        "outgoing_terminal_count": out_count,
                        "is_terminal_covered": covered,
                        "gap_type": gap_type,
                    },
                )
            )
        return violations


def main() -> int:
    gate = ExitDispositionGate()
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
