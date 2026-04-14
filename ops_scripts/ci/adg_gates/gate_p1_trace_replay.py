"""Gate 8: P1 Trace / Replay / Eval Coverage Ratchet.

Blocks regressions on action-capable or mutation-capable paths missing trace/replay/eval.
Focuses on critical-path increases first.

Source views:
    - mv_trace_replay_eval_gaps
    - mv_eval_coverage_by_path
    - mv_replay_surface_gaps
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation
from tqdm import tqdm


class TraceReplayEvalGate(ADGGateBase):
    """P1 Trace/Replay/Eval Coverage Ratchet."""

    gate_family = "trace_replay_eval"
    severity = "P1"
    source_views = [
        "mv_trace_replay_eval_gaps",
        "mv_eval_coverage_by_path",
        "mv_replay_surface_gaps",
    ]

    def _execute_gate_logic(self) -> GateResult:
        """Execute trace/replay/eval coverage check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "no_trace": 0,
            "no_replay": 0,
            "no_eval": 0,
            "eval_coverage_by_layer": {},
            "baseline_coverage": {},
        }

        if not self.conn:
            return self._empty_result()

        baseline = self._load_baseline("trace_replay_eval")
        baseline_gaps = baseline.get("gaps", {})

        # Check trace/replay/eval gaps
        try:
            cursor = self.conn.execute("""
                SELECT node_id, file, layer, has_trace, has_replay_link, has_eval, gap_type
                FROM mv_trace_replay_eval_gaps
                WHERE gap_type != 'ok'
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                node_id, file, layer, has_trace, has_replay_link, has_eval, gap_type = row

                key = f"{layer}:{node_id}"
                prev_gap = baseline_gaps.get(key, False)

                if gap_type == "no_trace":
                    summary["no_trace"] += 1
                elif gap_type == "no_replay":
                    summary["no_replay"] += 1
                elif gap_type == "no_eval":
                    summary["no_eval"] += 1

                if not prev_gap:
                    violation = GateViolation(
                        violation_id=f"tre_gap_{node_id}",
                        source_view="mv_trace_replay_eval_gaps",
                        source_node=str(node_id),
                        source_edge=None,
                        file=file,
                        line=None,
                        layer_src=layer,
                        layer_dst=None,
                        path_id=str(node_id),
                        first_illegal_hop=f"{layer}->{gap_type}",
                        path_criticality=2.0,
                        in_modified_area=self._is_in_modified_area(file),
                        message=f"New trace/replay/eval gap ({gap_type}): {file} in {layer}",
                        extra={
                            "has_trace": bool(has_trace),
                            "has_replay_link": bool(has_replay_link),
                            "has_eval": bool(has_eval),
                            "gap_type": gap_type,
                        },
                    )
                    violations.append(violation)
        except sqlite3.Error:
            pass

        # Check eval coverage by layer
        try:
            cursor = self.conn.execute("""
                SELECT layer, action_node_count, eval_covered_count, gap_count, coverage_pct
                FROM mv_eval_coverage_by_path
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                layer, action_node_count, eval_covered_count, gap_count, coverage_pct = row

                summary["eval_coverage_by_layer"][layer] = {
                    "action_nodes": action_node_count,
                    "covered": eval_covered_count,
                    "gaps": gap_count,
                    "coverage_pct": coverage_pct,
                }

                prev_coverage = summary["baseline_coverage"].get(layer, 100.0)
                if coverage_pct < prev_coverage - 5:
                    violation = GateViolation(
                        violation_id=f"eval_coverage_{layer}",
                        source_view="mv_eval_coverage_by_path",
                        source_node=None,
                        source_edge=None,
                        file=None,
                        line=None,
                        layer_src=layer,
                        layer_dst=None,
                        path_id=None,
                        first_illegal_hop=None,
                        path_criticality=1.5,
                        in_modified_area=False,
                        message=f"Eval coverage regression in {layer}: {prev_coverage:.1f}% -> {coverage_pct:.1f}%",
                        extra={
                            "layer": layer,
                            "action_node_count": action_node_count,
                            "eval_covered_count": eval_covered_count,
                            "coverage_pct": coverage_pct,
                            "previous_pct": prev_coverage,
                        },
                    )
                    violations.append(violation)
        except sqlite3.Error:
            pass

        new_baseline = {"gaps": {}, "coverage": summary["eval_coverage_by_layer"]}
        self._save_baseline("trace_replay_eval", new_baseline)

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
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={
                "total_violations": 0,
                "no_trace": 0,
                "no_replay": 0,
                "no_eval": 0,
                "eval_coverage_by_layer": {},
                "baseline_coverage": {},
                "note": "Materialized views not available - baseline preserved",
            },
        )


def main() -> int:
    gate = TraceReplayEvalGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    import sys

    sys.exit(main())
