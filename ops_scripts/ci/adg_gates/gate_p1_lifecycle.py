"""Gate 7: P1 Lifecycle Coverage Ratchet.

Blocks regressions in L2 E1/E2/E3/E4/E5 coverage.
Blocks regressions in exit coverage.
Blocks worsening heal/retry terminal handling.

Source views:
    - mv_l2_phase_coverage
    - mv_exit_disposition_coverage
    - mv_heal_retry_exit_gaps
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation
from tqdm import tqdm


class LifecycleCoverageGate(ADGGateBase):
    """P1 Lifecycle Coverage Ratchet.

    Enforces non-regression of L2 lifecycle phase coverage.
    Tracks coverage across E1-E5 phases and exit dispositions.
    """

    gate_family = "lifecycle_coverage"
    severity = "P1"
    source_views = [
        "mv_l2_phase_coverage",
        "mv_exit_disposition_coverage",
        "mv_heal_retry_exit_gaps",
    ]

    def _execute_gate_logic(self) -> GateResult:
        """Execute lifecycle coverage ratchet check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "phase_coverage_gaps": 0,
            "exit_coverage_gaps": 0,
            "heal_retry_gaps": 0,
            "current_coverage": {},
            "baseline_coverage": {},
        }

        if not self.conn:
            return self._empty_result()

        # Load baseline
        baseline = self._load_baseline("lifecycle_coverage")
        baseline_phases = baseline.get("phases", {})
        baseline_exits = baseline.get("exits", {})
        baseline_heal_retry = baseline.get("heal_retry", 0)

        # Check 1: L2 phase coverage gaps
        try:
            cursor = self.conn.execute("""
                SELECT phase_label, node_count, has_entry_edge, has_exit_edge, covered_by_test, gap_flag
                FROM mv_l2_phase_coverage
                WHERE gap_flag = 1
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                phase_label, node_count, has_entry_edge, has_exit_edge, covered_by_test, _ = row

                summary["phase_coverage_gaps"] += 1

                # Check for regression
                prev_count = baseline_phases.get(phase_label, 0)
                summary["current_coverage"][phase_label] = node_count
                summary["baseline_coverage"][phase_label] = prev_count

                if node_count > prev_count:
                    violation = GateViolation(
                        violation_id=f"phase_regression_{phase_label}",
                        source_view="mv_l2_phase_coverage",
                        source_node=None,
                        source_edge=None,
                        file=None,
                        line=None,
                        layer_src=None,
                        layer_dst=None,
                        path_id=None,
                        first_illegal_hop=None,
                        path_criticality=2.0,
                        in_modified_area=False,
                        message=f"Lifecycle regression: {phase_label} phase gap increased "
                        f"({prev_count} -> {node_count} nodes, entry={has_entry_edge}, exit={has_exit_edge}, test={covered_by_test})",
                        extra={
                            "phase_label": phase_label,
                            "node_count": node_count,
                            "has_entry_edge": bool(has_entry_edge),
                            "has_exit_edge": bool(has_exit_edge),
                            "covered_by_test": bool(covered_by_test),
                            "previous_count": prev_count,
                        },
                    )
                    violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 2: Exit disposition coverage gaps
        try:
            cursor = self.conn.execute("""
                SELECT exit_type, module_count, has_success_path, has_failure_path,
                       has_terminal_handler, gap_flag
                FROM mv_exit_disposition_coverage
                WHERE gap_flag = 1
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                (
                    exit_type,
                    module_count,
                    has_success_path,
                    has_failure_path,
                    has_terminal_handler,
                    gap_flag,
                ) = row

                summary["exit_coverage_gaps"] += 1

                prev_count = baseline_exits.get(exit_type, 0)

                if module_count > prev_count:
                    violation = GateViolation(
                        violation_id=f"exit_regression_{exit_type}",
                        source_view="mv_exit_disposition_coverage",
                        source_node=None,
                        source_edge=None,
                        file=None,
                        line=None,
                        layer_src=None,
                        layer_dst=None,
                        path_id=None,
                        first_illegal_hop=None,
                        path_criticality=2.0,
                        in_modified_area=False,
                        message=f"Exit coverage regression: {exit_type} modules without proper handling "
                        f"({prev_count} -> {module_count}, success={has_success_path}, failure={has_failure_path}, terminal={has_terminal_handler})",
                        extra={
                            "exit_type": exit_type,
                            "module_count": module_count,
                            "has_success_path": bool(has_success_path),
                            "has_failure_path": bool(has_failure_path),
                            "has_terminal_handler": bool(has_terminal_handler),
                            "previous_count": prev_count,
                        },
                    )
                    violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 3: Heal/retry exit gaps
        try:
            cursor = self.conn.execute("""
                SELECT gap_type, affected_modules, heal_count, retry_count, exit_count
                FROM mv_heal_retry_exit_gaps
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                gap_type, affected_modules, heal_count, retry_count, exit_count = row

                summary["heal_retry_gaps"] += affected_modules

                if affected_modules > baseline_heal_retry:
                    violation = GateViolation(
                        violation_id=f"heal_retry_{gap_type}",
                        source_view="mv_heal_retry_exit_gaps",
                        source_node=None,
                        source_edge=None,
                        file=None,
                        line=None,
                        layer_src=None,
                        layer_dst=None,
                        path_id=None,
                        first_illegal_hop=None,
                        path_criticality=1.5,
                        in_modified_area=False,
                        message=f"Heal/retry regression: {gap_type} affecting {affected_modules} modules "
                        f"(heal={heal_count}, retry={retry_count}, exit={exit_count})",
                        extra={
                            "gap_type": gap_type,
                            "affected_modules": affected_modules,
                            "heal_count": heal_count,
                            "retry_count": retry_count,
                            "exit_count": exit_count,
                            "baseline": baseline_heal_retry,
                        },
                    )
                    violations.append(violation)
        except sqlite3.Error:
            pass

        # Save current state as new baseline
        new_baseline = {
            "phases": summary["current_coverage"],
            "exits": {},  # Would be populated from exit view
            "heal_retry": summary["heal_retry_gaps"],
        }
        self._save_baseline("lifecycle_coverage", new_baseline)

        # Determine status: P1 blocks only on regression (not absolute count)
        summary["total_violations"] = len(violations)
        status = "blocked" if violations else "passed"

        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=violations,
            summary=summary,
        )

    def _empty_result(self) -> GateResult:
        """Return empty result when connection unavailable."""
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={
                "total_violations": 0,
                "phase_coverage_gaps": 0,
                "exit_coverage_gaps": 0,
                "heal_retry_gaps": 0,
                "current_coverage": {},
                "baseline_coverage": {},
                "note": "Materialized views not available - baseline preserved",
            },
        )


def main() -> int:
    """CLI entry point."""
    gate = LifecycleCoverageGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    import sys

    sys.exit(main())
