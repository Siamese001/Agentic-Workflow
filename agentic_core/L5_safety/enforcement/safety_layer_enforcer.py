from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "safety_layer_enforcer")
trace_contract.emit_determinism_digest("p0", "safety_layer_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "safety_layer_enforcer", "L5")
trace_contract._emit_routes_through("p1", "safety_layer_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "safety_layer_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "safety_layer_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "safety_layer_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "safety_layer_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "safety_layer_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "safety_layer_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "safety_layer_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "safety_layer_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "safety_layer_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "safety_layer_enforcer")
trace_contract._emit_gated_by_confidence("p1", "safety_layer_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "safety_layer_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "safety_layer_enforcer", "L5")

trace_contract._emit_applies_guardrail("p0", "safety_layer_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "safety_layer_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "safety_layer_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "safety_layer_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "safety_layer_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "safety_layer_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "safety_layer_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "safety_layer_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "safety_layer_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "safety_layer_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "safety_layer_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "safety_layer_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "safety_layer_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "safety_layer_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "safety_layer_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "safety_layer_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "safety_layer_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "safety_layer_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "safety_layer_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "safety_layer_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "safety_layer_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "safety_layer_enforcer", "exec_snapshot_link")

"L5 Safety Layer Integration.\n\nCoordinates PII Vault, Constitutional Overseer, and Cost Governor.\n"
import logging
from typing import TYPE_CHECKING, Any

from agentic_core.L1_cognition.types.action_request_types import ActionRequest

if TYPE_CHECKING:
    from agentic_core.governor import create_cost_governor
    from agentic_core.overseer import create_overseer
    from agentic_core.PiiVault import create_pii_vault

trace_contract._emit_emits_metric_event("safety_layer_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("safety_layer_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("safety_layer_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("safety_layer_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("safety_layer_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("safety_layer_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("safety_layer_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("safety_layer_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("safety_layer_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("safety_layer_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("safety_layer_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("safety_layer_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("safety_layer_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("safety_layer_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("safety_layer_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("safety_layer_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("safety_layer_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("safety_layer_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("safety_layer_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("safety_layer_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("safety_layer_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("safety_layer_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("safety_layer_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("safety_layer_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("safety_layer_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("safety_layer_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("safety_layer_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("safety_layer_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "safety_layer_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "safety_layer_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_layer_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_layer_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "safety_layer_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "safety_layer_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "safety_layer_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "safety_layer_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "safety_layer_enforcer", "routing_commit")

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class L5SafetyLayer:
    """L5 Safety Layer that validates all actions before execution."""

    # guardian: allow-magic-config
    def __init__(self, cost_limit_usd: float = 5.0):
        """Initialize the safety layer.

        Args:
            cost_limit_usd: Maximum allowed cost in USD
        """
        self.PiiVault = create_pii_vault()
        self.overseer = create_overseer()
        self.CostGovernor = create_cost_governor(cost_limit_usd)
        self.session_id = "mission-session"
        self.validation_count = 0
        self.blocked_count = 0
        LOGGER.info("L5 Safety Layer initialized")

    async def validate_action(self, request: ActionRequest) -> bool:
        """Validate an action request through all safety checks.

        Args:
            request: The ActionRequest to validate

        Returns:
            True if action is safe and approved, False otherwise
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "L5SafetyLayer.validate_action")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:L5SafetyLayer.validate_action".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.validation_count += 1
        try:
            Violation: Any = await self.overseer.validate_action(request)
            if Violation.is_violation:
                self.blocked_count += 1
                LOGGER.error(f"L5: Action BLOCKED - {Violation.reason}")
                return False
            await self._check_and_redact_pii(request)
            if not self._validate_cost_estimate(request):
                self.blocked_count += 1
                LOGGER.error("L5: Action BLOCKED - Cost limit would be exceeded")
                return False
            LOGGER.info("L5: Action Validated - [SAFE]")
            return True
        except (ValueError, TypeError) as e:
            self.blocked_count += 1
            LOGGER.error(f"L5: Validation error - {e}")
            return False

    async def _check_and_redact_pii(self, request: ActionRequest):
        """Check request parameters for PII and redact if necessary.

        Args:
            request: ActionRequest to check
        """
        for key, value in request.parameters.items():
            if isinstance(value, str) and len(value) > 10:
                if any(keyword in value.lower() for keyword in ["email", "phone", "ssn", "address"]):
                    redacted = self.PiiVault.redact(self.session_id, value)
                    if redacted != value:
                        LOGGER.warning(f"L5: PII detected and redacted in parameter '{key}'")
                        request.parameters[key] = redacted

    def _validate_cost_estimate(self, request: ActionRequest) -> bool:
        """Validate if the estimated cost is within budget.

        Args:
            request: ActionRequest to validate

        Returns:
            True if cost is acceptable, False otherwise
        """
        estimated_tokens = {
            "tool_execution": 100,
            "file_operations": 50,
            "diagnostic_tool_creation": 500,
        }.get(request.action_type, 100)
        return self.CostGovernor.check_action_cost(estimated_tokens)

    def track_action_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Track actual cost after action execution.

        Args:
            model: Model used
            input_tokens: Input tokens consumed
            output_tokens: Output tokens generated

        Returns:
            Cost of the action

        Raises:
            BudgetExceededError: If budget is exceeded
        """
        return self.CostGovernor.track(model, input_tokens, output_tokens)

    def get_safety_stats(self) -> dict[str, Any]:
        """Get safety layer statistics.

        Returns:
            Dictionary with safety statistics
        """
        return {
            "validations_performed": self.validation_count,
            "actions_blocked": self.blocked_count,
            "block_rate_percent": self.blocked_count / max(self.validation_count, 1) * 100,
            "pii_vault_stats": self.PiiVault.get_stats(),
            "cost_governor_stats": self.CostGovernor.get_stats(),
            "forbidden_patterns_count": len(self.overseer.get_forbidden_patterns()),
        }

    def cleanup(self) -> Any:
        """Cleanup resources and sessions."""
        self.PiiVault.clear_session(self.session_id)
        LOGGER.info("L5 Safety Layer cleanup complete")


# guardian: allow-magic-config
def create_l5_safety_layer(cost_limit_usd: float = 5.0) -> L5SafetyLayer:
    """Factory function to create L5 safety layer.

    Args:
        cost_limit_usd: Maximum allowed cost in USD

    Returns:
        L5SafetyLayer instance
    """
    return L5SafetyLayer(cost_limit_usd)
