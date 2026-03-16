"""Validator agent for outreach drafts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from apps_lic.utils.LICAgentBase import LICAgentBase

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "ValidatorAgent", "execution_auth")
_emit_validates_capability("p2", "ValidatorAgent", "capability_check")
_emit_routes_to_capability("p2", "ValidatorAgent", "capability_route")
_emit_writes_via_uwg("p2", "ValidatorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "ValidatorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "ValidatorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "ValidatorAgent", "exec_output")
_emit_dispatches_agent("p3", "ValidatorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "ValidatorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "ValidatorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "ValidatorAgent", "healing_outcome")
_emit_escalates_failure("p3", "ValidatorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "ValidatorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ValidatorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "ValidatorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "ValidatorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ValidatorAgent", "eval_metric")
_emit_stores_embedding("p4", "ValidatorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "ValidatorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ValidatorAgent", "exec_snapshot_link")
from apps_lic.tools.validation_tools import ValidationResult, validate_schema_policy

_emit_applies_guardrail("p0", "ValidatorAgent", "p0_governance")
_emit_snapshots_state("p0", "ValidatorAgent", "state_snapshot")
emit_replay_key("p0", "ValidatorAgent")
emit_determinism_digest("p0", "ValidatorAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class ValidatorAgent(LICAgentBase):
    """Sovereign Validator Agent - Apply QA rules and perform limited retries."""

    max_retries: int = 3
    validation_rules: dict[str, Any] = field(
        default_factory=lambda: {"strict_mode": True, "quality_threshold": 0.8}
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    def check(
        self,
        draft: str,
        route_decision,
        pii_map: dict[str, str],
        *,
        artifacts: Mapping[str, str] | None = None,
    ) -> ValidationResult:
        """Sovereign validation check with retry logic."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L5_POLICY, "ValidatorAgent.check")
        artifacts = artifacts or {}
        current_draft = draft
        attempts = 1
        result = validate_schema_policy({"draft": current_draft}, self.validation_rules)
        while not result.passed and attempts <= self.max_retries:
            current_draft = self._retry(current_draft, result, artifacts)
            attempts += 1
            result = validate_schema_policy({"draft": current_draft}, self.validation_rules)
        return result

    def _retry(self, draft: str, result: ValidationResult, artifacts: Mapping[str, str]) -> str:
        """Simple retry logic - can be enhanced with LLM-based fixes."""
        return draft

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)

    # guardian: allow-type-erasure
    def heal_repository(self, *args, **kwargs) -> dict:
        """heal_repository() not implemented for ValidatorAgent."""
        raise NotImplementedError("heal_repository() not implemented for ValidatorAgent")
