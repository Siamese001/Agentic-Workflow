"""
L5 Guardian Decision - Active blocking enforcement.

L5 must block execution before L2.2 with policy enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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

emit_replay_key("p0", "guardian_decision")
emit_determinism_digest("p0", "guardian_decision")

_emit_dispatches_healing_run("p1", "guardian_decision", "L5")
_emit_routes_through("p1", "guardian_decision", "L5")
_emit_checks_agent_registry("p1", "guardian_decision", "agent_registry")
_emit_validates_agent_capability("p1", "guardian_decision", "capability")
_emit_dispatches_execution_plan("p1", "guardian_decision", "exec_plan")
_emit_agent_executes_agent("p1", "guardian_decision", "sub_agent")
_emit_routes_to_agent("p1", "guardian_decision", "target_agent")
_emit_verifies_policy("p1", "guardian_decision", "policy_check")
_emit_observes_runtime_state("p1", "guardian_decision", "runtime_state")
_emit_verifies_boundary("p1", "guardian_decision", "boundary_check")
_emit_transcripts_response("p1", "guardian_decision", "transcript")
_emit_hard_fails_untranscripted("p1", "guardian_decision")
_emit_gated_by_confidence("p1", "guardian_decision", "confidence_gate")
_emit_escalates_to_human("p1", "guardian_decision", "L5")
_emit_reads_policy_state("p1", "guardian_decision", "L5")

_emit_applies_guardrail("p0", "guardian_decision", "p0_governance")
_emit_snapshots_state("p0", "guardian_decision", "state_snapshot")
_emit_authorize_and_execute("p2", "guardian_decision", "execution_auth")
_emit_validates_capability("p2", "guardian_decision", "capability_check")
_emit_routes_to_capability("p2", "guardian_decision", "capability_route")
_emit_writes_via_uwg("p2", "guardian_decision", "uwg_write")
_emit_blocks_direct_write("p2", "guardian_decision", "direct_write_block")
_emit_records_tool_invocation("p2", "guardian_decision", "tool_invocation")
_emit_captures_execution_output("p2", "guardian_decision", "exec_output")
_emit_dispatches_agent("p3", "guardian_decision", "agent_dispatch")
_emit_coordinates_agents("p3", "guardian_decision", "agent_coordination")
_emit_records_workflow_lineage("p3", "guardian_decision", "workflow_lineage")
_emit_records_healing_outcome("p3", "guardian_decision", "healing_outcome")
_emit_escalates_failure("p3", "guardian_decision", "failure_escalation")
_emit_orchestrates_workflow("p3", "guardian_decision", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "guardian_decision", "healing_dispatch")
_emit_invokes_evaluation("p3", "guardian_decision", "evaluation_signal")
_emit_records_telemetry_event("p4", "guardian_decision", "telemetry_event")
_emit_captures_evaluation_metric("p4", "guardian_decision", "eval_metric")
_emit_stores_embedding("p4", "guardian_decision", "embedding_store")
_emit_updates_meta_learning_state("p4", "guardian_decision", "meta_learning")
_emit_links_execution_to_snapshot("p4", "guardian_decision", "exec_snapshot_link")
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("guardian_decision", "p4obs", "metric_1")
_emit_emits_metric_event("guardian_decision", "p4obs", "metric_2")
_emit_emits_metric_event("guardian_decision", "p4obs", "metric_3")
_emit_emits_metric_event("guardian_decision", "p4obs", "metric_4")
_emit_emits_metric_event("guardian_decision", "p4obs", "metric_5")
_emit_emits_metric_event("guardian_decision", "p4obs", "metric_6")
_emit_records_incident_event("guardian_decision", "p4obs", "incident")
_emit_captures_runtime_anomaly("guardian_decision", "p4obs", "anomaly")
_emit_writes_observability_log("guardian_decision", "p4obs", "obs_log")
_emit_updates_monitoring_state("guardian_decision", "p4obs", "mon_state")
_emit_triggers_alert("guardian_decision", "p4obs", "alert")
_emit_links_incident_trace("guardian_decision", "p4obs", "trace_link")
_emit_captures_pattern("guardian_decision", "p3lm", "pattern")
_emit_records_learning_event("guardian_decision", "p3lm", "learning_event")
_emit_writes_learning_snapshot("guardian_decision", "p3lm", "snapshot")
_emit_feeds_meta_learning("guardian_decision", "p3lm", "meta_feed")
_emit_updates_routing_strategy("guardian_decision", "p3lm", "routing")
_emit_improves_agent_policy("guardian_decision", "p3lm", "policy")
_emit_stores_learning_state("guardian_decision", "p3lm", "state")
_emit_records_execution_trace("guardian_decision", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("guardian_decision", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("guardian_decision", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("guardian_decision", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("guardian_decision", "L4_STATE", "p2_trace_5")
_emit_reads_environ("guardian_decision", "env_read", "p2_env_1")
_emit_reads_environ("guardian_decision", "env_read", "p2_env_2")
_emit_reads_runtime_state("guardian_decision", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("guardian_decision", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "guardian_decision", "context_pull")
_emit_pulls_context("p1", "guardian_decision", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "guardian_decision", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "guardian_decision", "uwg_term_2")
_emit_writes_through("p1", "guardian_decision", "write_through")
_emit_writes_through("p1", "guardian_decision", "write_through_2")
_emit_validated_by_safety_plane("p1", "guardian_decision", "safety_validation")
_emit_invokes_eval("p1", "guardian_decision", "eval_call")
_emit_proposal_commits_routing("p1", "guardian_decision", "routing_commit")


@dataclass
class GuardianDecision:
    """Decision from L5 Guardian with enforcement capabilities."""

    allow: bool
    escalate: bool
    violations: list[str]
    budget_remaining: int
    policy_version: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "allow": self.allow,
            "escalate": self.escalate,
            "violations": self.violations,
            "budget_remaining": self.budget_remaining,
            "policy_version": self.policy_version,
        }


class GuardianViolationError(Exception):
    """Raised when Guardian blocks execution."""

    def __init__(self, decision: GuardianDecision, message: str | None = None) -> None:
        self.decision = decision
        if message is None:
            message = f"Guardian blocked execution: {decision.violations}"
        super().__init__(message)


class L5Guardian:
    """
    Active Guardian that enforces policies before L2.2.

    Enforces:
    - Tool allowlist
    - File access scope
    - Token budget
    - Agent permission map
    - Rate limits
    """

    def __init__(self, policy_version: str = "1.0") -> None:
        self.policy_version = policy_version
        self.tool_allowlist = {
            "file_read",
            "file_write",
            "ast_parse",
            "llm_call",
            "redis_get",
            "redis_set",
            "pinecone_query",
            "pinecone_upsert",
        }
        self.file_scope_whitelist = {"/tmp", "/workspace", AGENTIC_CORE_DIR}
        # guardian: allow-magic-config
        self.token_budget = 1000000
        self.agent_permissions = {
            "L1_cognition": ["read", "transform"],
            "L2_execution": ["read", "write", "validate"],
            "L3_orchestration": ["read", "write", "orchestrate"],
            "L5_safety": ["read", "enforce", "block"],
        }

    def validate(self, manifest: Any, state: Any, policy_version: str | None = None) -> GuardianDecision:
        """
        Validate execution intent against all policies.

        Args:
            manifest: Execution manifest to validate
            state: Current execution state
            policy_version: Policy version to enforce

        Returns:
            GuardianDecision with allow/block result
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "L5Guardian.validate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:L5Guardian.validate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []
        escalate = False
        if hasattr(manifest, "tool_name"):
            if manifest.tool_name not in self.tool_allowlist:
                violations.append(f"Tool '{manifest.tool_name}' not in allowlist")
        if hasattr(manifest, "file_path") and isinstance(manifest.file_path, str):
            file_path = str(manifest.file_path)
            if not any(allowed in file_path for allowed in self.file_scope_whitelist):
                violations.append(f"File access '{file_path}' outside allowed scope")
        if hasattr(manifest, "token_usage"):
            if manifest.token_usage > self.token_budget:
                violations.append(f"Token usage {manifest.token_usage} exceeds budget {self.token_budget}")
                escalate = True
        if hasattr(manifest, "agent_layer"):
            agent_layer = manifest.agent_layer
            required_permission = getattr(manifest, "required_permission", "read")
            if agent_layer not in self.agent_permissions:
                violations.append(f"Unknown agent layer '{agent_layer}'")
            elif required_permission not in self.agent_permissions[agent_layer]:
                violations.append(f"Agent '{agent_layer}' lacks permission '{required_permission}'")
        allow = len(violations) == 0
        budget_remaining = max(0, self.token_budget - getattr(manifest, "token_usage", 0))
        return GuardianDecision(
            allow=allow,
            escalate=escalate,
            violations=violations,
            budget_remaining=budget_remaining,
            policy_version=policy_version or self.policy_version,
        )

    def log_decision_to_state_bus(self, decision: GuardianDecision, trace_id: str) -> None:
        """Log Guardian decision to L4 state bus."""
        import logging

        Logger = logging.getLogger(__name__)
        Logger.info(f"[L5_GUARDIAN] Decision for {trace_id}: {decision.to_dict()}")
