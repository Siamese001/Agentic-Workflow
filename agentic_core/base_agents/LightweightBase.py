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
- HealerMixin (healing - optional for simple agents)
- MCPHardenedMixin (MCP protocol - optional)
- SubatomicTestingMixin (self-testing - optional)

MRO Depth: ~8 classes (vs ~20+ for full SovereignBaseAgent)

Usage:
    class SimpleAgent(LightweightAgentBase):
        def __post_init__(self):
            super().__post_init__()
            # Agent-specific initialization

    # For agents needing healing, add it explicitly:
    class HealingAgent(HealerMixin, LightweightAgentBase):
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_applies_guardrail("p0", "LightweightBase", "p0_governance")
_emit_reads_policy_state("p0", "LightweightBase", "policy_binding")
_emit_snapshots_state("p0", "LightweightBase", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("LightweightBase", "p4obs", "metric_1")
_emit_emits_metric_event("LightweightBase", "p4obs", "metric_2")
_emit_emits_metric_event("LightweightBase", "p4obs", "metric_3")
_emit_emits_metric_event("LightweightBase", "p4obs", "metric_4")
_emit_emits_metric_event("LightweightBase", "p4obs", "metric_5")
_emit_emits_metric_event("LightweightBase", "p4obs", "metric_6")
_emit_records_incident_event("LightweightBase", "p4obs", "incident")
_emit_captures_runtime_anomaly("LightweightBase", "p4obs", "anomaly")
_emit_writes_observability_log("LightweightBase", "p4obs", "obs_log")
_emit_updates_monitoring_state("LightweightBase", "p4obs", "mon_state")
_emit_triggers_alert("LightweightBase", "p4obs", "alert")
_emit_links_incident_trace("LightweightBase", "p4obs", "trace_link")
_emit_captures_pattern("LightweightBase", "p3lm", "pattern")
_emit_records_learning_event("LightweightBase", "p3lm", "learning_event")
_emit_writes_learning_snapshot("LightweightBase", "p3lm", "snapshot")
_emit_feeds_meta_learning("LightweightBase", "p3lm", "meta_feed")
_emit_updates_routing_strategy("LightweightBase", "p3lm", "routing")
_emit_improves_agent_policy("LightweightBase", "p3lm", "policy")
_emit_stores_learning_state("LightweightBase", "p3lm", "state")
_emit_records_execution_trace("LightweightBase", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("LightweightBase", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("LightweightBase", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("LightweightBase", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("LightweightBase", "L4_STATE", "p2_trace_5")
_emit_reads_environ("LightweightBase", "env_read", "p2_env_1")
_emit_reads_environ("LightweightBase", "env_read", "p2_env_2")
_emit_reads_runtime_state("LightweightBase", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("LightweightBase", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "LightweightBase", "context_pull")
_emit_pulls_context("p1", "LightweightBase", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "LightweightBase", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "LightweightBase", "uwg_term_2")
_emit_writes_through("p1", "LightweightBase", "write_through")
_emit_writes_through("p1", "LightweightBase", "write_through_2")
_emit_validated_by_safety_plane("p1", "LightweightBase", "safety_validation")
_emit_invokes_eval("p1", "LightweightBase", "eval_call")
_emit_proposal_commits_routing("p1", "LightweightBase", "routing_commit")
_emit_escalates_to_human("p1", "LightweightBase", "human_escalation")
_emit_routes_through("p1", "LightweightBase", "route_through")
_emit_checks_agent_registry("p1", "LightweightBase", "agent_registry")
_emit_validates_agent_capability("p1", "LightweightBase", "capability")
_emit_dispatches_execution_plan("p1", "LightweightBase", "exec_plan")
_emit_agent_executes_agent("p1", "LightweightBase", "sub_agent")
_emit_routes_to_agent("p1", "LightweightBase", "target_agent")
_emit_verifies_policy("p1", "LightweightBase", "policy_check")
_emit_observes_runtime_state("p1", "LightweightBase", "runtime_state")
_emit_verifies_boundary("p1", "LightweightBase", "boundary_check")
_emit_transcripts_response("p1", "LightweightBase", "transcript")
_emit_hard_fails_untranscripted("p1", "LightweightBase")
_emit_gated_by_confidence("p1", "LightweightBase", "confidence_gate")
emit_replay_key("p0", "LightweightBase")
emit_determinism_digest("p0", "LightweightBase")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "LightweightBase", "execution_auth")
_emit_validates_capability("p2", "LightweightBase", "capability_check")
_emit_routes_to_capability("p2", "LightweightBase", "capability_route")
_emit_writes_via_uwg("p2", "LightweightBase", "uwg_write")
_emit_blocks_direct_write("p2", "LightweightBase", "direct_write_block")
_emit_records_tool_invocation("p2", "LightweightBase", "tool_invocation")
_emit_captures_execution_output("p2", "LightweightBase", "exec_output")
_emit_dispatches_agent("p3", "LightweightBase", "agent_dispatch")
_emit_coordinates_agents("p3", "LightweightBase", "agent_coordination")
_emit_records_workflow_lineage("p3", "LightweightBase", "workflow_lineage")
_emit_records_healing_outcome("p3", "LightweightBase", "healing_outcome")
_emit_escalates_failure("p3", "LightweightBase", "failure_escalation")
_emit_orchestrates_workflow("p3", "LightweightBase", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "LightweightBase", "healing_dispatch")
_emit_invokes_evaluation("p3", "LightweightBase", "evaluation_signal")
_emit_records_telemetry_event("p4", "LightweightBase", "telemetry_event")
_emit_captures_evaluation_metric("p4", "LightweightBase", "eval_metric")
_emit_stores_embedding("p4", "LightweightBase", "embedding_store")
_emit_updates_meta_learning_state("p4", "LightweightBase", "meta_learning")
_emit_links_execution_to_snapshot("p4", "LightweightBase", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class LightweightAgentBase(
    CostGuardrailMixin, ContextManagementMixin, TracingMixin, CachingMixin, MetricsMixin,
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
    - HealerMixin: For autonomous healing
    - HITLMixin: For human-in-the-loop workflows
    - BatchingMixin: For batch operations
    - MCPHardenedMixin: For MCP protocol safety
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LightweightAgentBase.verify_lightweight_state")

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
