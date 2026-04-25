#!/usr/bin/env python3
"""Gate AUDIT-6 — violation triage SLA ratchet.

Two enforcement rules:

1. **Hard block (Tier B)** — any violation with severity HIGH /
   CRITICAL / P0 and ``disposition='untriaged'`` blocks the build
   immediately. High-severity defects MUST be acknowledged.

2. **Count ratchet (Tier R)** — total count of ``disposition='untriaged'``
   rows is locked at the seeded baseline. Any new untriaged row regresses
   the build, forcing the team to disposition before merge.

The ADG ``violations`` table has no ``first_seen`` column at the
current schema version, so a true age-based SLA is deferred. This
gate's count ratchet is the working substitute — it forces dispositioning
on every increment.

Tier: hybrid (B for the hard rule + R for the ratchet). Reports under
the Tier R baseline shape; Tier B violations are emitted with severity
``fail`` so they always exit non-zero.
"""

from __future__ import annotations

import sqlite3
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

HARD_SEVERITIES = ("HIGH", "CRITICAL", "P0")


class ViolationAgingSlaGate(WiringGate):
    gate_id = "AUDIT_6_violation_aging_sla"
    tier = "R"
    baseline_filename = "audit_violation_aging_sla.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        cur = conn.cursor()
        violations: list[Violation] = []

        # Rule 1 — hard block on HIGH/CRITICAL/P0 untriaged
        sev_placeholders = ",".join("?" * len(HARD_SEVERITIES))
        cur.execute(
            f"""
            SELECT id, category, severity, evidence, file_path, line_no
            FROM violations
            WHERE disposition = 'untriaged'
              AND severity IN ({sev_placeholders})
            """,
            HARD_SEVERITIES,
        )
        for vid, category, severity, evidence, file_path, line_no in cur.fetchall():
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier="B",
                    subject=f"{file_path}:{line_no}",
                    rule="high_severity_violation_untriaged",
                    detail=f"category={category} severity={severity} evidence={evidence}",
                    severity="fail",
                    extra={
                        "violation_id": vid,
                        "category": category,
                        "severity": severity,
                        "evidence": evidence,
                        "file_path": file_path,
                        "line_no": line_no,
                        "rule_class": "hard_block",
                    },
                )
            )

        # Rule 2 — count ratchet on all untriaged
        cur.execute("SELECT COUNT(*) FROM violations WHERE disposition = 'untriaged'")
        untriaged_total = cur.fetchone()[0]
        # Emit ONE synthetic violation per untriaged row so ratchet semantics work uniformly
        cur.execute(
            """
            SELECT id, category, severity, file_path, line_no
            FROM violations
            WHERE disposition = 'untriaged'
              AND severity NOT IN ('HIGH', 'CRITICAL', 'P0')
            """
        )
        for vid, category, severity, file_path, line_no in cur.fetchall():
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{file_path}:{line_no}",
                    rule="violation_remains_untriaged",
                    detail=f"category={category} severity={severity}",
                    extra={
                        "violation_id": vid,
                        "category": category,
                        "severity": severity,
                        "file_path": file_path,
                        "line_no": line_no,
                        "untriaged_total": untriaged_total,
                        "rule_class": "count_ratchet",
                    },
                )
            )
        return violations


def main() -> int:
    gate = ViolationAgingSlaGate()
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
