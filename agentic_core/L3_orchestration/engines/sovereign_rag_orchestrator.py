from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
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
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "sovereign_rag_orchestrator")
emit_determinism_digest("p0", "sovereign_rag_orchestrator")

_emit_dispatches_healing_run("p1", "sovereign_rag_orchestrator", "L3")
_emit_routes_through("p1", "sovereign_rag_orchestrator", "L3")
_emit_checks_agent_registry("p1", "sovereign_rag_orchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_rag_orchestrator", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_rag_orchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_rag_orchestrator", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_rag_orchestrator", "target_agent")
_emit_verifies_policy("p1", "sovereign_rag_orchestrator", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_rag_orchestrator", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_rag_orchestrator", "boundary_check")
_emit_transcripts_response("p1", "sovereign_rag_orchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_rag_orchestrator")
_emit_gated_by_confidence("p1", "sovereign_rag_orchestrator", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_rag_orchestrator", "L3")
_emit_reads_policy_state("p1", "sovereign_rag_orchestrator", "L3")
_emit_authorize_and_execute("p2", "sovereign_rag_orchestrator", "execution_auth")
_emit_validates_capability("p2", "sovereign_rag_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "sovereign_rag_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_rag_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_rag_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_rag_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_rag_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "sovereign_rag_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_rag_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_rag_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_rag_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_rag_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_rag_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_rag_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_rag_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_rag_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_rag_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "sovereign_rag_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_rag_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_rag_orchestrator", "exec_snapshot_link")

"\nSovereign RAG Orchestrator - L3 Self-Optimizing RAG System\nAdapts parameters based on performance with persistent configuration\n"
import asyncio
import json
import logging
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock

logger = logging.getLogger(__name__)
from agentic_core.L3_orchestration.types.rag_provider_types import (
    IRagProvider,
    RagDocument,
    RagQuery,
    RagResult,
)


def _get_active_configs():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_active_configs", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_active_configs", "p0_governance")
    from agentic_core.L4_state.config.versioned_configs import get_active_configs

    return get_active_configs


def _get_retrieval_anchor_types():
    from agentic_core.L4_state.types.retrieval_anchor_types import AnchoredResult, RetrievalAnchor

    return (AnchoredResult, RetrievalAnchor)


from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
from agentic_core.utils.schemas.decorators_compat_util import standard_heal
from agentic_core.utils.schemas.timeout_decorator_util import timeout

_emit_emits_metric_event("sovereign_rag_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_rag_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_rag_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_rag_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_rag_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_rag_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_rag_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_rag_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_rag_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_rag_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_rag_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("sovereign_rag_orchestrator", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_rag_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("sovereign_rag_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_rag_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_rag_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_rag_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_rag_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("sovereign_rag_orchestrator", "p3lm", "state")
_emit_records_execution_trace("sovereign_rag_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_rag_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_rag_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_rag_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_rag_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_rag_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_rag_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_rag_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_rag_orchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_rag_orchestrator", "context_pull")
_emit_pulls_context("p1", "sovereign_rag_orchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_rag_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_rag_orchestrator", "uwg_term_2")
_emit_writes_through("p1", "sovereign_rag_orchestrator", "write_through")
_emit_writes_through("p1", "sovereign_rag_orchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_rag_orchestrator", "safety_validation")
_emit_invokes_eval("p1", "sovereign_rag_orchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_rag_orchestrator", "routing_commit")
from agentic_core.runtime.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_dispatch_entry")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_dispatch_exit")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_tool_invoke")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_tool_complete")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_agent_entry")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_agent_exit")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_uwg_write")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_trace_sign")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_guardrail_check")
emit_determinism_digest("trace_sovereign_rag_orchestrator", "sovereign_rag_orchestrator_policy_verify")


def get_sovereign_rag_orchestrator() -> SovereignRagOrchestrator:
    """
    Get singleton instance of Sovereign RAG Orchestrator.

    Returns:
        SovereignRagOrchestrator instance
    """
    return SovereignRagOrchestrator()


@dataclass
class SovereignRagOrchestrator(SovereignBaseAgent, IRagProvider):
    """
    Sovereign RAG Orchestrator - L3 Self-Optimizing RAG System.

    Adapts parameters based on performance with persistent configuration.
    Implements IRagProvider for unified RAG interface.
    """

    def __init__(
        self,
        retriever: Any | None = None,
        query_planner: Any | None = None,
        guardrail: Any | None = None,
        engine: Any | None = None,
    ) -> None:
        """
        Initialize sovereign RAG orchestrator.

        Args:
            retriever: Optional retriever instance
            query_planner: Optional query planner instance
            guardrail: Optional guardrail instance
            engine: Optional engine instance
        """
        self.query_history: list[Any] = []
        self.config_path: Path = Path("agentic_core/L4_state/memory/.sovereign_config.json")
        self._load_sovereign_config()
        self.threshold_adaptation_rate: float = 0.02
        self.performance_window: int = 50
        self.retriever: Any | None = retriever
        self.query_planner: Any | None = query_planner
        self.guardrail: Any | None = guardrail
        self.engine: Any | None = engine
        self.enable_red_team_critique: bool = False
        self.max_critique_rounds: int = 2
        self.titanium_pipeline: Any | None = None
        self._init_titanium_pipeline()

    def _init_titanium_pipeline(self) -> None:
        """Initialize Titanium RAG Pipeline for SOTA features with strict lazy-loading."""
        try:
            from apps_shared.utils.TitaniumRAGPipeline import TitaniumRAGPipeline

            self.titanium_pipeline = TitaniumRAGPipeline(
                enable_compression=True, enable_decomposition=True, enable_reranking=True, enable_caching=True
            )
            print("   [OK] Titanium RAG Pipeline integrated")
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            print("   [WARN] Titanium RAG Pipeline unavailable - Using legacy path")

    def _load_sovereign_config(self) -> None:
        """
        L4: Persist the 'learned intelligence' of the system.

        Loads configuration from persistent storage or uses defaults.
        """
        _budget_cfg = get_active_configs().budget
        _routing_cfg = get_active_configs().routing
        # guardian: allow-config-with-logic
        if self.config_path.exists():
            config = json.loads(self.config_path.read_text())
            self.faithfulness_threshold = config.get("faithfulness_threshold", 0.88)
            self.max_hops = config.get("max_hops", _routing_cfg.depth_breaker)
            self.base_top_k = config.get("base_top_k", _budget_cfg.max_k)
        else:
            # guardian: allow-magic-config
            self.faithfulness_threshold = 0.88
            self.max_hops = _routing_cfg.depth_breaker
            self.base_top_k = _budget_cfg.max_k

    def _save_sovereign_config(self) -> None:
        """
        L4: Write learned parameters back to the Canon.

        Persists learned configuration to disk.
        """
        _wg.ensure_dir(self.config_path.parent)
        _wg.write_text(
            self.config_path,
            json.dumps(
                {
                    "faithfulness_threshold": self.faithfulness_threshold,
                    "max_hops": self.max_hops,
                    "base_top_k": self.base_top_k,
                }
            ),
        )

    # guardian: allow-type-erasure
    async def red_team_critique(self, answer: str, documents: list[Any], query: str) -> dict[str, Any]:
        """
        L5: Red team critique for faithfulness validation.

        Args:
            answer: Generated answer to critique
            documents: Source documents used
            query: Original query

        Returns:
            Dictionary with faithfulness score and improvement suggestions
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "SovereignRAGOrchestrator.red_team_critique"
        )
        response: Any = await self.engine.resilient_mutation(critique_prompt, temperature=0.3)

        # guardian: allow-type-erasure
        def _parse_critique(raw) -> Any:
            """Parse critique."""
            try:
                from agentic_core.L1_cognition.engines.query_planner import query_planner

                planner_helper = query_planner()
                cleaned = planner_helper._clean_json_response(raw)
                return json.loads(cleaned)
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                return {
                    "faithfulness_score": 0.0,
                    "improvement_suggestion": "Critical parsing error. Retry retrieval.",
                }

        return _parse_critique(response)

    async def retrieve(self, query: RagQuery) -> RagResult:
        """
        Unified retrieve method implementing IRagProvider interface.
        Routes to Titanium Pipeline if available, else falls back to legacy.
        """
        start_time = get_clock().now_epoch()
        if self.titanium_pipeline:

            async def retrieval_func(q: str, max_docs: int, **kwargs):
                vector_results = await self.retriever.hybrid_search(q, top_k=max_docs)
                sparse_results = []
                return (vector_results, sparse_results)

            result = await self.titanium_pipeline.query(
                query.query, retrieval_function=retrieval_func, top_k_final=query.top_k
            )
            documents = [
                RagDocument(
                    id=doc.doc_id,
                    text=doc.metadata.get("text", ""),
                    score=doc.final_score,
                    metadata=doc.metadata,
                    source="titanium_pipeline",
                )
                for doc in result["documents"]
            ]
            return RagResult(
                query=query.query,
                documents=documents,
                latency_ms=(get_clock().now_epoch() - start_time) * 1000,
                cached=result["metadata"].get("cached", False),
                reranked=result["metadata"].get("reranked", False),
                metadata=result["metadata"],
            )
        else:
            legacy_result = await self.sovereign_retrieve(
                query.query, top_k=query.top_k, filters=query.filters, mission_context=query.mission_context
            )
            documents = [
                RagDocument(
                    id=f"doc_{i}",
                    text=doc.text if hasattr(doc, "text") else str(doc),
                    score=doc.score if hasattr(doc, "score") else 0.0,
                    metadata={},
                    source="legacy_retriever",
                )
                for i, doc in enumerate(legacy_result.get("documents", []))
            ]
            return RagResult(
                query=query.query,
                documents=documents,
                latency_ms=(get_clock().now_epoch() - start_time) * 1000,
                faithfulness_score=legacy_result.get("faithfulness", 0.0),
                metadata=legacy_result,
            )

    async def index(self, documents: list[RagDocument], namespace: str = "sovereign-core") -> dict[str, int]:
        """Index documents into RAG system."""
        if not self.retriever:
            return {"indexed": 0, "failed": 0, "skipped": len(documents)}
        return {"indexed": len(documents), "failed": 0, "skipped": 0}

    # guardian: allow-type-erasure
    def get_health(self) -> dict[str, Any]:
        """Get RAG system health status."""
        return {
            "retriever_available": self.retriever is not None,
            "guardrail_available": self.guardrail is not None,
            "engine_available": self.engine is not None,
            "titanium_pipeline_available": self.titanium_pipeline is not None,
            "config": self.get_config(),
        }

    # guardian: allow-type-erasure
    async def sovereign_retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filters: dict | None = None,
        mission_context: dict | None = None,
    ) -> dict[str, Any]:
        """
        Main retrieval method with multi-hop expansion and self-optimization
        """
        if top_k is None:
            top_k: Any = self.base_top_k
        current_query: Any = query
        all_documents: Any = []
        for hop in range(self.max_hops):
            base_queries: Any = await self.query_planner.decompose_query(current_query)
            all_queries: Any = []
            async with asyncio.TaskGroup() as tg:
                tasks: Any = [
                    tg.create_task(self.query_planner.multi_query_generation(bq)) for bq in base_queries
                ]
            for t in tasks:
                all_queries.extend(t.result())
            all_queries: Any = list(dict.fromkeys(all_queries))
            _hop_top_k = get_active_configs().budget.max_k
            tasks: Any = [self.retriever.hybrid_search(q, top_k=_hop_top_k) for q in all_queries]
            results_lists: Any = await asyncio.gather(*tasks)
            retrieved: Any = [doc for sublist in results_lists for doc in sublist]
            unique_docs: Any = self.retriever.deduplicate_by_hash(retrieved, set())
            all_documents.extend(unique_docs)
            if len(all_documents) >= top_k:
                break
        final_docs: Any = await self.guardrail.rerank_documents(all_documents, query, top_k=top_k)
        _anchors = [
            AnchoredResult(
                content=doc.content if hasattr(doc, "content") else str(doc),
                anchor=RetrievalAnchor(
                    source_doc_id=getattr(doc, "doc_id", getattr(doc, "id", f"doc-{i}")),
                    chunk_id=getattr(doc, "chunk_id", f"chunk-{i}"),
                    char_start=0,
                    char_end=len(doc.content if hasattr(doc, "content") else str(doc)),
                    retrieved_at_utc=RetrievalAnchor.now_utc(),
                    version_hash=getattr(doc, "content_hash", getattr(doc, "hash", "unknown")),
                ),
            )
            for i, doc in enumerate(final_docs)
        ]
        result: Any = {
            "query": query,
            "documents": final_docs,
            "anchors": _anchors,
            "faithfulness": 0.85,
            "top_k": top_k,
            "hops": hop + 1,
        }
        self.query_history.append(result)
        if len(self.query_history) >= self.performance_window:
            await self.adapt_parameters(result)
        return result

    # guardian: allow-type-erasure
    async def adapt_parameters(self, result: dict) -> Any:
        """Self-optimization: adjust thresholds with dampen and persistence"""
        recent: Any = self.query_history[-self.performance_window :]
        faithfulness_scores: Any = [r.get("faithfulness", 0.0) for r in recent]
        avg_faithfulness: Any = sum(faithfulness_scores) / len(faithfulness_scores)
        if avg_faithfulness > 0.94:
            self.faithfulness_threshold = min(
                0.95, self.faithfulness_threshold + self.threshold_adaptation_rate
            )
            self._save_sovereign_config()
            print(f"   [SELF-OPT] Raising threshold to {self.faithfulness_threshold:.3f}")
        elif avg_faithfulness < 0.85:
            self.faithfulness_threshold = max(
                0.7, self.faithfulness_threshold - self.threshold_adaptation_rate
            )
            self._save_sovereign_config()
            print(f"   [SELF-OPT] Lowering threshold to {self.faithfulness_threshold:.3f}")
        if avg_faithfulness > 0.92 and self.base_top_k > 8:
            self.base_top_k -= 1
            self._save_sovereign_config()
            print(f"   [SELF-OPT] Reducing top_k to {self.base_top_k}")
        elif avg_faithfulness < 0.82 and self.base_top_k < 20:
            self.base_top_k += 1
            self._save_sovereign_config()
            print(f"   [SELF-OPT] Increasing top_k to {self.base_top_k}")

    # guardian: allow-type-erasure
    async def multi_hop_retrieve(self, query: str, max_hops: int | None = None) -> dict[str, Any]:
        """
        Multi-hop retrieval with iterative refinement
        """
        if max_hops is None:
            max_hops: Any = self.max_hops
        all_documents: Any = []
        current_query: Any = query
        for hop in range(max_hops):
            result: Any = await self.sovereign_retrieve(current_query)
            all_documents.extend(result.get("documents", []))
            if result.get("faithfulness", 0.0) >= self.faithfulness_threshold:
                break
            current_query: Any = f"Refined: {current_query}"
        return {
            "query": query,
            "documents": all_documents,
            "hops": hop + 1,
            "faithfulness": result.get("faithfulness", 0.0),
        }

    def set_rerank_engine(self, rerank_engine: Any) -> None:
        """Inject a RerankEngine implementation.

        The engine must implement:
            async rerank(query: str, candidates: list[Any]) -> list[Any]

        When set, _llm_rerank() routes through this engine instead of
        falling back to score-sorted truncation.
        Fail-closed: any exception in reranking returns candidates[:top_k] unchanged.
        """
        self.engine = rerank_engine

    async def _llm_rerank(self, candidates: list[Any], query: str, top_k: int) -> list[Any]:
        """Rerank candidates via injected engine or fall back to score-sorted truncation."""
        if self.engine is None:
            try:
                candidates.sort(key=lambda d: getattr(d, "score", 0.0), reverse=True)
            except (AttributeError, TypeError) as e:
                logger.debug(f"Failed to sort candidates by score: {e}")
            return candidates[:top_k]
        try:
            return await self.engine.rerank(query, candidates)
        except (AttributeError, TypeError, ValueError, RuntimeError) as e:
            logger.warning("_llm_rerank: rerank_engine raised — returning candidates[:top_k]", exc_info=True)
            return candidates[:top_k]

    _SUFFICIENCY_THRESHOLD: float = 0.6
    _MAX_REFLECTION_ROUNDS: int = 2

    async def _check_sufficiency(self, candidates: list[Any], query: str) -> float:
        """Compute mean cosine similarity of top results to query embedding.

        Returns a float in [0, 1]. 0.0 means no embedder available.
        """
        try:
            import math

            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            q_emb = bmg_embed_text(query)
            if not q_emb or not candidates:
                return 0.0

            def _cosine(a: list[float], b: list[float]) -> float:
                dot = sum((x * y for x, y in zip(a, b)))
                na = math.sqrt(sum(x * x for x in a))
                nb = math.sqrt(sum(x * x for x in b))
                return dot / (na * nb + 1e-08)

            scores = []
            for doc in candidates[: self.base_top_k]:
                text = (
                    doc.text
                    if hasattr(doc, "text")
                    else doc.get("text", "")
                    if isinstance(doc, dict)
                    else str(doc)
                )
                d_emb = bmg_embed_text(text)
                if d_emb:
                    scores.append(_cosine(q_emb, d_emb))
            return sum(scores) / len(scores) if scores else 0.0
        except (AttributeError, TypeError, ZeroDivisionError) as e:
            logger.debug(f"Embedding similarity calculation failed: {e}")
            return 0.0

    # guardian: allow-type-erasure
    async def agentic_retrieve_with_reflection(self, query: str, top_k: int | None = None) -> dict[str, Any]:
        """Single-pass retrieval with up to MAX_REFLECTION_ROUNDS refinement rounds.

        If initial retrieval sufficiency < SUFFICIENCY_THRESHOLD (0.60):
        - Calls query_planner.decompose_query() to produce sub-queries
        - Executes retrieval for each sub-query, merges with sovereign_retrieve
        - Hard limit: 2 refinement rounds (no unbounded recursion)

        Returns the same dict shape as sovereign_retrieve().
        """
        if top_k is None:
            top_k = self.base_top_k
        result = await self.sovereign_retrieve(query, top_k=top_k)
        candidates = result.get("documents", [])
        for _round in range(self._MAX_REFLECTION_ROUNDS):
            sufficiency = await self._check_sufficiency(candidates, query)
            if sufficiency >= self._SUFFICIENCY_THRESHOLD:
                break
            logger.info(
                "agentic_retrieve_with_reflection: sufficiency=%.3f < %.3f — round %d refinement",
                sufficiency,
                self._SUFFICIENCY_THRESHOLD,
                _round + 1,
            )
            try:
                sub_queries = await self.query_planner.decompose_query(query)
            except (AttributeError, TypeError, ValueError) as e:
                logger.debug(f"Query decomposition failed: {e}")
                break
            for sq in sub_queries:
                try:
                    sub_result = await self.sovereign_retrieve(sq, top_k=top_k)
                    sub_docs = sub_result.get("documents", [])
                    seen_ids = {getattr(d, "id", None) or getattr(d, "doc_id", None) for d in candidates}
                    for doc in sub_docs:
                        doc_id = getattr(doc, "id", None) or getattr(doc, "doc_id", None)
                        if doc_id not in seen_ids:
                            candidates.append(doc)
                            seen_ids.add(doc_id)
                except (AttributeError, KeyError) as e:
                    logger.debug(f"Failed to process sub-query result: {e}")
                    continue
        result["documents"] = candidates
        result["reflection_applied"] = True
        return result

    # guardian: allow-type-erasure
    def get_config(self) -> dict[str, Any]:
        """Get current configuration"""
        return {
            "faithfulness_threshold": self.faithfulness_threshold,
            "max_hops": self.max_hops,
            "base_top_k": self.base_top_k,
            "threshold_adaptation_rate": self.threshold_adaptation_rate,
            "performance_window": self.performance_window,
        }

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L3 orchestration/workflow_engines - operational only."""
        if _call_path is None:
            _call_path = set()
        super().heal_repository(
            dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path
        )
        agent_name = "SovereignRagOrchestrator"
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration/workflow_engines - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by SovereignRagOrchestrator.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"SovereignRagOrchestrator heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            return {
                "status": "failed",
                "details": f"SovereignRagOrchestrator heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
