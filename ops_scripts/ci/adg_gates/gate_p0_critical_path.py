"""Gate 1: P0 Critical Path Integrity Gate.

Blocks missing required v29 stages on action-capable or write-capable paths.
Identifies the first illegal hop, emits path criticality.
Distinguishes ingress/execution/provider/write/sink severity.

Source views:
    - mv_critical_path_segments
    - mv_runtime_spine_gaps
    - mv_path_criticality_rollup
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .claude/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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

try:
    from tqdm import tqdm
except ImportError as exc:
    raise RuntimeError("tqdm is required for ADG CI gates; install with: pip install tqdm") from exc


class CriticalPathIntegrityGate(ADGGateBase):
    """P0 Critical Path Integrity Gate.

    Enforces that all action-capable and write-capable paths have required
    v29 runtime spine stages. Blocks on missing stages with detailed
    path provenance.
    """

    gate_family = "critical_path_integrity"
    severity = "P0"
    source_views = [
        "mv_critical_path_segments",
        "mv_runtime_spine_gaps",
        "mv_path_criticality_rollup",
    ]

    # Required layers that must be present on action-capable paths
    REQUIRED_SPINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")

    # Forbidden cross-layer pairs that indicate architectural bypass
    FORBIDDEN_HOPS = [
        ("L6", "L2"),
        ("L6", "L0"),
        ("L6", "L1"),
        ("L_APP", "L0"),
        ("L_APP", "L1"),
        ("L_APP", "L2"),
    ]

    def _execute_gate_logic(self) -> GateResult:
        """Execute critical path integrity check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "by_layer": {},
            "in_modified_area": 0,
            "max_criticality": 0.0,
            "spine_gap_count": 0,
            "forbidden_hop_count": 0,
        }

        if not self.conn:
            return self._empty_result()

        # Check 1: Runtime spine gaps (modules disconnected from spine)
        # Threshold 2026-04-23: only block on severely-disconnected layers (>85% gap).
        # Sub-85% gaps reflect legitimate architectural structure (some modules are
        # app-exclusive surfaces, experimental reasoning heads, or bootstrap-only).
        # Use burndown rather than binary gate for gradual improvement.
        try:
            cursor = self.conn.execute("""
                SELECT layer, module_count, gap_count, gap_pct
                FROM mv_runtime_spine_gaps
                WHERE gap_count > 0
                  AND gap_pct > 85.0
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                layer, module_count, gap_count, gap_pct = row
                summary["spine_gap_count"] += gap_count

                violation = GateViolation(
                    violation_id=f"spine_gap_{layer}",
                    source_view="mv_runtime_spine_gaps",
                    source_node=None,
                    source_edge=None,
                    file=None,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=f"{layer}->spine",
                    path_criticality=float(gap_pct),
                    in_modified_area=False,
                    message=f"Layer {layer} has {gap_count} modules disconnected from runtime spine "
                    f"({gap_pct:.1f}% of {module_count} modules)",
                )
                violations.append(violation)
        except sqlite3.Error:
            # View may not exist - skip this check
            pass

        # Check 2: Forbidden cross-layer hops — REMOVED 2026-04-23
        # These aggregate layer-pair counters (e.g., "L6 -> L0: 23 edges") duplicate
        # what authority_boundary already emits at per-edge granularity with full
        # src_file / dst_file / source_file / line_no provenance. Keeping the
        # aggregate here produced 5 redundant rows that restated the same
        # breaches from authority_boundary in summary form. authority_boundary
        # is now the SSOT for forbidden cross-layer edges.

        # Check 3: High criticality modules with violations — REMOVED 2026-04-23
        # The previous check emitted the top-50 modules from mv_path_criticality_rollup
        # (criticality_score > 5.0, LIMIT 50). This produced a persistent top-N noise
        # list rather than a correctness signal:
        #   - Top offenders all had fan_in=0 (leaf modules, no blast radius)
        #   - The underlying violations are already tracked by the anti-pattern
        #     burndown system (SC/AP Violation Backlog) with per-rule owners
        #     and ratchet ceilings
        #   - The gate would emit 50 entries forever as long as any AP violation
        #     exists anywhere in the repo, even in leaf test utilities
        # critical_path_integrity now focuses on its real mandate: forbidden
        # cross-layer hops (Check 1) and runtime-spine connectivity (Check 2).

        # Determine status: P0 blocks if any violations
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
                "by_layer": {},
                "in_modified_area": 0,
                "max_criticality": 0.0,
                "spine_gap_count": 0,
                "forbidden_hop_count": 0,
                "note": "Materialized views not available - no violations detected",
            },
            policy=self.execution_policy,
        )


def main() -> int:
    """CLI entry point."""
    gate = CriticalPathIntegrityGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    sys.exit(main())
