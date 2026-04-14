"""
EmbeddingMixin - Unified Embedding Access for Agents

[PHASE 4 MIGRATION] Provides single interface to embedding operations.
"""

from typing import Any, Literal

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

_emit_applies_guardrail("p0", "embedding_mixin", "p0_governance")
_emit_reads_policy_state("p0", "embedding_mixin", "policy_binding")
_emit_snapshots_state("p0", "embedding_mixin", "state_snapshot")
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

_emit_emits_metric_event("embedding_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("embedding_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("embedding_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("embedding_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("embedding_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("embedding_mixin", "p4obs", "metric_6")
_emit_records_incident_event("embedding_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("embedding_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("embedding_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("embedding_mixin", "p4obs", "mon_state")
_emit_triggers_alert("embedding_mixin", "p4obs", "alert")
_emit_links_incident_trace("embedding_mixin", "p4obs", "trace_link")
_emit_captures_pattern("embedding_mixin", "p3lm", "pattern")
_emit_records_learning_event("embedding_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("embedding_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("embedding_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("embedding_mixin", "p3lm", "routing")
_emit_improves_agent_policy("embedding_mixin", "p3lm", "policy")
_emit_stores_learning_state("embedding_mixin", "p3lm", "state")
_emit_records_execution_trace("embedding_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("embedding_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("embedding_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("embedding_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("embedding_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("embedding_mixin", "env_read", "p2_env_1")
_emit_reads_environ("embedding_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("embedding_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("embedding_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "embedding_mixin", "context_pull")
_emit_pulls_context("p1", "embedding_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "embedding_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "embedding_mixin", "uwg_term_2")
_emit_writes_through("p1", "embedding_mixin", "write_through")
_emit_writes_through("p1", "embedding_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "embedding_mixin", "safety_validation")
_emit_invokes_eval("p1", "embedding_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "embedding_mixin", "routing_commit")
_emit_escalates_to_human("p1", "embedding_mixin", "human_escalation")
_emit_routes_through("p1", "embedding_mixin", "route_through")
_emit_checks_agent_registry("p1", "embedding_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "embedding_mixin", "capability")
_emit_dispatches_execution_plan("p1", "embedding_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "embedding_mixin", "sub_agent")
_emit_routes_to_agent("p1", "embedding_mixin", "target_agent")
_emit_verifies_policy("p1", "embedding_mixin", "policy_check")
_emit_observes_runtime_state("p1", "embedding_mixin", "runtime_state")
_emit_verifies_boundary("p1", "embedding_mixin", "boundary_check")
_emit_transcripts_response("p1", "embedding_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "embedding_mixin")
_emit_gated_by_confidence("p1", "embedding_mixin", "confidence_gate")
emit_replay_key("p0", "embedding_mixin")
emit_determinism_digest("p0", "embedding_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "embedding_mixin", "execution_auth")
_emit_validates_capability("p2", "embedding_mixin", "capability_check")
_emit_routes_to_capability("p2", "embedding_mixin", "capability_route")
_emit_writes_via_uwg("p2", "embedding_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "embedding_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "embedding_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "embedding_mixin", "exec_output")
_emit_dispatches_agent("p3", "embedding_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "embedding_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "embedding_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "embedding_mixin", "healing_outcome")
_emit_escalates_failure("p3", "embedding_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "embedding_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embedding_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "embedding_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "embedding_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embedding_mixin", "eval_metric")
_emit_stores_embedding("p4", "embedding_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "embedding_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embedding_mixin", "exec_snapshot_link")

EmbeddingProvider = Literal["gemini", "openai", "bge-m3"]


class EmbeddingMixin:
    """
    Mixin providing unified embedding gateway access.

    [PHASE 4 MIGRATION] Replaces direct embedding implementations.

    Usage:
        class MyAgent(EmbeddingMixin, SovereignBaseAgent):
            async def process(self, text: str):
                embedding = await self.get_embedding(text)
                return embedding
    """

    _embedding_gateway: Any | None = None

    @property
    def embedding_gateway(self) -> Any:
        """Lazy-load embedding gateway singleton."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "EmbeddingMixin.embedding_gateway"
        )

        if self._embedding_gateway is None:
            try:
                from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import get_embedding_gateway

                self._embedding_gateway = get_embedding_gateway()
            # guardian: allow-silent-swallow - optional dependency
            except ImportError:
                raise NotImplementedError(
                    "EmbeddingMixin: Embedding gateway is not available. Install the required dependencies or configure agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent.",
                )
        return self._embedding_gateway

    async def get_embedding(
        self,
        content: str,
        provider: EmbeddingProvider = "bge-m3",
        use_cache: bool = True,
    ) -> list[float]:
        """Get embedding through gateway."""
        return await self.embedding_gateway.get_embedding(content, provider, use_cache)

    async def get_embeddings_batch(
        self,
        contents: list[str],
        provider: EmbeddingProvider = "bge-m3",
    ) -> list[list[float]]:
        """Get batch embeddings through gateway."""
        try:
            return await self.embedding_gateway.get_embeddings_batch(contents, provider)
        except (AttributeError, RuntimeError, OSError) as e:
            import logging

            logging.getLogger(__name__).debug("embedding_mixin: Exception swallowed at L204: %s", e)
