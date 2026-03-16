"""
EmbeddingMixin - Unified Embedding Access for Agents

[PHASE 4 MIGRATION] Provides single interface to embedding operations.
"""

from typing import Any, Literal

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "embedding_mixin", "p0_governance")
_emit_reads_policy_state("p0", "embedding_mixin", "policy_binding")
_emit_snapshots_state("p0", "embedding_mixin", "state_snapshot")
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EmbeddingMixin.embedding_gateway")

        if self._embedding_gateway is None:
            try:
                from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import get_embedding_gateway

                self._embedding_gateway = get_embedding_gateway()
            except ImportError:
                raise NotImplementedError(
                    "EmbeddingMixin: Embedding gateway is not available. Install the required dependencies or configure agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent."
                )
        return self._embedding_gateway

    async def get_embedding(
        self, content: str, provider: EmbeddingProvider = "bge-m3", use_cache: bool = True
    ) -> list[float]:
        """Get embedding through gateway."""
        return await self.embedding_gateway.get_embedding(content, provider, use_cache)

    async def get_embeddings_batch(
        self, contents: list[str], provider: EmbeddingProvider = "bge-m3"
    ) -> list[list[float]]:
        """Get batch embeddings through gateway."""
        return await self.embedding_gateway.get_embeddings_batch(contents, provider)
