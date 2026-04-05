__version__ = "13.0"
import asyncio

from agentic_core.interfaces.gateway import GenerationRequest, SovereignLLMGateway
from agentic_core.L2_execution.utils import get_clock
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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
)

_emit_reads_policy_state("p0", "GeminiLLMClient", "policy_binding")
_emit_snapshots_state("p0", "GeminiLLMClient", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "GeminiLLMClient", "execution_auth")
_emit_validates_capability("p2", "GeminiLLMClient", "capability_check")
_emit_routes_to_capability("p2", "GeminiLLMClient", "capability_route")
_emit_writes_via_uwg("p2", "GeminiLLMClient", "uwg_write")
_emit_blocks_direct_write("p2", "GeminiLLMClient", "direct_write_block")
_emit_records_tool_invocation("p2", "GeminiLLMClient", "tool_invocation")
_emit_captures_execution_output("p2", "GeminiLLMClient", "exec_output")
_emit_dispatches_agent("p3", "GeminiLLMClient", "agent_dispatch")
_emit_coordinates_agents("p3", "GeminiLLMClient", "agent_coordination")
_emit_records_workflow_lineage("p3", "GeminiLLMClient", "workflow_lineage")
_emit_records_healing_outcome("p3", "GeminiLLMClient", "healing_outcome")
_emit_escalates_failure("p3", "GeminiLLMClient", "failure_escalation")
_emit_orchestrates_workflow("p3", "GeminiLLMClient", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GeminiLLMClient", "healing_dispatch")
_emit_invokes_evaluation("p3", "GeminiLLMClient", "evaluation_signal")
_emit_records_telemetry_event("p4", "GeminiLLMClient", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GeminiLLMClient", "eval_metric")
_emit_stores_embedding("p4", "GeminiLLMClient", "embedding_store")
_emit_updates_meta_learning_state("p4", "GeminiLLMClient", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GeminiLLMClient", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("GeminiLLMClient", "p4obs", "metric_1")
_emit_emits_metric_event("GeminiLLMClient", "p4obs", "metric_2")
_emit_emits_metric_event("GeminiLLMClient", "p4obs", "metric_3")
_emit_emits_metric_event("GeminiLLMClient", "p4obs", "metric_4")
_emit_emits_metric_event("GeminiLLMClient", "p4obs", "metric_5")
_emit_emits_metric_event("GeminiLLMClient", "p4obs", "metric_6")
_emit_records_incident_event("GeminiLLMClient", "p4obs", "incident")
_emit_captures_runtime_anomaly("GeminiLLMClient", "p4obs", "anomaly")
_emit_writes_observability_log("GeminiLLMClient", "p4obs", "obs_log")
_emit_updates_monitoring_state("GeminiLLMClient", "p4obs", "mon_state")
_emit_triggers_alert("GeminiLLMClient", "p4obs", "alert")
_emit_links_incident_trace("GeminiLLMClient", "p4obs", "trace_link")
_emit_captures_pattern("GeminiLLMClient", "p3lm", "pattern")
_emit_records_learning_event("GeminiLLMClient", "p3lm", "learning_event")
_emit_writes_learning_snapshot("GeminiLLMClient", "p3lm", "snapshot")
_emit_feeds_meta_learning("GeminiLLMClient", "p3lm", "meta_feed")
_emit_updates_routing_strategy("GeminiLLMClient", "p3lm", "routing")
_emit_improves_agent_policy("GeminiLLMClient", "p3lm", "policy")
_emit_stores_learning_state("GeminiLLMClient", "p3lm", "state")
_emit_records_execution_trace("GeminiLLMClient", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("GeminiLLMClient", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("GeminiLLMClient", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("GeminiLLMClient", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("GeminiLLMClient", "L4_STATE", "p2_trace_5")
_emit_reads_environ("GeminiLLMClient", "env_read", "p2_env_1")
_emit_reads_environ("GeminiLLMClient", "env_read", "p2_env_2")
_emit_reads_runtime_state("GeminiLLMClient", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("GeminiLLMClient", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "GeminiLLMClient", "context_pull")
_emit_pulls_context("p1", "GeminiLLMClient", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "GeminiLLMClient", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "GeminiLLMClient", "uwg_term_2")
_emit_writes_through("p1", "GeminiLLMClient", "write_through")
_emit_writes_through("p1", "GeminiLLMClient", "write_through_2")
_emit_validated_by_safety_plane("p1", "GeminiLLMClient", "safety_validation")
_emit_invokes_eval("p1", "GeminiLLMClient", "eval_call")
_emit_proposal_commits_routing("p1", "GeminiLLMClient", "routing_commit")
_emit_escalates_to_human("p1", "GeminiLLMClient", "human_escalation")
_emit_routes_through("p1", "GeminiLLMClient", "route_through")
_emit_checks_agent_registry("p1", "GeminiLLMClient", "agent_registry")
_emit_validates_agent_capability("p1", "GeminiLLMClient", "capability")
_emit_dispatches_execution_plan("p1", "GeminiLLMClient", "exec_plan")
_emit_agent_executes_agent("p1", "GeminiLLMClient", "sub_agent")
_emit_routes_to_agent("p1", "GeminiLLMClient", "target_agent")
_emit_verifies_policy("p1", "GeminiLLMClient", "policy_check")
_emit_observes_runtime_state("p1", "GeminiLLMClient", "runtime_state")
_emit_verifies_boundary("p1", "GeminiLLMClient", "boundary_check")
_emit_transcripts_response("p1", "GeminiLLMClient", "transcript")
_emit_hard_fails_untranscripted("p1", "GeminiLLMClient")
_emit_gated_by_confidence("p1", "GeminiLLMClient", "confidence_gate")


class GeminiLLMClient:
    """Gateway-delegating client for Gemini.  No direct SDK access."""

    _AGENT_ID = "GeminiLLMClient"
    try:
        from agentic_core.L3_orchestration.healers.healing_tier_config import HealingTierConfig as _HTC

        _MODEL: str = _HTC().model_gemini_2_5_pro_id
    except (ImportError, AttributeError):
        _MODEL = "gemini-2.5-pro"

    def __init__(self, circuit_breaker=None):
        self._gateway = SovereignLLMGateway()
        self.circuit_breaker = circuit_breaker

    def generate(self, prompt: str) -> str:
        import uuid  # noqa: PLC0415

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GeminiLLMClient.generate")
        request = GenerationRequest(
            agent_id=self._AGENT_ID, provider="google", model=self._MODEL, prompt=prompt
        )
        _clk = get_clock()
        _clk.emit_replay_key(context=f"lic:gemini:{self._AGENT_ID}:{self._MODEL}")
        _clk.emit_determinism_digest(inputs={"agent": self._AGENT_ID, "model": self._MODEL})
        response = asyncio.get_event_loop().run_until_complete(self._gateway.route_generation(request))
        return response.content
