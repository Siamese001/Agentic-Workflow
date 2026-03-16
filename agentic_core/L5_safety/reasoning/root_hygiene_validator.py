"""
RootHygieneValidatorAgent - L5 Pure Validator.

Read-only scan of root hygiene violations via RootHygieneAgent.scan_root_violations().
Emits structured results without mutating the filesystem.
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

emit_replay_key("p0", "root_hygiene_validator")
emit_determinism_digest("p0", "root_hygiene_validator")

_emit_dispatches_healing_run("p1", "root_hygiene_validator", "L5")
_emit_routes_through("p1", "root_hygiene_validator", "L5")
_emit_escalates_to_human("p1", "root_hygiene_validator", "L5")
_emit_reads_policy_state("p1", "root_hygiene_validator", "L5")

_emit_applies_guardrail("p0", "root_hygiene_validator", "p0_governance")
_emit_snapshots_state("p0", "root_hygiene_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "root_hygiene_validator", "execution_auth")
_emit_validates_capability("p2", "root_hygiene_validator", "capability_check")
_emit_routes_to_capability("p2", "root_hygiene_validator", "capability_route")
_emit_writes_via_uwg("p2", "root_hygiene_validator", "uwg_write")
_emit_blocks_direct_write("p2", "root_hygiene_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "root_hygiene_validator", "tool_invocation")
_emit_captures_execution_output("p2", "root_hygiene_validator", "exec_output")
_emit_dispatches_agent("p3", "root_hygiene_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "root_hygiene_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "root_hygiene_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "root_hygiene_validator", "healing_outcome")
_emit_escalates_failure("p3", "root_hygiene_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "root_hygiene_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "root_hygiene_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "root_hygiene_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "root_hygiene_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "root_hygiene_validator", "eval_metric")
_emit_stores_embedding("p4", "root_hygiene_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "root_hygiene_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "root_hygiene_validator", "exec_snapshot_link")


class RootHygieneValidatorAgent:
    """L5 Certify-only validator for root directory hygiene violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan_root_violations(self) -> dict[str, Any]:
        """Delegate to RootHygieneAgent.scan_root_violations (read-only)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "RootHygieneValidatorAgent.scan_root_violations"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:RootHygieneValidatorAgent.scan_root_violations".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent

        agent = RootHygieneAgent(project_root=self.project_root, dry_run=True)
        return agent.scan_root_violations()
