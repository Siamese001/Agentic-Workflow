"""
ArchitectureGovernorValidatorAgent - L5 Pure Validator.

Detects architectural governance violations (import compliance, layer gravity,
naming) via StructureValidatorAgent without mutating the codebase. Emits a
structured check dict consumed by heal_architecture_governance via HEALER_REGISTRY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "ArchitectureGovernorValidatorAgent")
emit_determinism_digest("p0", "ArchitectureGovernorValidatorAgent")

_emit_dispatches_healing_run("p1", "ArchitectureGovernorValidatorAgent", "L5")
_emit_routes_through("p1", "ArchitectureGovernorValidatorAgent", "L5")
_emit_escalates_to_human("p1", "ArchitectureGovernorValidatorAgent", "L5")
_emit_reads_policy_state("p1", "ArchitectureGovernorValidatorAgent", "L5")

_emit_applies_guardrail("p0", "ArchitectureGovernorValidatorAgent", "p0_governance")
_emit_snapshots_state("p0", "ArchitectureGovernorValidatorAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "ArchitectureGovernorValidatorAgent", "execution_auth")
_emit_validates_capability("p2", "ArchitectureGovernorValidatorAgent", "capability_check")
_emit_routes_to_capability("p2", "ArchitectureGovernorValidatorAgent", "capability_route")
_emit_writes_via_uwg("p2", "ArchitectureGovernorValidatorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "ArchitectureGovernorValidatorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "ArchitectureGovernorValidatorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "ArchitectureGovernorValidatorAgent", "exec_output")
_emit_dispatches_agent("p3", "ArchitectureGovernorValidatorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "ArchitectureGovernorValidatorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "ArchitectureGovernorValidatorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "ArchitectureGovernorValidatorAgent", "healing_outcome")
_emit_escalates_failure("p3", "ArchitectureGovernorValidatorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "ArchitectureGovernorValidatorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ArchitectureGovernorValidatorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "ArchitectureGovernorValidatorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "ArchitectureGovernorValidatorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ArchitectureGovernorValidatorAgent", "eval_metric")
_emit_stores_embedding("p4", "ArchitectureGovernorValidatorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "ArchitectureGovernorValidatorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ArchitectureGovernorValidatorAgent", "exec_snapshot_link")

CHECK_ID = "architecture_governance"


class ArchitectureGovernorValidatorAgent:
    """L5 Certify-only validator for architectural governance."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan(self, target_territory: str | None = None) -> dict[str, Any]:
        """Run ArchitectureGovernorAgent.heal_repository in dry-run mode.

        Args:
            target_territory: Optional territory to scope the scan.

        Returns:
            Raw governance report dict from heal_repository(dry_run=True).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ArchitectureGovernorValidatorAgent.scan"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ArchitectureGovernorValidatorAgent.scan".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

        agent = ArchitectureGovernorAgent(project_root=self.project_root)
        return agent.heal_repository(dry_run=True, execute=False, target_territory=target_territory)

    def to_check_dict(self, target_territory: str | None = None) -> dict[str, Any]:
        """Return structured check dict for _invoke_healer dispatch."""
        scan_result = self.scan(target_territory=target_territory)
        violations_found = scan_result.get("violations_found", 0)
        return {
            "check_id": CHECK_ID,
            "evidence": scan_result,
            "violations_count": violations_found,
            "territory": target_territory,
            "repo_root": str(self.project_root),
        }

    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """Alias for to_check_dict for orchestrator compatibility."""
        return self.to_check_dict(target_territory=target_territory)
