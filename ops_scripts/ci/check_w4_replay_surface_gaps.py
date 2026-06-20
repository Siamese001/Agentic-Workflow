#!/usr/bin/env python3
"""Gate I2 — replay-surface / evidence-consumption gap (plan W4.7).

Reads ``mv_replay_surface_gaps`` — a node with ``mutation_count > 0``
and ``replay_link_count = 0`` is producing state mutations whose
replay surface is not consumed by downstream replay/evidence
pipelines. This is the evidence-built-not-consumed anti-pattern.

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


class ReplaySurfaceGapsGate(WiringGate):
    gate_id = "I2_replay_surface_gaps_ratchet"
    tier = "R"
    baseline_filename = "wiring_replay_surface_gaps_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        rows = list(
            conn.execute(
                """
                SELECT file, layer, mutation_count, replay_link_count, gap_flag
                FROM mv_replay_surface_gaps
                WHERE gap_flag = 1
                """
            )
        )
        violations: list[Violation] = []
        for file_path, layer, mcount, rcount, gap in tqdm(rows, desc="I2_replay_gaps", unit="node"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=file_path,
                    rule="replay_surface_unconsumed",
                    detail=f"{layer}: mutations={mcount}, replay_links={rcount}",
                    extra={
                        "file": file_path,
                        "layer": layer,
                        "mutation_count": mcount,
                        "replay_link_count": rcount,
                        "gap_flag": gap,
                    },
                )
            )
        return violations


def main() -> int:
    gate = ReplaySurfaceGapsGate()
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
