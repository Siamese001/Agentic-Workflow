#!/usr/bin/env python3
"""Gate M — untrusted-text-to-action taint (plan W5.1).

Reads ``mv_actionable_surface_without_schema`` — any actionable edge
(tool call, write, provider invocation) whose source accepts untrusted
text and has NO structured-output contract on that surface is a taint
hazard per OpenAI's Agent-Builder Safety guidance.

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


class TaintActionableGate(WiringGate):
    gate_id = "M_taint_actionable_ratchet"
    tier = "R"
    baseline_filename = "wiring_taint_actionable_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        rows = list(
            conn.execute(
                """
                SELECT file, layer, action_edge_count, structured_output_count, gap_flag
                FROM mv_actionable_surface_without_schema
                WHERE gap_flag = 1
                """
            )
        )
        violations: list[Violation] = []
        for file_path, layer, acount, scount, gap in tqdm(rows, desc="M_taint_action", unit="node"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=file_path,
                    rule="actionable_surface_without_schema",
                    detail=f"{layer}: actions={acount}, structured_outputs={scount}",
                    extra={
                        "file": file_path,
                        "layer": layer,
                        "action_edge_count": acount,
                        "structured_output_count": scount,
                        "gap_flag": gap,
                    },
                )
            )
        return violations


def main() -> int:
    gate = TaintActionableGate()
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
