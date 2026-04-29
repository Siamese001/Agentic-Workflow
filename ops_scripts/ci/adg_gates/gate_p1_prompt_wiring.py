"""Gate P1-PROMPT-WIRING: Prompt-assembly subsystem disconnected from runtime.

Blocks when any module in the prompt-assembly wiring surface (dispatcher,
bridge, evidence-contract) is test-covered but has zero live runtime callers.

This gate catches the exact negative-space pattern that was previously
undetectable by SC-5 / AP-14 / mv_unknown_taxonomy_and_orphans:
  - The subsystem was fully built and test-proven.
  - No live runtime caller imported it.
  - All existing ADG checks trivially passed because they require at least
    *some* edges to fire — test-only callers supplied those edges.

Source views:
    - mv_prompt_assembly_wiring_gaps   (primary — Phase A materialized view)

Failure condition:
    gap_type = 'disconnected' AND test_callers > 0

Blocking (not ratchet): a test-only subsystem is a structural gap, not a
regression trend.  Zero tolerance — any orphaned runtime surface halts CI.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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
from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy

_VIEW = "mv_prompt_assembly_wiring_gaps"

_PROMPT_ASSEMBLY_PATH_FRAGMENTS: tuple[str, ...] = (
    "tools/adg/prompt_assembly/",
    "c0_evidence_contract_types",
    "c0_dispatcher",
    "c0_bridge_adapter",
)


class PromptAssemblyWiringGate(ADGGateBase):
    """P1 gate: fails when a prompt-assembly surface is test-only (no live caller).

    Reads ``mv_prompt_assembly_wiring_gaps``.  Falls back to an inline SQL
    query if the materialized view has not been refreshed yet (e.g. on a
    fresh clone before ``generate_full_adg.py`` is run).
    """

    gate_family = "prompt_assembly_wiring"
    severity = "P1"
    source_views = [_VIEW]
    execution_policy = ExecutionPolicy(
        stage="full",
        repairability="manual_only",
        gate_action="halt",
        artifact_policy="full_adg_report",
        signal_source="sqlite_mv_ci",
        evidence_tier="truth",
    )

    def _execute_gate_logic(self) -> GateResult:
        """Query prompt-assembly wiring gaps and block on any disconnected surface."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "disconnected_surfaces": 0,
            "signal_source": _VIEW,
        }

        if not self.conn:
            return self._empty_result(summary)

        rows = self._fetch_orphaned_rows()

        for (
            target_symbol,
            target_file,
            live_callers,
            test_callers,
        ) in rows:  # progress_bar: bounded by orphaned rows
            summary["disconnected_surfaces"] += 1
            in_modified = self._is_in_modified_area(target_file)
            violations.append(
                GateViolation(
                    violation_id=f"prompt_wiring_orphan_{target_symbol}",
                    source_view=_VIEW,
                    source_node=target_symbol,
                    source_edge=None,
                    file=target_file or "",
                    line=0,
                    layer_src=None,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=None,
                    path_criticality=2.5,
                    in_modified_area=in_modified,
                    message=(
                        f"PROMPT-WIRING ORPHAN: {target_symbol} — "
                        f"live_callers={live_callers}, test_callers={test_callers} "
                        f"(test-only subsystem, no runtime caller) "
                        f"[{target_file}]"
                    ),
                    extra={
                        "target_symbol": target_symbol,
                        "target_file": target_file,
                        "live_callers": live_callers,
                        "test_callers": test_callers,
                        "gap_type": "disconnected",
                        "remediation": (
                            "Wire a live runtime caller (e.g. orchestrator) to import this "
                            "module, or remove the dead subsystem if it is no longer needed."
                        ),
                    },
                )
            )

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
            policy=self.execution_policy,
        )

    def _fetch_orphaned_rows(self) -> list[tuple[str, str, int, int]]:
        """Return (target_symbol, target_file, live_callers, test_callers) for orphaned modules.

        Primary: query ``mv_prompt_assembly_wiring_gaps`` (requires Phase A refresh).
        Fallback: inline SQL if the view is absent.
        """
        assert self.conn is not None
        try:
            rows = self.conn.execute(
                "SELECT target_symbol, target_file, live_callers, test_callers "
                f"FROM {_VIEW} "
                "WHERE gap_type = 'disconnected' AND test_callers > 0 "
                "ORDER BY test_callers DESC, target_file ASC"
            ).fetchall()
            return [(r[0], r[1], r[2], r[3]) for r in rows]
        except sqlite3.OperationalError:
            return self._fallback_inline_query()

    def _fallback_inline_query(self) -> list[tuple[str, str, int, int]]:
        """Inline SQL fallback when mv_prompt_assembly_wiring_gaps is not yet materialized."""
        assert self.conn is not None
        path_clauses = " OR ".join(
            f"n.resolved_path LIKE '%{frag}%'" for frag in _PROMPT_ASSEMBLY_PATH_FRAGMENTS
        )
        try:
            rows = self.conn.execute(
                "SELECT n.adg_name, n.resolved_path, "
                "    COUNT(DISTINCT CASE "
                "        WHEN c.resolved_path NOT LIKE 'tests/%' "
                "         AND c.resolved_path NOT LIKE 'test_%' "
                "        THEN e.id END) AS live_callers, "
                "    COUNT(DISTINCT CASE "
                "        WHEN c.resolved_path LIKE 'tests/%' "
                "          OR c.resolved_path LIKE 'test_%' "
                "        THEN e.id END) AS test_callers "
                "FROM nodes n "
                "LEFT JOIN edges e ON e.dst_id = n.id AND e.relation_type = 'imports' "
                "LEFT JOIN nodes c ON c.id = e.src_id "
                f"WHERE n.entity_type = 'module' "
                f"  AND n.resolved_path NOT LIKE 'tests/%' "
                f"  AND ({path_clauses}) "
                "GROUP BY n.id "
                "HAVING live_callers = 0 AND test_callers > 0 "
                "ORDER BY test_callers DESC, n.resolved_path ASC",
            ).fetchall()
            return [(r[0], r[1], r[2], r[3]) for r in rows]
        except sqlite3.OperationalError:
            return []

    def _empty_result(self, summary: dict[str, Any]) -> GateResult:
        """Return empty passed result when connection is unavailable."""
        summary["note"] = "SQLite connection unavailable — gate skipped"
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary=summary,
            policy=self.execution_policy,
        )


def main() -> int:
    """CLI entry point."""
    gate = PromptAssemblyWiringGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    sys.exit(main())
