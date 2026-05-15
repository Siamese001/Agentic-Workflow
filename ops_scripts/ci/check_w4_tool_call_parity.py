#!/usr/bin/env python3
"""Gate O — tool-call ground-truth parity (plan W4.8, Anthropic pattern).

Flags modules that invoke a provider/tool (``invokes_provider`` or
``routes_through``) but emit zero observability edges. Per Anthropic's
"Building Effective Agents" guidance, every tool invocation must have
a ground-truth receipt at the observability layer — otherwise the
agent cannot self-audit.

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

TOOL_RELATIONS = ("invokes_provider", "routes_through")
RECEIPT_RELATIONS = (
    "emits_side_effect",
    "syncs_l4_telemetry",
    "stamps_execution_packet",
    "triggered_telemetry",
)


class ToolCallParityGate(WiringGate):
    gate_id = "O_tool_call_parity_ratchet"
    tier = "R"
    baseline_filename = "wiring_tool_call_parity_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        tool_list = ",".join(f"'{r}'" for r in TOOL_RELATIONS)
        receipt_list = ",".join(f"'{r}'" for r in RECEIPT_RELATIONS)
        query = f"""
            SELECT DISTINCT
                src.resolved_path AS caller_path,
                src.layer         AS caller_layer
            FROM edges te
            JOIN nodes src ON src.id = te.src_id
            WHERE te.relation_type IN ({tool_list})
              AND src.resolved_path IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM edges re
                  WHERE re.src_id = te.src_id
                    AND re.relation_type IN ({receipt_list})
              )
        """
        rows = list(conn.execute(query))
        violations: list[Violation] = []
        for caller_path, caller_layer in tqdm(rows, desc="O_tool_call_parity", unit="mod"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=caller_path,
                    rule="tool_call_without_receipt",
                    detail=f"{caller_layer}: invokes tool; no observability emission",
                    extra={"caller_path": caller_path, "caller_layer": caller_layer},
                )
            )
        return violations


def main() -> int:
    gate = ToolCallParityGate()
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
