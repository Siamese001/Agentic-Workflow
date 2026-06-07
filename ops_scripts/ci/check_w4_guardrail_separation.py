#!/usr/bin/env python3
"""Gate N — guardrail / evaluator co-location (plan W4.9, Anthropic pattern).

Flags L5 guardrail / enforcement modules that share a ``writes_to``
target with an L3 orchestration (core-response) module. The Anthropic
"Building Effective Agents" evaluator-optimizer pattern requires the
screen/guardrail to be a distinct surface from the core responder —
otherwise a poisoned evaluator can silently rewrite the response.

Tier: R (ratchet).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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


class GuardrailSeparationGate(WiringGate):
    gate_id = "N_guardrail_separation_ratchet"
    tier = "R"
    baseline_filename = "wiring_guardrail_separation_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        query = """
            SELECT DISTINCT
                l5.resolved_path AS l5_path,
                l3.resolved_path AS l3_path,
                tgt.resolved_path AS shared_target
            FROM edges e5
            JOIN nodes l5  ON l5.id  = e5.src_id
            JOIN nodes tgt ON tgt.id = e5.dst_id
            JOIN edges e3  ON e3.dst_id = e5.dst_id AND e3.relation_type = 'writes_to'
            JOIN nodes l3  ON l3.id  = e3.src_id
            WHERE e5.relation_type = 'writes_to'
              AND l5.layer = 'L5'
              AND l3.layer = 'L3'
              AND l5.resolved_path IS NOT NULL
              AND l3.resolved_path IS NOT NULL
              AND tgt.resolved_path IS NOT NULL
        """
        rows = list(conn.execute(query))
        violations: list[Violation] = []
        for l5_path, l3_path, shared in tqdm(rows, desc="N_guardrail_sep", unit="pair"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{l5_path} <-> {l3_path}",
                    rule="l5_l3_shared_write_target",
                    detail=f"shared target: {shared}",
                    extra={
                        "l5_path": l5_path,
                        "l3_path": l3_path,
                        "shared_target": shared,
                    },
                )
            )
        return violations


def main() -> int:
    gate = GuardrailSeparationGate()
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
