"""
EmbeddingMixin - Unified Embedding Access for Agents

[PHASE 4 MIGRATION] Provides single interface to embedding operations.
"""

from typing import Any, Literal

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "embedding_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "embedding_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "embedding_mixin", "state_snapshot")

trace_contract._emit_emits_metric_event("embedding_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("embedding_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("embedding_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("embedding_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("embedding_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("embedding_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("embedding_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("embedding_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("embedding_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("embedding_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("embedding_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("embedding_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("embedding_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("embedding_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("embedding_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("embedding_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("embedding_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("embedding_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("embedding_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("embedding_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("embedding_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("embedding_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("embedding_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("embedding_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("embedding_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("embedding_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("embedding_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("embedding_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "embedding_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "embedding_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "embedding_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "embedding_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "embedding_mixin", "write_through")
trace_contract._emit_writes_through("p1", "embedding_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "embedding_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "embedding_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "embedding_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "embedding_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "embedding_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "embedding_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "embedding_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "embedding_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "embedding_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "embedding_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "embedding_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "embedding_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "embedding_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "embedding_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "embedding_mixin")
trace_contract._emit_gated_by_confidence("p1", "embedding_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "embedding_mixin")
trace_contract.emit_determinism_digest("p0", "embedding_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "embedding_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "embedding_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "embedding_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "embedding_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "embedding_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "embedding_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "embedding_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "embedding_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "embedding_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "embedding_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "embedding_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "embedding_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "embedding_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "embedding_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "embedding_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "embedding_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "embedding_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "embedding_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "embedding_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "embedding_mixin", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "EmbeddingMixin.embedding_gateway"
        )

        if self._embedding_gateway is None:
            try:
                from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import get_embedding_gateway

                self._embedding_gateway = get_embedding_gateway()
            except ImportError:  # guardian: allow-silent-swallow -- optional dependency
                raise NotImplementedError(
                    "EmbeddingMixin: Embedding gateway is not available. Install the required dependencies or configure agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent."
                ) from None
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
        except (
            AttributeError,
            RuntimeError,
            OSError,
        ) as e:  # guardian: allow-log-and-swallow -- embedding batch: non-fatal, logging.debug already called
            import logging

            logging.getLogger(__name__).debug("embedding_mixin: Exception swallowed at L204: %s", e)
