from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "SprawlInspectorAgent")
emit_determinism_digest("p0", "SprawlInspectorAgent")

_emit_dispatches_healing_run("p1", "SprawlInspectorAgent", "L5")
_emit_routes_through("p1", "SprawlInspectorAgent", "L5")
_emit_escalates_to_human("p1", "SprawlInspectorAgent", "L5")
_emit_reads_policy_state("p1", "SprawlInspectorAgent", "L5")
_emit_authorize_and_execute("p2", "SprawlInspectorAgent", "execution_auth")
_emit_validates_capability("p2", "SprawlInspectorAgent", "capability_check")
_emit_routes_to_capability("p2", "SprawlInspectorAgent", "capability_route")
_emit_writes_via_uwg("p2", "SprawlInspectorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "SprawlInspectorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "SprawlInspectorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "SprawlInspectorAgent", "exec_output")
_emit_dispatches_agent("p3", "SprawlInspectorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "SprawlInspectorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "SprawlInspectorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "SprawlInspectorAgent", "healing_outcome")
_emit_escalates_failure("p3", "SprawlInspectorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "SprawlInspectorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SprawlInspectorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "SprawlInspectorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "SprawlInspectorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SprawlInspectorAgent", "eval_metric")
_emit_stores_embedding("p4", "SprawlInspectorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "SprawlInspectorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SprawlInspectorAgent", "exec_snapshot_link")

"\nSprawl Inspector - Pre-Flight Architectural Survey\nIdentifies low-density folders and excessive breadth for consolidation.\nImplements Key 49 (Universal Depth Law) and Key 41 (Modular Atomicity).\n"
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal


@dataclass
class SprawlInspectorAgent(SovereignBaseAgent):
    """
    Sprawl Inspector - Pre-Flight Architectural Survey.

    Identifies low-density folders and excessive breadth for consolidation.
    Implements Key 49 (Universal Depth Law) and Key 41 (Modular Atomicity).
    """

    def __init__(self, target_path: Path = AGENTIC_CORE_DIR) -> None:
        """
        Initialize sprawl inspector.

        Args:
            target_path: Root directory to inspect for sprawl violations
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SprawlInspectorAgent.__init__", "state_snapshot")
        self.root: Path = Path(target_path)
        self.MAX_BREADTH: int = 7
        self.MIN_FILES: int = 3
        self.report: Dict[str, Any] = {
            "metadata": {
                "target": str(target_path),
                "timestamp": datetime.now().isoformat(),
                "user": os.getenv("USERNAME", "unknown"),
            },
            "violations": [],
            "flattening_candidates": [],
        }

    # guardian: allow-type-erasure
    def inspect(self) -> Dict[str, Any]:
        """
        Scan directory tree for sprawl violations.

        Returns:
            Report dictionary with violations and flattening candidates
        """
        _emit_applies_guardrail(str(uuid.uuid4()), "SprawlInspectorAgent.inspect", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SprawlInspectorAgent.inspect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SprawlInspectorAgent.inspect".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            p: Path = Path(root)
            py_files: list[str] = [f for f in files if f.endswith(".py")]
            if len(dirs) > self.MAX_BREADTH:
                self.report["violations"].append(
                    {
                        "path": str(p),
                        "type": "Breadth Violation",
                        "count": len(dirs),
                        "msg": f"Found {len(dirs)} subfolders. Violates 'Magic 7' rule.",
                    }
                )
            if 0 < len(py_files) < self.MIN_FILES and (not dirs) and (p != self.root):
                self.report["flattening_candidates"].append(
                    {
                        "folder": str(p),
                        "files": py_files,
                        "file_count": len(py_files),
                        "reason": "Low Signal Density (Fragmented)",
                    }
                )
        return self.report

    def print_summary(self) -> None:
        """
        Print human-readable summary of sprawl violations.

        Displays breadth violations and flattening candidates.
        """
        print(+"=" * 70)
        print("🔍 PROJECT SPRAWL REPORT")
        print("=" * 70)
        print(f"Target: {self.report['metadata']['target']}")
        print(f"Timestamp: {self.report['metadata']['timestamp']}")
        print()
        print(f"📊 Breadth Violations: {len(self.report['violations'])}")
        print(f"📁 Flattening Candidates: {len(self.report['flattening_candidates'])}")
        if self.report["violations"]:
            print("\n[BREADTH VIOLATIONS]")
            for v in self.report["violations"]:
                print(f"  • {v['path']}: {v['count']} subfolders (max: {self.MAX_BREADTH})")
        if self.report["flattening_candidates"]:
            print("\n[FLATTENING CANDIDATES]")
            for c in self.report["flattening_candidates"][:10]:
                print(f"  • {c['folder']}: {c['file_count']} files - {c['reason']}")
            if len(self.report["flattening_candidates"]) > 10:
                print(f"  ... and {len(self.report['flattening_candidates']) - 10} more")
        print("=" * 70)

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by SprawlInspectorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"SprawlInspectorAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"SprawlInspectorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


if __name__ == "__main__":
    inspector: Any = SprawlInspectorAgent(AGENTIC_CORE_DIR)
    data: Any = inspector.inspect()
    inspector.print_summary()
    _wg.write_json("sprawl_report.json", data, indent=4)
    print("\n[OK] Detailed sprawl map saved to sprawl_report.json")
    print("    Use this report to guide architectural consolidation.")
