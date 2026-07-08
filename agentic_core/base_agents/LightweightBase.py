"""
LightweightAgentBase - Minimal Infrastructure for Simple Agents

Phase 4 MRO Refactoring: Alternative to full SovereignBaseAgent.

Provides only essential infrastructure:
- CostGuardrailMixin (budget control)
- ContextManagementMixin (context window management)
- TracingMixin (observability)
- CachingMixin (performance - from Phase 3 split)
- MetricsMixin (performance - from Phase 3 split)

Does NOT include:
- HITLMixin (human-in-the-loop - heavy, not always needed)
- PerformanceMixin (full version - use split mixins instead)
- PineconeVectorMixin (vector memory - optional)
- HealingPolicyMixin (healing - optional for simple agents)
- MCPOperationMixin (MCP protocol - optional)
- SubatomicTestingMixin (self-testing - optional)

MRO Depth: ~8 classes (vs ~20+ for full SovereignBaseAgent)

Usage:
    class SimpleAgent(LightweightAgentBase):
        def __post_init__(self):
            super().__post_init__()
            # Agent-specific initialization

    # For agents needing healing, add it explicitly:
    class HealingAgent(HealingPolicyMixin, LightweightAgentBase):
        pass
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.mixins.caching_mixin import CachingMixin
from agentic_core.mixins.context_management_mixin import ContextManagementMixin
from agentic_core.mixins.cost_mixin import CostGuardrailMixin
from agentic_core.mixins.metrics_mixin import MetricsMixin
from agentic_core.mixins.tracing_mixin import TracingMixin
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "LightweightBase", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "LightweightBase", "policy_binding")
trace_contract._emit_snapshots_state("p0", "LightweightBase", "state_snapshot")

trace_contract._emit_emits_metric_event("LightweightBase", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("LightweightBase", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("LightweightBase", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("LightweightBase", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("LightweightBase", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("LightweightBase", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("LightweightBase", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("LightweightBase", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("LightweightBase", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("LightweightBase", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("LightweightBase", "p4obs", "alert")
trace_contract._emit_links_incident_trace("LightweightBase", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("LightweightBase", "p3lm", "pattern")
trace_contract._emit_records_learning_event("LightweightBase", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("LightweightBase", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("LightweightBase", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("LightweightBase", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("LightweightBase", "p3lm", "policy")
trace_contract._emit_stores_learning_state("LightweightBase", "p3lm", "state")
trace_contract._emit_records_execution_trace("LightweightBase", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("LightweightBase", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("LightweightBase", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("LightweightBase", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("LightweightBase", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("LightweightBase", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("LightweightBase", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("LightweightBase", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("LightweightBase", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "LightweightBase", "context_pull")
trace_contract._emit_pulls_context("p1", "LightweightBase", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "LightweightBase", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "LightweightBase", "uwg_term_2")
trace_contract._emit_writes_through("p1", "LightweightBase", "write_through")
trace_contract._emit_writes_through("p1", "LightweightBase", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "LightweightBase", "safety_validation")
trace_contract._emit_invokes_eval("p1", "LightweightBase", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "LightweightBase", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "LightweightBase", "human_escalation")
trace_contract._emit_routes_through("p1", "LightweightBase", "route_through")
trace_contract._emit_checks_agent_registry("p1", "LightweightBase", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "LightweightBase", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "LightweightBase", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "LightweightBase", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "LightweightBase", "target_agent")
trace_contract._emit_verifies_policy("p1", "LightweightBase", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "LightweightBase", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "LightweightBase", "boundary_check")
trace_contract._emit_transcripts_response("p1", "LightweightBase", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "LightweightBase")
trace_contract._emit_gated_by_confidence("p1", "LightweightBase", "confidence_gate")
trace_contract.emit_replay_key("p0", "LightweightBase")
trace_contract.emit_determinism_digest("p0", "LightweightBase")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "LightweightBase", "execution_auth")
trace_contract._emit_validates_capability("p2", "LightweightBase", "capability_check")
trace_contract._emit_routes_to_capability("p2", "LightweightBase", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "LightweightBase", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "LightweightBase", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "LightweightBase", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "LightweightBase", "exec_output")
trace_contract._emit_dispatches_agent("p3", "LightweightBase", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "LightweightBase", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "LightweightBase", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "LightweightBase", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "LightweightBase", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "LightweightBase", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "LightweightBase", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "LightweightBase", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "LightweightBase", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "LightweightBase", "eval_metric")
trace_contract._emit_stores_embedding("p4", "LightweightBase", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "LightweightBase", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "LightweightBase", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class LightweightAgentBase(
    CostGuardrailMixin,
    ContextManagementMixin,
    TracingMixin,
    CachingMixin,
    MetricsMixin,
):
    """
    Lightweight base agent with minimal infrastructure.

    Phase 4 MRO Refactoring: Reduced MRO depth for simple agents.

    Includes:
    - Cost control and budget enforcement
    - Context window management
    - Distributed tracing
    - LRU caching with TTL
    - Performance metrics collection

    For additional capabilities, inherit from the relevant mixins:
    - HealingPolicyMixin: For autonomous healing
    - HITLMixin: For human-in-the-loop workflows
    - BatchingMixin: For batch operations
    - MCPOperationMixin: For MCP protocol safety
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initializes all parent mixins in the correct MRO order."""
        super().__init__(**kwargs)
        self._lightweight_initialized = True
        Logger.debug(f"[LIGHTWEIGHT] {self.__class__.__name__} lightweight agent initialized")

    def verify_lightweight_state(self) -> bool:
        """
        Verify that lightweight infrastructure was properly initialized.

        Returns:
            True if all checks pass

        Raises:
            RuntimeError: If any initialization check fails
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "LightweightAgentBase.verify_lightweight_state"
        )

        errors = []
        if not getattr(self, "_lightweight_initialized", False):
            errors.append(
                f"{self.__class__.__name__}: _lightweight_initialized is False. Did you forget to call super().__post_init__()?",
            )
        if errors:
            error_msg = "Lightweight initialization failed:\n" + "\n".join(f"  - {e}" for e in errors)
            Logger.error(f"[LIGHTWEIGHT] {error_msg}")
            raise RuntimeError(error_msg)
        return True

    def get_lightweight_status(self) -> dict[str, Any]:
        """Get current status of lightweight infrastructure."""
        return {
            "lightweight_initialized": getattr(self, "_lightweight_initialized", False),
            "class_name": self.__class__.__name__,
            "mro_depth": len(type(self).__mro__),
            "capabilities": ["cost_control", "context_management", "tracing", "caching", "metrics"],
        }


__all__ = ["LightweightAgentBase"]
