"""
LLMProviderMixin - Unified LLM Access for Agents

[PHASE 4 MIGRATION] Provides single interface to all LLM providers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "llm_provider_mixin", "p0_governance")
_emit_reads_policy_state("p0", "llm_provider_mixin", "policy_binding")
_emit_snapshots_state("p0", "llm_provider_mixin", "state_snapshot")
emit_replay_key("p0", "llm_provider_mixin")
emit_determinism_digest("p0", "llm_provider_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "llm_provider_mixin", "execution_auth")
_emit_validates_capability("p2", "llm_provider_mixin", "capability_check")
_emit_routes_to_capability("p2", "llm_provider_mixin", "capability_route")
_emit_writes_via_uwg("p2", "llm_provider_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "llm_provider_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "llm_provider_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "llm_provider_mixin", "exec_output")
_emit_dispatches_agent("p3", "llm_provider_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "llm_provider_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "llm_provider_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "llm_provider_mixin", "healing_outcome")
_emit_escalates_failure("p3", "llm_provider_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "llm_provider_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "llm_provider_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "llm_provider_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "llm_provider_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "llm_provider_mixin", "eval_metric")
_emit_stores_embedding("p4", "llm_provider_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "llm_provider_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "llm_provider_mixin", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("llm_provider_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("llm_provider_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("llm_provider_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("llm_provider_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("llm_provider_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("llm_provider_mixin", "p4obs", "metric_6")
_emit_records_incident_event("llm_provider_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("llm_provider_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("llm_provider_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("llm_provider_mixin", "p4obs", "mon_state")
_emit_triggers_alert("llm_provider_mixin", "p4obs", "alert")
_emit_links_incident_trace("llm_provider_mixin", "p4obs", "trace_link")
_emit_captures_pattern("llm_provider_mixin", "p3lm", "pattern")
_emit_records_learning_event("llm_provider_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("llm_provider_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("llm_provider_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("llm_provider_mixin", "p3lm", "routing")
_emit_improves_agent_policy("llm_provider_mixin", "p3lm", "policy")
_emit_stores_learning_state("llm_provider_mixin", "p3lm", "state")
_emit_records_execution_trace("llm_provider_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("llm_provider_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("llm_provider_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("llm_provider_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("llm_provider_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("llm_provider_mixin", "env_read", "p2_env_1")
_emit_reads_environ("llm_provider_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("llm_provider_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("llm_provider_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "llm_provider_mixin", "context_pull")
_emit_pulls_context("p1", "llm_provider_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "llm_provider_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "llm_provider_mixin", "uwg_term_2")
_emit_writes_through("p1", "llm_provider_mixin", "write_through")
_emit_writes_through("p1", "llm_provider_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "llm_provider_mixin", "safety_validation")
_emit_invokes_eval("p1", "llm_provider_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "llm_provider_mixin", "routing_commit")
_emit_escalates_to_human("p1", "llm_provider_mixin", "human_escalation")
_emit_routes_through("p1", "llm_provider_mixin", "route_through")
_emit_checks_agent_registry("p1", "llm_provider_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "llm_provider_mixin", "capability")
_emit_dispatches_execution_plan("p1", "llm_provider_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "llm_provider_mixin", "sub_agent")
_emit_routes_to_agent("p1", "llm_provider_mixin", "target_agent")
_emit_verifies_policy("p1", "llm_provider_mixin", "policy_check")
_emit_observes_runtime_state("p1", "llm_provider_mixin", "runtime_state")
_emit_verifies_boundary("p1", "llm_provider_mixin", "boundary_check")
_emit_transcripts_response("p1", "llm_provider_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "llm_provider_mixin")
_emit_gated_by_confidence("p1", "llm_provider_mixin", "confidence_gate")

Provider = Literal["openai", "anthropic", "google"]


def _get_llm_gateway():
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway

    return get_llm_gateway()


class LLMProviderMixin:
    """
    Mixin providing unified LLM gateway access.

    [PHASE 4 MIGRATION] Replaces direct SDK imports.

    Usage:
        class MyAgent(LLMProviderMixin, SovereignBaseAgent):
            async def process(self, query: str) -> str:
                response = await self.llm_generate(query)
                return response["content"]
    """

    _llm_gateway: SovereignLLMGateway | None = None

    @property
    def llm_gateway(self) -> SovereignLLMGateway:
        """Lazy-load LLM gateway singleton."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LLMProviderMixin.llm_gateway")

        if self._llm_gateway is None:
            self._llm_gateway = _get_llm_gateway()
        return self._llm_gateway

    async def llm_generate(
        self,
        prompt: str,
        model: str | None = None,
        provider: Provider = "openai",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate LLM response through gateway."""
        return await self.llm_gateway.generate(prompt, model=model, provider=provider, **kwargs)

    async def llm_generate_with_fallback(
        self,
        prompt: str,
        model: str | None = None,
        fallback_providers: list[Provider] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate with automatic provider fallback."""
        return await self.llm_gateway.generate(
            prompt,
            model=model,
            fallback_providers=fallback_providers,
            **kwargs,
        )
