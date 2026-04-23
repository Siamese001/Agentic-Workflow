#!/usr/bin/env python3
"""Gate P — structured-field extraction boundary (plan W5.2).

Reads ``mv_structured_output_gaps`` — a node that calls
``generates_prompt`` at scale but has no structured-output schema
attached violates OpenAI's "structured-field extraction boundary"
principle: external text must hit a type surface before influencing
decisions.

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


class StructuredOutputGate(WiringGate):
    gate_id = "P_structured_output_ratchet"
    tier = "R"
    baseline_filename = "wiring_structured_output_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        rows = list(
            conn.execute(
                """
                SELECT file, layer, generates_prompt_count, output_schema_flag, gap_flag
                FROM mv_structured_output_gaps
                WHERE gap_flag = 1
                """
            )
        )
        violations: list[Violation] = []
        for file_path, layer, pcount, schema_flag, gap in tqdm(rows, desc="P_struct_out", unit="node"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=file_path,
                    rule="prompt_generation_without_schema",
                    detail=f"{layer}: generates_prompt={pcount}, schema={schema_flag}",
                    extra={
                        "file": file_path,
                        "layer": layer,
                        "generates_prompt_count": pcount,
                        "output_schema_flag": schema_flag,
                        "gap_flag": gap,
                    },
                )
            )
        return violations


def main() -> int:
    gate = StructuredOutputGate()
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
