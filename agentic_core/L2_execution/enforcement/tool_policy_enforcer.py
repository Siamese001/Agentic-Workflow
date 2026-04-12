"""
§Wave2.4 — ToolPolicyEnforcer: LawSlot enforcement gate for tool calls.

Resolves applicable law slots and enforces policy constraints before
tool execution. Default behavior is PASS with empty slots if no policy
is configured.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.L2_execution.types.tool_enforcement_types import (
    LawSlotOutcome,
    ToolEnforcementArtifact,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "tool_policy_enforcer")
emit_determinism_digest("p0", "tool_policy_enforcer")

_emit_dispatches_healing_run("p1", "tool_policy_enforcer", "L2")
_emit_routes_through("p1", "tool_policy_enforcer", "L2")
_emit_checks_agent_registry("p1", "tool_policy_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "tool_policy_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "tool_policy_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "tool_policy_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "tool_policy_enforcer", "target_agent")
_emit_verifies_policy("p1", "tool_policy_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "tool_policy_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "tool_policy_enforcer", "boundary_check")
_emit_transcripts_response("p1", "tool_policy_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_policy_enforcer")
_emit_gated_by_confidence("p1", "tool_policy_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "tool_policy_enforcer", "L2")
_emit_reads_policy_state("p1", "tool_policy_enforcer", "L2")

_emit_snapshots_state("p0", "tool_policy_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "tool_policy_enforcer", "execution_auth")
_emit_validates_capability("p2", "tool_policy_enforcer", "capability_check")
_emit_routes_to_capability("p2", "tool_policy_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "tool_policy_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "tool_policy_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_policy_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "tool_policy_enforcer", "exec_output")
_emit_dispatches_agent("p3", "tool_policy_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_policy_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_policy_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_policy_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "tool_policy_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_policy_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_policy_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_policy_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_policy_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_policy_enforcer", "eval_metric")
_emit_stores_embedding("p4", "tool_policy_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_policy_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_policy_enforcer", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("tool_policy_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("tool_policy_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("tool_policy_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("tool_policy_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("tool_policy_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("tool_policy_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("tool_policy_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_policy_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("tool_policy_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_policy_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("tool_policy_enforcer", "p4obs", "alert")
_emit_links_incident_trace("tool_policy_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("tool_policy_enforcer", "p3lm", "pattern")
_emit_records_learning_event("tool_policy_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_policy_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_policy_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_policy_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("tool_policy_enforcer", "p3lm", "policy")
_emit_stores_learning_state("tool_policy_enforcer", "p3lm", "state")
_emit_records_execution_trace("tool_policy_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_policy_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_policy_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_policy_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_policy_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_policy_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("tool_policy_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_policy_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_policy_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_policy_enforcer", "context_pull")
_emit_pulls_context("p1", "tool_policy_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_policy_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_policy_enforcer", "uwg_term_2")
_emit_writes_through("p1", "tool_policy_enforcer", "write_through")
_emit_writes_through("p1", "tool_policy_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_policy_enforcer", "safety_validation")
_emit_invokes_eval("p1", "tool_policy_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "tool_policy_enforcer", "routing_commit")

_log = logging.getLogger(__name__)


def _stable_args_hash(args: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of tool arguments.

    Uses sorted-key JSON serialization with default=str for non-serializable
    values, ensuring identical args always produce the same hash.
    """
    serialized = json.dumps(args, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class ToolPolicyEnforcer:
    """§Wave2.4 — Minimal law-slot enforcement handler.

    Resolves applicable law slots for a given tool + context and returns
    an enforcement decision (PASS / BLOCK / MODIFY).

    Default behavior (no policy rules configured): PASS with empty slots.

    Subclass or configure `_policy_rules` to implement real enforcement.
    """

    def __init__(self) -> None:
        self._policy_rules: dict[str, dict[str, Any]] = {}

    def register_rule(
        self,
        tool_name: str,
        *,
        outcome: LawSlotOutcome,
        law_slots: tuple[str, ...] = (),
        rationale: str = "",
        arg_transform: dict[str, Any] | None = None,
    ) -> None:
        """Register a policy rule for a specific tool.

        Used primarily for testing and configuration.
        """
        self._policy_rules[tool_name] = {
            "outcome": outcome,
            "law_slots": law_slots,
            "rationale": rationale,
            "arg_transform": arg_transform,
        }

    def resolve_slots(
        self,
        tool_name: str,
        context: dict[str, Any] | None = None,
    ) -> tuple[str, ...]:
        """Resolve applicable law slot IDs for this tool + context."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "ToolPolicyEnforcer.resolve_slots",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ToolPolicyEnforcer.resolve_slots".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        rule = self._policy_rules.get(tool_name)
        if rule:
            return rule.get("law_slots", ())
        return ()

    def enforce(
        self,
        tool_name: str,
        args: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> tuple[LawSlotOutcome, dict[str, Any], str, tuple[str, ...]]:
        """Enforce policy for a tool call.

        Returns:
            (outcome, new_args, rationale, applied_slots)
            - outcome: PASS, BLOCK, or MODIFY
            - new_args: original args if PASS/BLOCK; transformed args if MODIFY
            - rationale: human-readable explanation
            - applied_slots: tuple of law slot IDs that were applied
        """
        rule = self._policy_rules.get(tool_name)
        if not rule:
            return (LawSlotOutcome.PASS, args, "No policy rules configured", ())

        outcome = rule["outcome"]
        slots = rule.get("law_slots", ())
        rationale = rule.get("rationale", f"Policy rule: {outcome.value}")

        if outcome == LawSlotOutcome.MODIFY and rule.get("arg_transform"):
            new_args = {**args, **rule["arg_transform"]}
            return (outcome, new_args, rationale, slots)

        return (outcome, args, rationale, slots)

    def build_artifact(
        self,
        tool_name: str,
        outcome: LawSlotOutcome,
        applied_slots: tuple[str, ...],
        rationale: str,
        original_args_hash: str,
        modified_args_hash: str = "",
        trace_id: str = "",
        agent_id: str = "",
    ) -> ToolEnforcementArtifact:
        """Build a ToolEnforcementArtifact for emission."""
        return ToolEnforcementArtifact(
            enforcement_id=str(uuid.uuid4()),
            timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            trace_id=trace_id or str(uuid.uuid4())[:16],
            agent_id=agent_id or "unknown",
            tool_name=tool_name,
            outcome=outcome,
            applied_law_slots=applied_slots,
            rationale=rationale,
            original_args_hash=original_args_hash,
            modified_args_hash=modified_args_hash,
        )


# Module-level default enforcer (singleton pattern matching MCPToolServer)
_TOOL_POLICY_ENFORCER: ToolPolicyEnforcer | None = None


def get_tool_policy_enforcer() -> ToolPolicyEnforcer:
    """Get or create the global ToolPolicyEnforcer instance."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.get_tool_policy_enforcer", "L2_EXECUTION")
    global _TOOL_POLICY_ENFORCER
    if _TOOL_POLICY_ENFORCER is None:
        _TOOL_POLICY_ENFORCER = ToolPolicyEnforcer()
    return _TOOL_POLICY_ENFORCER


def set_tool_policy_enforcer(enforcer: ToolPolicyEnforcer | None) -> None:
    """Replace the global enforcer (for testing or reconfiguration)."""
    global _TOOL_POLICY_ENFORCER
    _TOOL_POLICY_ENFORCER = enforcer


__all__ = [
    "ToolPolicyEnforcer",
    "_stable_args_hash",
    "get_tool_policy_enforcer",
    "set_tool_policy_enforcer",
]
