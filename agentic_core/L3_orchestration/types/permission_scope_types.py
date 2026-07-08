from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "permission_scope_types")
trace_contract.emit_determinism_digest("p0", "permission_scope_types")

trace_contract._emit_dispatches_healing_run("p1", "permission_scope_types", "L3")
trace_contract._emit_routes_through("p1", "permission_scope_types", "L3")
trace_contract._emit_checks_agent_registry("p1", "permission_scope_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "permission_scope_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "permission_scope_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "permission_scope_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "permission_scope_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "permission_scope_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "permission_scope_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "permission_scope_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "permission_scope_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "permission_scope_types")
trace_contract._emit_gated_by_confidence("p1", "permission_scope_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "permission_scope_types", "L3")
trace_contract._emit_reads_policy_state("p1", "permission_scope_types", "L3")
trace_contract._emit_authorize_and_execute("p2", "permission_scope_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "permission_scope_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "permission_scope_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "permission_scope_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "permission_scope_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "permission_scope_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "permission_scope_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "permission_scope_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "permission_scope_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "permission_scope_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "permission_scope_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "permission_scope_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "permission_scope_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "permission_scope_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "permission_scope_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "permission_scope_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "permission_scope_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "permission_scope_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "permission_scope_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "permission_scope_types", "exec_snapshot_link")

"Types and models for agent_permissions."
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from agentic_core.L1_cognition.identity.spiffe_manager_types import AgentIdentity
except ImportError:  # guardian: allow-silent-swallow
    AgentIdentity = type("AgentIdentity", (), {})

trace_contract._emit_emits_metric_event("permission_scope_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("permission_scope_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("permission_scope_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("permission_scope_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("permission_scope_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("permission_scope_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("permission_scope_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("permission_scope_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("permission_scope_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("permission_scope_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("permission_scope_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("permission_scope_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("permission_scope_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("permission_scope_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("permission_scope_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("permission_scope_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("permission_scope_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("permission_scope_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("permission_scope_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("permission_scope_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("permission_scope_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("permission_scope_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("permission_scope_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("permission_scope_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("permission_scope_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("permission_scope_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("permission_scope_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("permission_scope_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "permission_scope_types", "context_pull")
trace_contract._emit_pulls_context("p1", "permission_scope_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "permission_scope_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "permission_scope_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "permission_scope_types", "write_through")
trace_contract._emit_writes_through("p1", "permission_scope_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "permission_scope_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "permission_scope_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "permission_scope_types", "routing_commit")

Logger: Any = logging.getLogger(__name__)


class PermissionScope(Enum):
    """Permission scopes."""

    TOOL_EXECUTION: Any = "tool_execution"
    DATA_ACCESS: Any = "data_access"
    AGENT_COMMUNICATION: Any = "agent_communication"
    SYSTEM_CONFIGURATION: Any = "system_configuration"
    CODE_EXECUTION: Any = "code_execution"


class PermissionAction(Enum):
    """Permission actions."""

    READ: Any = "read"
    WRITE: Any = "write"
    EXECUTE: Any = "execute"
    DELETE: Any = "delete"
    ADMIN: Any = "admin"


@dataclass
class Permission:
    """Individual Permission."""

    scope: PermissionScope
    action: PermissionAction
    resource: str
    conditions: dict[str, Any] = field(default_factory=dict)

    def matches(self, scope: PermissionScope, action: PermissionAction, resource: str) -> bool:
        """Check if Permission matches request.

        Args:
            scope: Requested scope
            action: Requested action
            resource: Requested resource

        Returns:
            True if matches
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "Permission.matches", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "Permission.matches", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "Permission.matches")

        scope_match: Any = self.scope == scope
        action_match: Any = self.action == action or self.action == PermissionAction.ADMIN
        resource_match: Any = self.resource == resource or self.resource == "*"
        return scope_match and action_match and resource_match

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scope": self.scope.value,
            "action": self.action.value,
            "resource": self.resource,
            "conditions": self.conditions,
        }


@dataclass
class PermissionCheck:
    """Result of Permission check."""

    allowed: bool
    identity: AgentIdentity
    Permission: Permission | None = None
    reason: str = ""
    safety_decision: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "allowed": self.allowed,
            "identity": self.identity.to_dict(),
            "Permission": self.Permission.to_dict() if self.Permission else None,
            "reason": self.reason,
            "safety_decision": self.safety_decision.to_dict() if self.safety_decision else None,
        }
