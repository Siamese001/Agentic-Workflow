#!/usr/bin/env python3
"""Gate C4 — policy decision without audit (plan W4.4).

Flags ``controls_flow`` edges whose source module has no L6 emission
(``emits_side_effect`` / ``syncs_l4_telemetry`` / ``l6_ingests_l4_trace``).
Policy enforcement without an audit trail is a governance hazard.

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

AUDIT_RELATIONS = ("emits_side_effect", "syncs_l4_telemetry", "l6_ingests_l4_trace")


class PolicyWithoutAuditGate(WiringGate):
    gate_id = "C4_policy_without_audit_ratchet"
    tier = "R"
    baseline_filename = "wiring_policy_without_audit_ratchet.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        audit_list = ",".join(f"'{r}'" for r in AUDIT_RELATIONS)
        query = f"""
            SELECT DISTINCT
                src.resolved_path AS policy_path,
                src.layer         AS policy_layer
            FROM edges pe
            JOIN nodes src ON src.id = pe.src_id
            WHERE pe.relation_type = 'controls_flow'
              AND src.resolved_path IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM edges ae
                  WHERE ae.src_id = pe.src_id
                    AND ae.relation_type IN ({audit_list})
              )
        """
        rows = list(conn.execute(query))
        violations: list[Violation] = []
        for policy_path, policy_layer in tqdm(rows, desc="C4_policy_audit", unit="mod"):
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=policy_path,
                    rule="policy_without_audit",
                    detail=f"{policy_layer}: controls_flow present; no audit emission",
                    extra={"policy_path": policy_path, "policy_layer": policy_layer},
                )
            )
        return violations


def main() -> int:
    gate = PolicyWithoutAuditGate()
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
