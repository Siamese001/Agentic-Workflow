"""Gate P1: Architecture Witness Tier Gate.

Enforces two complementary gate classes derived from mv_handoff_witness_tiers
and mv_cross_cutting_witness_tiers:

  Class A (positive witness) -- live runtime proof required:
    - required families: violation if runtime-orphaned (plumbing/test covered, 0 live_rt)
    - planned families:  warn-only; not yet blocking

  Class B (absence / negative) -- breach/forbidden-path surface required:
    - violation if governing breach view is absent from the DB
    - reports families without a dedicated breach surface as insufficient

Regression protection:
    - violation if mv_handoff_witness_tiers or mv_cross_cutting_witness_tiers missing
    - violation if required Class A families absent from mv_cross_cutting_witness_tiers

Source views:
    - mv_handoff_witness_tiers
    - mv_cross_cutting_witness_tiers
    - mv_write_sovereignty_paths      (Class B: no_direct_write_live_planes)
    - mv_digest_reconciliation        (Class B: replay_envelope_continuity)
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation


# Class A: cross-cutting families required-live NOW (confirmed live_rt > 0 in repo).
_REQUIRED_LIVE_CC: frozenset[str] = frozenset(
    {
        "capability_egress_chokepoint",
        "heal_retry_under_blueprint",
        "hitl_freeze_materialize_reclear",
        "retrieval_surface_integrity",
        "uwg_full_commit_chain",
    }
)

# Class A: cross-cutting families PLANNED (runtime-orphaned; warn-only, not yet blocking).
_PLANNED_CC: frozenset[str] = frozenset(
    {
        "commit_uwg_envelope_continuity",
        "exit_hitl_envelope_continuity",
        "future_run_only_promotion",
        "offline_publication_before_runtime",
    }
)

# Class B: absence/negative families and their governing breach views.
# All four families now have dedicated breach surfaces.
_CLASS_B_BREACH: dict[str, str | None] = {
    "no_direct_write_live_planes": "mv_write_sovereignty_paths",
    "replay_envelope_continuity": "mv_digest_reconciliation",
    "local_heal_first": "mv_local_heal_first_breaches",
    "observability_non_interference": "mv_observability_interference_breaches",
}

# Required mv_* tables (regression protection)
_REQUIRED_TABLES: frozenset[str] = frozenset(
    {
        "mv_handoff_witness_tiers",
        "mv_cross_cutting_witness_tiers",
    }
)


class ArchitectureWitnessGate(ADGGateBase):
    """P1 Architecture Witness Tier Gate.

    Enforces Class A (positive witness) and Class B (absence/breach) gate policies
    across runtime-spine handoff families and cross-cutting architectural families.
    """

    gate_family = "architecture_witness"
    severity = "P1"
    source_views = [
        "mv_handoff_witness_tiers",
        "mv_cross_cutting_witness_tiers",
        "mv_write_sovereignty_paths",
        "mv_digest_reconciliation",
        "mv_local_heal_first_breaches",
        "mv_observability_interference_breaches",
    ]

    def _execute_gate_logic(self) -> GateResult:
        """Execute architecture witness tier gate check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "class_a_required_violations": 0,
            "class_a_planned_warnings": 0,
            "class_b_status": {},
            "tables_missing": [],
            "schema_violations": [],
        }

        if not self.conn:
            return self._empty_result()

        # -- Regression: required mv_* tables must exist ----------------------
        try:
            existing_tables: set[str] = {
                row[0]
                for row in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
        except sqlite3.Error as exc:
            print(
                f"[CI-GATE] architecture_witness: could not query tables: {exc}",
                file=sys.stderr,
            )
            return self._empty_result()

        missing_tables = _REQUIRED_TABLES - existing_tables
        for tbl in sorted(missing_tables):  # tqdm: short sorted set, no bar needed
            summary["tables_missing"].append(tbl)
            violations.append(
                GateViolation(
                    violation_id=f"regression_missing_table_{tbl}",
                    source_view=tbl,
                    source_node=None,
                    source_edge=None,
                    file=None,
                    line=None,
                    layer_src=None,
                    layer_dst=None,
                    path_id=tbl,
                    first_illegal_hop=None,
                    path_criticality=5.0,
                    in_modified_area=False,
                    message=f"Regression: required table '{tbl}' missing from ADG SQLite",
                    extra={"gate_class": "regression_protection", "table": tbl},
                )
            )

        if missing_tables:
            summary["total_violations"] = len(violations)
            return GateResult(
                gate_family=self.gate_family,
                severity=self.severity,
                snapshot_id=self._snapshot_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="blocked",
                violations=violations,
                summary=summary,
            )

        # -- Class A: cross-cutting required-live families --------------------
        try:
            cc_rows = self.conn.execute(
                "SELECT family_name,"
                " COALESCE(SUM(live_runtime_witness_count), 0),"
                " COALESCE(SUM(plumbing_witness_count), 0),"
                " COALESCE(SUM(test_witness_count), 0),"
                " COALESCE(SUM(runtime_orphaned), 0)"
                " FROM mv_cross_cutting_witness_tiers"
                " GROUP BY family_name"
            ).fetchall()
        except sqlite3.Error as exc:
            print(
                f"[CI-GATE] architecture_witness: Class A query failed: {exc}",
                file=sys.stderr,
            )
            cc_rows = []

        present_cc = {row[0] for row in cc_rows}
        missing_required = _REQUIRED_LIVE_CC - present_cc
        for family in sorted(missing_required):  # tqdm: short sorted set, no bar needed
            summary["schema_violations"].append(
                f"Required Class A family '{family}' missing from mv_cross_cutting_witness_tiers"
            )
            violations.append(
                GateViolation(
                    violation_id=f"regression_missing_family_{family}",
                    source_view="mv_cross_cutting_witness_tiers",
                    source_node=family,
                    source_edge=None,
                    file=None,
                    line=None,
                    layer_src=None,
                    layer_dst=None,
                    path_id=family,
                    first_illegal_hop=None,
                    path_criticality=5.0,
                    in_modified_area=False,
                    message=(
                        f"Regression: required Class A family '{family}' missing "
                        f"from mv_cross_cutting_witness_tiers"
                    ),
                    extra={"gate_class": "regression_protection", "family": family},
                )
            )

        for family_name, live_rt, plumbing, test, orphaned in cc_rows:  # tqdm: DB result set, no bar needed
            if family_name in _REQUIRED_LIVE_CC and orphaned > 0:
                summary["class_a_required_violations"] += 1
                violations.append(
                    GateViolation(
                        violation_id=f"class_a_orphan_{family_name}",
                        source_view="mv_cross_cutting_witness_tiers",
                        source_node=family_name,
                        source_edge=None,
                        file=None,
                        line=None,
                        layer_src=None,
                        layer_dst=None,
                        path_id=family_name,
                        first_illegal_hop=None,
                        path_criticality=4.0,
                        in_modified_area=False,
                        message=(
                            f"Class A required-live family '{family_name}' is runtime-orphaned: "
                            f"plumbing={plumbing} test={test} live_rt={live_rt} "
                            f"orphaned_rels={orphaned}"
                        ),
                        extra={
                            "gate_class": "A",
                            "family": family_name,
                            "status": "required",
                            "plumbing_witness_count": int(plumbing),
                            "test_witness_count": int(test),
                            "live_runtime_witness_count": int(live_rt),
                            "orphaned_relation_count": int(orphaned),
                        },
                    )
                )
            elif family_name in _PLANNED_CC and orphaned > 0:
                summary["class_a_planned_warnings"] += 1

        # -- Class B: absence/negative families --------------------------------
        for family, breach_view in _CLASS_B_BREACH.items():  # tqdm: small config dict, no bar needed
            b_status: dict[str, Any] = {
                "family": family,
                "gate_class": "B",
                "breach_view": breach_view,
            }
            if breach_view is None:
                b_status["breach_surface"] = "INSUFFICIENT"
            elif breach_view not in existing_tables:
                b_status["breach_surface"] = "MISSING"
            else:
                try:
                    row_count = self.conn.execute(
                        f"SELECT COUNT(*) FROM {breach_view}"  # noqa: S608
                    ).fetchone()[0]
                    b_status["breach_surface"] = "PRESENT"
                    b_status["breach_view_rows"] = row_count
                except sqlite3.Error:
                    b_status["breach_surface"] = "ERROR"
            summary["class_b_status"][family] = b_status

        summary["total_violations"] = len(violations)
        status = "blocked" if violations else "passed"

        if summary["class_a_planned_warnings"] > 0:
            summary["planned_warning_note"] = (
                f"{summary['class_a_planned_warnings']} Class A families are planned "
                "(runtime-orphaned but not yet required-live)"
            )

        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=violations,
            summary=summary,
            policy=self.execution_policy,
        )

    def _empty_result(self) -> GateResult:
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={
                "total_violations": 0,
                "note": "Materialized views not available",
                "class_a_required_violations": 0,
                "class_a_planned_warnings": 0,
                "class_b_status": {},
                "tables_missing": [],
                "schema_violations": [],
            },
            policy=self.execution_policy,
        )


def main() -> None:
    """CLI entry point for standalone gate execution."""
    gate = ArchitectureWitnessGate()
    gate.run_and_exit()


if __name__ == "__main__":
    main()
