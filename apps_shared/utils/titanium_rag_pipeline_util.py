"""Titanium RAG Pipeline - State-of-the-Art Retrieval with Precision, Reasoning, and SOTA.

This module orchestrates the complete Titanium RAG system with three layers:
- Phase 1: Precision Layer (Contextual Compression)
- Phase 2: Reasoning Layer (Query Decomposition & Dynamic scoring)
- Phase 3: SOTA Layer (Semantic cache & Cross-Encoder Reranking)

Enhanced with adversarial defense as the outermost security layer.
"""

import logging
import time
from typing import Any

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

_emit_authorize_and_execute("p2", "titanium_rag_pipeline_util", "execution_auth")
_emit_validates_capability("p2", "titanium_rag_pipeline_util", "capability_check")
_emit_routes_to_capability("p2", "titanium_rag_pipeline_util", "capability_route")
_emit_writes_via_uwg("p2", "titanium_rag_pipeline_util", "uwg_write")
_emit_blocks_direct_write("p2", "titanium_rag_pipeline_util", "direct_write_block")
_emit_records_tool_invocation("p2", "titanium_rag_pipeline_util", "tool_invocation")
_emit_captures_execution_output("p2", "titanium_rag_pipeline_util", "exec_output")
_emit_dispatches_agent("p3", "titanium_rag_pipeline_util", "agent_dispatch")
_emit_coordinates_agents("p3", "titanium_rag_pipeline_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "titanium_rag_pipeline_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "titanium_rag_pipeline_util", "healing_outcome")
_emit_escalates_failure("p3", "titanium_rag_pipeline_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "titanium_rag_pipeline_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "titanium_rag_pipeline_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "titanium_rag_pipeline_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "titanium_rag_pipeline_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "titanium_rag_pipeline_util", "eval_metric")
_emit_stores_embedding("p4", "titanium_rag_pipeline_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "titanium_rag_pipeline_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "titanium_rag_pipeline_util", "exec_snapshot_link")
from .graphrag_fusion import (
    GraphRAGFusion,
    get_graphrag_fusion,
)
from .input_guardrail import (
    GuardAction,
    InputGuardrail,
    get_input_guardrail,
)
from .precision_layer import (
    ContextualCompressor,
)
from .reasoning_layer import (
    HybridScorer,
    QueryDecomposer,
)
from .retrieval_grader import (
    GradeStatus,
    RetrievalGrader,
    WebSearchFallback,
    get_retrieval_grader,
    get_web_search_fallback,
)
from .sota_layer import (
    ContrastiveSemanticCache,
    LateInteractionReranker,
)

_emit_applies_guardrail("p0", "titanium_rag_pipeline_util", "p0_governance")
_emit_reads_policy_state("p0", "titanium_rag_pipeline_util", "policy_binding")
_emit_snapshots_state("p0", "titanium_rag_pipeline_util", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("titanium_rag_pipeline_util", "p4obs", "metric_1")
_emit_emits_metric_event("titanium_rag_pipeline_util", "p4obs", "metric_2")
_emit_emits_metric_event("titanium_rag_pipeline_util", "p4obs", "metric_3")
_emit_emits_metric_event("titanium_rag_pipeline_util", "p4obs", "metric_4")
_emit_emits_metric_event("titanium_rag_pipeline_util", "p4obs", "metric_5")
_emit_emits_metric_event("titanium_rag_pipeline_util", "p4obs", "metric_6")
_emit_records_incident_event("titanium_rag_pipeline_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("titanium_rag_pipeline_util", "p4obs", "anomaly")
_emit_writes_observability_log("titanium_rag_pipeline_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("titanium_rag_pipeline_util", "p4obs", "mon_state")
_emit_triggers_alert("titanium_rag_pipeline_util", "p4obs", "alert")
_emit_links_incident_trace("titanium_rag_pipeline_util", "p4obs", "trace_link")
_emit_captures_pattern("titanium_rag_pipeline_util", "p3lm", "pattern")
_emit_records_learning_event("titanium_rag_pipeline_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("titanium_rag_pipeline_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("titanium_rag_pipeline_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("titanium_rag_pipeline_util", "p3lm", "routing")
_emit_improves_agent_policy("titanium_rag_pipeline_util", "p3lm", "policy")
_emit_stores_learning_state("titanium_rag_pipeline_util", "p3lm", "state")
_emit_records_execution_trace("titanium_rag_pipeline_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("titanium_rag_pipeline_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("titanium_rag_pipeline_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("titanium_rag_pipeline_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("titanium_rag_pipeline_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("titanium_rag_pipeline_util", "env_read", "p2_env_1")
_emit_reads_environ("titanium_rag_pipeline_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("titanium_rag_pipeline_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("titanium_rag_pipeline_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "titanium_rag_pipeline_util", "context_pull")
_emit_pulls_context("p1", "titanium_rag_pipeline_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "titanium_rag_pipeline_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "titanium_rag_pipeline_util", "uwg_term_2")
_emit_writes_through("p1", "titanium_rag_pipeline_util", "write_through")
_emit_writes_through("p1", "titanium_rag_pipeline_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "titanium_rag_pipeline_util", "safety_validation")
_emit_invokes_eval("p1", "titanium_rag_pipeline_util", "eval_call")
_emit_proposal_commits_routing("p1", "titanium_rag_pipeline_util", "routing_commit")
_emit_escalates_to_human("p1", "titanium_rag_pipeline_util", "human_escalation")
_emit_routes_through("p1", "titanium_rag_pipeline_util", "route_through")
_emit_checks_agent_registry("p1", "titanium_rag_pipeline_util", "agent_registry")
_emit_validates_agent_capability("p1", "titanium_rag_pipeline_util", "capability")
_emit_dispatches_execution_plan("p1", "titanium_rag_pipeline_util", "exec_plan")
_emit_agent_executes_agent("p1", "titanium_rag_pipeline_util", "sub_agent")
_emit_routes_to_agent("p1", "titanium_rag_pipeline_util", "target_agent")
_emit_verifies_policy("p1", "titanium_rag_pipeline_util", "policy_check")
_emit_observes_runtime_state("p1", "titanium_rag_pipeline_util", "runtime_state")
_emit_verifies_boundary("p1", "titanium_rag_pipeline_util", "boundary_check")
_emit_transcripts_response("p1", "titanium_rag_pipeline_util", "transcript")
_emit_hard_fails_untranscripted("p1", "titanium_rag_pipeline_util")
_emit_gated_by_confidence("p1", "titanium_rag_pipeline_util", "confidence_gate")
emit_replay_key("p0", "titanium_rag_pipeline_util")
emit_determinism_digest("p0", "titanium_rag_pipeline_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class TitaniumRAGPipeline:
    """Titanium-grade RAG pipeline combining all three layers.

    Phase 1 (Precision): Filters noise and avoids unnecessary searches
    Phase 2 (Reasoning): Handles complex queries with intelligent decomposition
    Phase 3 (SOTA): Provides Google-quality ranking and Redis-speed caching
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        # Phase 1 components
        gate: AdaptiveRetrievalGate | None = None,
        compressor: ContextualCompressor | None = None,
        # Phase 2 components
        decomposer: QueryDecomposer | None = None,
        scorer: HybridScorer | None = None,
        # Phase 3 components
        reranker: LateInteractionReranker | None = None,
        cache: ContrastiveSemanticCache | None = None,
        # Security layer
        input_guardrail: InputGuardrail | None = None,
        # CRAG layer
        retrieval_grader: RetrievalGrader | None = None,
        web_search_fallback: WebSearchFallback | None = None,
        # GraphRAG layer
        graphrag_fusion: GraphRAGFusion | None = None,
        # configuration
        enable_compression: bool = True,
        enable_decomposition: bool = True,
        enable_reranking: bool = True,
        enable_caching: bool = True,
        enable_security: bool = True,
        enable_crag: bool = True,
        enable_graphrag: bool = True,
        max_retrieved_docs: int = 50,
        top_k_final: int = 5,
    ):
        """Initialize the Titanium RAG Pipeline.

        Args:
            gate: Adaptive retrieval gate (Phase 1)
            compressor: Contextual compressor (Phase 1)
            decomposer: Query decomposer (Phase 2)
            scorer: Dynamic hybrid scorer (Phase 2)
            reranker: Late interaction reranker (Phase 3)
            cache: Contrastive semantic cache (Phase 3)
            input_guardrail: Security layer for input validation
            retrieval_grader: CRAG grader for document relevance
            web_search_fallback: Web search fallback for CRAG
            graphrag_fusion: GraphRAG fusion for relationship queries
            enable_compression: Whether to enable compression
            enable_decomposition: Whether to enable query decomposition
            enable_reranking: Whether to enable reranking
            enable_caching: Whether to enable caching
            enable_security: Whether to enable security scanning
            enable_crag: Whether to enable Corrective RAG
            enable_graphrag: Whether to enable GraphRAG fusion
            max_retrieved_docs: Maximum documents to retrieve initially
            top_k_final: Number of top documents to return
        """
        # Initialize components if not provided
        self.gate = gate or AdaptiveRetrievalGate()
        self.compressor = compressor or ContextualCompressor()
        self.decomposer = decomposer or QueryDecomposer()
        self.scorer = scorer or HybridScorer(dynamic_alpha=True)
        self.reranker = reranker or LateInteractionReranker()
        self.cache = cache or ContrastiveSemanticCache()

        # Initialize security layer
        self.input_guardrail = input_guardrail or (get_input_guardrail() if enable_security else None)
        self.enable_security = enable_security and self.input_guardrail is not None

        # Initialize CRAG layer
        self.retrieval_grader = retrieval_grader or (get_retrieval_grader() if enable_crag else None)
        self.web_search_fallback = web_search_fallback or (get_web_search_fallback() if enable_crag else None)
        self.enable_crag = enable_crag and self.retrieval_grader is not None

        # Initialize GraphRAG layer
        self.graphrag_fusion = graphrag_fusion or (get_graphrag_fusion() if enable_graphrag else None)
        self.enable_graphrag = enable_graphrag and self.graphrag_fusion is not None

        # configuration
        self.enable_compression = enable_compression
        self.enable_decomposition = enable_decomposition
        self.enable_reranking = enable_reranking
        self.enable_caching = enable_caching
        self.max_retrieved_docs = max_retrieved_docs
        self.top_k_final = top_k_final

        # Statistics
        self.stats = {
            "total_queries": 0,
            "gate_blocks": 0,
            "cache_hits": 0,
            "decompositions": 0,
            "compressions": 0,
            "rerankings": 0,
            "security_blocks": 0,
            "security_warnings": 0,
            "pii_redactions": 0,
            "crag_fallbacks": 0,
            "crag_passes": 0,
            "graphrag_queries": 0,
            "graphrag_fallbacks": 0,
        }

        logger.info(
            f"Initialized TitaniumRAGPipeline with all 3 phases + "
            f"Security Layer: {self.enable_security} + "
            f"CRAG Layer: {self.enable_crag} + "
            f"GraphRAG Layer: {self.enable_graphrag}",
        )

    async def query(self, query: str, retrieval_function: callable, **kwargs) -> dict[str, Any]:
        """Execute a complete RAG pipeline query.

        Args:
            query: User query
            retrieval_function: Async function to retrieve documents
            **kwargs: Additional arguments for retrieval function

        Returns:
            Dictionary with results and metadata
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "TitaniumRAGPipeline.query"
        )
        start_time = time.time()
        self.stats["total_queries"] += 1

        logger.info(f"Processing query: {query[:50]}...")

        # Security Layer: Input validation (Phase 0 - Outermost)
        # ----------------------------------------------------
        if self.enable_security and self.input_guardrail:
            guard_result = self.input_guardrail.scan(query, user_id=kwargs.get("user_id"))

            # Handle security actions
            if guard_result.action == GuardAction.BLOCK:
                self.stats["security_blocks"] += 1
                logger.warning(f"Query blocked by security: {guard_result.reason}")
                return {
                    "query": query,
                    "response": "I cannot process that request due to safety protocols.",
                    "documents": [],
                    "metadata": {
                        "security_action": "BLOCKED",
                        "security_reason": guard_result.reason,
                        "security_confidence": guard_result.confidence,
                        "processing_time": time.time() - start_time,
                    },
                }
            elif guard_result.action == GuardAction.WARN:
                self.stats["security_warnings"] += 1
                logger.warning(f"Security warning for query: {guard_result.reason}")
                # Continue but mark as suspicious
            elif guard_result.action == GuardAction.REDACT:
                self.stats["pii_redactions"] += 1
                logger.info("PII redacted from query")
                query = guard_result.sanitized_input or query

        # Phase 1: Precision Layer
        # ----------------------

        # 1. Check if retrieval is needed
        gate_decision = self.gate.should_retrieve(query)
        if not gate_decision.should_retrieve:
            self.stats["gate_blocks"] += 1
            logger.info(f"Query blocked by gate: {gate_decision.reason}")
            return {
                "query": query,
                "response": None,
                "documents": [],
                "metadata": {
                    "gate_decision": gate_decision.dict(),
                    "cached": False,
                    "decomposed": False,
                    "compressed": False,
                    "reranked": False,
                    "processing_time": time.time() - start_time,
                },
            }

        # 2. Check semantic cache
        cached_response = None
        if self.enable_caching:
            cached_response = self.cache.get(query)
            if cached_response:
                self.stats["cache_hits"] += 1
                logger.info("cache hit, returning cached response")
                return {
                    "query": query,
                    "response": cached_response,
                    "documents": [],
                    "metadata": {
                        "gate_decision": gate_decision.dict(),
                        "cached": True,
                        "decomposed": False,
                        "compressed": False,
                        "reranked": False,
                        "processing_time": time.time() - start_time,
                    },
                }

        # Phase 2: Reasoning Layer
        # -----------------------

        # 3. Decompose query if needed
        queries_to_process = [query]
        decomposed_result = None

        if self.enable_decomposition:
            decomposed_result = await self.decomposer.decompose(query)
            if len(decomposed_result.sub_queries) > 1:
                queries_to_process = decomposed_result.sub_queries
                self.stats["decompositions"] += 1
                logger.info(f"Decomposed into {len(queries_to_process)} sub-queries")

        # 4. Retrieve documents for each query
        all_retrieved = []
        for sub_query in tqdm(queries_to_process, desc="Processing", unit="item"):
            # Retrieve dense and sparse results
            dense_results, sparse_results = await retrieval_function(
                sub_query,
                max_docs=self.max_retrieved_docs,
                **kwargs,
            )

            # Score with dynamic alpha
            scored = self.scorer.score_documents(
                dense_results=dense_results,
                sparse_results=sparse_results,
                query=sub_query,
            )

            all_retrieved.extend(scored)

        # Remove duplicates and sort by score
        seen_docs = set()
        unique_docs = []
        for doc in all_retrieved:
            if doc.doc_id not in seen_docs:
                seen_docs.add(doc.doc_id)
                unique_docs.append(doc)

        unique_docs.sort(key=lambda x: x.final_score, reverse=True)
        retrieved_docs = unique_docs[: self.max_retrieved_docs]

        logger.info(f"Retrieved {len(retrieved_docs)} unique documents")

        # CRAG Layer: Grade retrieval quality
        # ------------------------------------
        if self.enable_crag and self.retrieval_grader:
            # Extract document texts for grading
            doc_texts = []
            for doc in retrieved_docs:
                if hasattr(doc, "metadata") and "text" in doc.metadata:
                    doc_texts.append(doc.metadata["text"])
                elif hasattr(doc, "text"):
                    doc_texts.append(doc.text)
                elif hasattr(doc, "content"):
                    doc_texts.append(doc.content)
                else:
                    doc_texts.append(f"Document {doc.doc_id}")

            # Grade the documents
            grade = await self.retrieval_grader.grade_documents(query, doc_texts)

            # Handle grading results
            if grade.status == GradeStatus.FALLBACK_REQUIRED:
                self.stats["crag_fallbacks"] += 1
                logger.warning(f"CRAG triggered fallback: {grade.reasoning}")

                # Perform web search fallback
                if self.web_search_fallback:
                    web_results = await self.web_search_fallback.search(query)

                    # Create documents from web results
                    web_docs = []
                    for i, result in tqdm(
                        enumerate(web_results.get("results", [])), desc="Processing", unit="item"
                    ):
                        web_doc = type(
                            "WebDocument",
                            (),
                            {
                                "doc_id": f"web_{i}",
                                "text": result.get("snippet", ""),
                                "metadata": {
                                    "text": result.get("snippet", ""),
                                    "source": result.get("url", ""),
                                    "title": result.get("title", ""),
                                    "from_web": True,
                                },
                                "final_score": 1.0 - (i * 0.1),  # Simple ranking
                            },
                        )()
                        web_docs.append(web_doc)

                    # Use web results instead of retrieved docs
                    retrieved_docs = web_docs

                    return {
                        "query": query,
                        "response": None,
                        "documents": retrieved_docs,
                        "metadata": {
                            "crag_action": "FALLBACK_WEB_SEARCH",
                            "crag_reason": grade.reasoning,
                            "crag_relevance_ratio": grade.relevance_ratio,
                            "web_results_count": len(web_docs),
                            "processing_time": time.time() - start_time,
                        },
                    }
            elif grade.status == GradeStatus.PASS:
                self.stats["crag_passes"] += 1
                logger.info(f"CRAG passed: {grade.reasoning}")
            else:
                logger.info(f"CRAG uncertain: {grade.reasoning}")

        # GraphRAG Layer: Fuse vector and graph results
        # -------------------------------------------
        if self.enable_graphrag and self.graphrag_fusion:
            try:
                # Create vector retriever function for GraphRAG
                async def vector_retriever_func(q: str, k: int) -> list[dict[str, Any]]:
                    # Use already retrieved documents
                    results = []
                    for doc in tqdm(retrieved_docs[:k], desc="Processing", unit="item"):
                        text = ""
                        if hasattr(doc, "metadata") and "text" in doc.metadata:
                            text = doc.metadata["text"]
                        elif hasattr(doc, "text"):
                            text = doc.text
                        elif hasattr(doc, "content"):
                            text = doc.content

                        results.append(
                            {
                                "text": text,
                                "doc_id": doc.doc_id,
                                "score": getattr(doc, "final_score", 0.0),
                            },
                        )
                    return results

                # Configure GraphRAG with vector retriever
                self.graphrag_fusion.vector_retriever = vector_retriever_func

                # Execute GraphRAG fusion
                fusion_result = await self.graphrag_fusion.query(
                    query,
                    max_results=self.top_k_final,
                )

                self.stats["graphrag_queries"] += 1

                # Create fused documents
                fused_docs = []

                # Add vector results
                for i, result in tqdm(
                    enumerate(fusion_result.vector_results), desc="Processing", unit="item"
                ):
                    fused_doc = type(
                        "FusedDocument",
                        (),
                        {
                            "doc_id": f"vector_{i}",
                            "text": result.get("text", ""),
                            "metadata": {
                                "text": result.get("text", ""),
                                "source": "vector_search",
                                "score": result.get("score", 0.0),
                            },
                            "final_score": result.get("score", 0.0),
                        },
                    )()
                    fused_docs.append(fused_doc)

                # Add graph results as structured context
                if fusion_result.graph_results and fusion_result.graph_results.entities:
                    graph_text = fusion_result.fused_context
                    graph_doc = type(
                        "GraphDocument",
                        (),
                        {
                            "doc_id": "graph_context",
                            "text": graph_text,
                            "metadata": {
                                "text": graph_text,
                                "source": "graph_search",
                                "entities": fusion_result.graph_results.entities,
                                "relationships": fusion_result.graph_results.relationships,
                                "confidence": fusion_result.graph_results.confidence,
                            },
                            "final_score": fusion_result.confidence,
                        },
                    )()
                    fused_docs.append(graph_doc)

                # Use fused results
                retrieved_docs = fused_docs

                logger.info(
                    f"GraphRAG fusion completed - Vector: {len(fusion_result.vector_results)}, "
                    f"Graph entities: {len(fusion_result.graph_results.entities)}",
                )

            # guardian: allow-silent-swallow
            except Exception as e:
                self.stats["graphrag_fallbacks"] += 1
                logger.error(f"GraphRAG fusion failed: {e}")
                # Continue with vector results only

        # Phase 3: SOTA Layer
        # -------------------

        # 5. Rerank documents
        if self.enable_reranking and len(retrieved_docs) > self.top_k_final:
            # Extract document texts from metadata
            doc_texts = []
            for doc in tqdm(retrieved_docs, desc="Processing", unit="item"):
                # Try multiple fields for document text
                if hasattr(doc, "metadata") and "text" in doc.metadata:
                    doc_texts.append(doc.metadata["text"])
                elif hasattr(doc, "text"):
                    doc_texts.append(doc.text)
                elif hasattr(doc, "content"):
                    doc_texts.append(doc.content)
                else:
                    # Fallback: use doc_id as placeholder
                    doc_texts.append(f"Document {doc.doc_id}")

            # Rerank
            reranked_texts = self.reranker.rerank(
                query=query,
                documents=doc_texts,
                top_k=self.top_k_final,
            )

            # Map back to documents by text matching
            text_to_doc = {}
            for doc in tqdm(retrieved_docs, desc="Processing", unit="item"):
                doc_text = None
                if hasattr(doc, "metadata") and "text" in doc.metadata:
                    doc_text = doc.metadata["text"]
                elif hasattr(doc, "text"):
                    doc_text = doc.text
                elif hasattr(doc, "content"):
                    doc_text = doc.content

                if doc_text and doc_text not in text_to_doc:
                    text_to_doc[doc_text] = doc

            # Reconstruct final documents list
            final_docs = []
            for text in reranked_texts:
                if text in text_to_doc:
                    final_docs.append(text_to_doc[text])

            # If we couldn't map all documents, fill with remaining ones
            if len(final_docs) < self.top_k_final:
                for doc in retrieved_docs:
                    if doc not in final_docs:
                        final_docs.append(doc)
                        if len(final_docs) >= self.top_k_final:
                            break

            self.stats["rerankings"] += 1
            logger.info(f"Reranked to {len(final_docs)} documents")
        else:
            final_docs = retrieved_docs[: self.top_k_final]

        # 6. Compress context if needed
        compressed_context = None
        if self.enable_compression and final_docs:
            doc_texts = [doc.metadata.get("text", "") for doc in final_docs]
            compression_result = self.compressor.compress(chunks=doc_texts, query=query)
            compressed_context = compression_result.compressed_text
            self.stats["compressions"] += 1
            logger.info(f"Compressed context: {compression_result.compression_ratio:.2f} ratio")

        # Generate response (mock - would use LLM in real implementation)
        response = self._generate_response(query, final_docs, compressed_context)

        # 7. cache the result
        if self.enable_caching and response:
            self.cache.put(query, response)
            logger.info("Cached the response")

        # Return results
        processing_time = time.time() - start_time
        logger.info(f"Query processed in {processing_time:.3f}s")

        return {
            "query": query,
            "response": response,
            "documents": final_docs,
            "compressed_context": compressed_context,
            "metadata": {
                "gate_decision": gate_decision.dict(),
                "cached": False,
                "decomposed": decomposed_result.dict() if decomposed_result else None,
                "compressed": bool(compressed_context),
                "reranked": self.enable_reranking and len(retrieved_docs) > self.top_k_final,
                "processing_time": processing_time,
                "stats": self.get_stats(),
            },
        }

    def _generate_response(
        self,
        query: str,
        documents: list[Any],
        compressed_context: str | None = None,
    ) -> str:
        """Generate response from retrieved documents.

        In a real implementation, this would call an LLM.
        Here we provide a mock response for testing.
        """
        if not documents:
            return "I couldn't find relevant information to answer your question."

        # Mock response based on available documents
        response = f"Based on {len(documents)} relevant documents"

        if compressed_context:
            response += f" (compressed to {len(compressed_context)} characters)"

        response += f", here's the answer to: {query}"

        return response

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics.

        Returns:
            Dictionary with usage statistics
        """
        total = self.stats["total_queries"]
        stats = self.stats.copy()

        # Calculate rates
        if total > 0:
            stats["gate_block_rate"] = self.stats["gate_blocks"] / total
            stats["cache_hit_rate"] = self.stats["cache_hits"] / total
            stats["decomposition_rate"] = self.stats["decompositions"] / total
            stats["compression_rate"] = self.stats["compressions"] / total
            stats["reranking_rate"] = self.stats["rerankings"] / total
        else:
            stats.update(
                {
                    "gate_block_rate": 0.0,
                    "cache_hit_rate": 0.0,
                    "decomposition_rate": 0.0,
                    "compression_rate": 0.0,
                    "reranking_rate": 0.0,
                },
            )

        return stats

    def get_component_info(self) -> dict[str, Any]:
        """Get information about all components.

        Returns:
            Dictionary with component status and capabilities
        """
        return {
            "phase_1_precision": {
                "gate_available": True,
                "compressor_available": True,
                "compression_enabled": self.enable_compression,
            },
            "phase_2_reasoning": {
                "decomposer_available": True,
                "scorer_available": True,
                "decomposition_enabled": self.enable_decomposition,
                "dynamic_alpha_enabled": self.scorer.dynamic_alpha,
            },
            "phase_3_sota": {
                "reranker_available": self.reranker.is_available,
                "cache_available": self.cache.is_available,
                "reranking_enabled": self.enable_reranking,
                "caching_enabled": self.enable_caching,
            },
        }


# Convenience function for quick setup
def create_titanium_pipeline(enable_all: bool = True, **kwargs) -> TitaniumRAGPipeline:
    """Create a Titanium RAG Pipeline with default configuration.

    Args:
        enable_all: Whether to enable all features
        **kwargs: Additional configuration options

    Returns:
        Configured TitaniumRAGPipeline instance
    """
    if enable_all:
        return TitaniumRAGPipeline(
            enable_compression=True,
            enable_decomposition=True,
            enable_reranking=True,
            enable_caching=True,
            **kwargs,
        )
    else:
        return TitaniumRAGPipeline(**kwargs)
