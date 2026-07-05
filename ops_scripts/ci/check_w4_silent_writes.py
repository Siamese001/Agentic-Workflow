#!/usr/bin/env python3
"""Gate C3 — silent write (no same-surface side-effect emit) (plan W4.3).

Flags modules with ``writes_to`` edges that emit zero
``emits_side_effect`` edges. Persistent state mutation without a
telemetry/audit sibling is a silent-write hazard.

Tier: R (ratchet).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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


class SilentWritesGate(WiringGate):
    gate_id = "C3_silent_writes_ratchet"
    tier = "R"
    baseline_filename = "wiring_silent_writes_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        query = """
            SELECT DISTINCT
                src.resolved_path AS writer_path,
                src.layer         AS writer_layer,
                src.id            AS writer_id
            FROM edges we
            JOIN nodes src ON src.id = we.src_id
            WHERE we.relation_type = 'writes_to'
              AND src.resolved_path IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM edges se
                  WHERE se.src_id = we.src_id
                    AND se.relation_type = 'emits_side_effect'
              )
              AND NOT EXISTS (
                  SELECT 1 FROM edges se
                  WHERE se.dst_id = we.src_id
                    AND se.relation_type = 'emits_side_effect'
              )
        """
        rows = list(conn.execute(query))
        violations: list[Violation] = []
        for writer_path, writer_layer, _wid in tqdm(rows, desc="C3_silent_writes", unit="mod"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=writer_path,
                    rule="writes_without_side_effect_emit",
                    detail=f"{writer_layer}: writes_to present; no emits_side_effect",
                    extra={"writer_path": writer_path, "writer_layer": writer_layer},
                )
            )
        return violations


def main() -> int:
    gate = SilentWritesGate()
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
