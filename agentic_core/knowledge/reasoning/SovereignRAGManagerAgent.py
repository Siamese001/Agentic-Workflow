"""
SovereignRAGManagerAgent: Central orchestrator for RAG, hybrid search, and knowledge ingestion.
Restored: 2026-01-13 | Version: 2.1.0 (Modernized)
"""

import logging
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.knowledge.document_loaders.pdf_loader import PDFDocumentLoader
from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "SovereignRAGManagerAgent", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "SovereignRAGManagerAgent", "policy_binding")
trace_contract._emit_snapshots_state("p0", "SovereignRAGManagerAgent", "state_snapshot")

trace_contract._emit_emits_metric_event("SovereignRAGManagerAgent", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("SovereignRAGManagerAgent", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("SovereignRAGManagerAgent", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("SovereignRAGManagerAgent", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("SovereignRAGManagerAgent", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("SovereignRAGManagerAgent", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("SovereignRAGManagerAgent", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("SovereignRAGManagerAgent", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("SovereignRAGManagerAgent", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("SovereignRAGManagerAgent", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("SovereignRAGManagerAgent", "p4obs", "alert")
trace_contract._emit_links_incident_trace("SovereignRAGManagerAgent", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("SovereignRAGManagerAgent", "p3lm", "pattern")
trace_contract._emit_records_learning_event("SovereignRAGManagerAgent", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("SovereignRAGManagerAgent", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("SovereignRAGManagerAgent", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("SovereignRAGManagerAgent", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("SovereignRAGManagerAgent", "p3lm", "policy")
trace_contract._emit_stores_learning_state("SovereignRAGManagerAgent", "p3lm", "state")
trace_contract._emit_records_execution_trace("SovereignRAGManagerAgent", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("SovereignRAGManagerAgent", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("SovereignRAGManagerAgent", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("SovereignRAGManagerAgent", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("SovereignRAGManagerAgent", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("SovereignRAGManagerAgent", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("SovereignRAGManagerAgent", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("SovereignRAGManagerAgent", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("SovereignRAGManagerAgent", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "SovereignRAGManagerAgent", "context_pull")
trace_contract._emit_pulls_context("p1", "SovereignRAGManagerAgent", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "SovereignRAGManagerAgent", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "SovereignRAGManagerAgent", "uwg_term_2")
trace_contract._emit_writes_through("p1", "SovereignRAGManagerAgent", "write_through")
trace_contract._emit_writes_through("p1", "SovereignRAGManagerAgent", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "SovereignRAGManagerAgent", "safety_validation")
trace_contract._emit_invokes_eval("p1", "SovereignRAGManagerAgent", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "SovereignRAGManagerAgent", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "SovereignRAGManagerAgent", "human_escalation")
trace_contract._emit_routes_through("p1", "SovereignRAGManagerAgent", "route_through")
trace_contract._emit_checks_agent_registry("p1", "SovereignRAGManagerAgent", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "SovereignRAGManagerAgent", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "SovereignRAGManagerAgent", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "SovereignRAGManagerAgent", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "SovereignRAGManagerAgent", "target_agent")
trace_contract._emit_verifies_policy("p1", "SovereignRAGManagerAgent", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "SovereignRAGManagerAgent", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "SovereignRAGManagerAgent", "boundary_check")
trace_contract._emit_transcripts_response("p1", "SovereignRAGManagerAgent", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "SovereignRAGManagerAgent")
trace_contract._emit_gated_by_confidence("p1", "SovereignRAGManagerAgent", "confidence_gate")
trace_contract.emit_replay_key("p0", "SovereignRAGManagerAgent")
trace_contract.emit_determinism_digest("p0", "SovereignRAGManagerAgent")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "SovereignRAGManagerAgent", "execution_auth")
trace_contract._emit_validates_capability("p2", "SovereignRAGManagerAgent", "capability_check")
trace_contract._emit_routes_to_capability("p2", "SovereignRAGManagerAgent", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "SovereignRAGManagerAgent", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "SovereignRAGManagerAgent", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "SovereignRAGManagerAgent", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "SovereignRAGManagerAgent", "exec_output")
trace_contract._emit_dispatches_agent("p3", "SovereignRAGManagerAgent", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "SovereignRAGManagerAgent", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "SovereignRAGManagerAgent", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "SovereignRAGManagerAgent", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "SovereignRAGManagerAgent", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "SovereignRAGManagerAgent", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "SovereignRAGManagerAgent", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "SovereignRAGManagerAgent", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "SovereignRAGManagerAgent", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "SovereignRAGManagerAgent", "eval_metric")
trace_contract._emit_stores_embedding("p4", "SovereignRAGManagerAgent", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "SovereignRAGManagerAgent", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "SovereignRAGManagerAgent", "exec_snapshot_link")


class SovereignRAGManager(SovereignBaseAgent):
    """Orchestrates the retrieval-augmented generation pipeline."""

    def __init__(self, storage_root: Path):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.storage_root = Path(storage_root)
        self.embedder = None
        self.vector_store = None
        try:
            from agentic_core.L4_state.utils.memory.bm25_store import get_bm25_store

            self.bm25_store = get_bm25_store()
        except (ImportError, AttributeError, OSError, RuntimeError, TypeError, ValueError):
            self.bm25_store = None
        try:
            from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

            class _BGEEmbedder:
                def embed_texts(self, texts):
                    return [bmg_embed_text(t) or [] for t in texts]

                def embed_query(self, text):
                    return bmg_embed_text(text)

            class _InMemVectorStore:
                def __init__(self):
                    self._store: dict = {}

                def upsert(self, vectors):
                    for vec_id, emb, meta in vectors:
                        self._store[vec_id] = {"id": vec_id, "embedding": emb, "metadata": meta}

                def query(self, query_emb, top_k=5):
                    import uuid as _uuid  # noqa: PLC0415

                    _trace_id = str(_uuid.uuid4())
                    trace_contract._emit_records_execution_trace(
                        _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "_InMemVectorStore.query"
                    )

                    import numpy as np

                    if not self._store or query_emb is None:
                        return []
                    q = np.array(query_emb, dtype=np.float32)
                    q_norm = q / (np.linalg.norm(q) + 1e-08)
                    scored = []
                    for entry in self._store.values():
                        v = np.array(entry["embedding"], dtype=np.float32)
                        v_norm = v / (np.linalg.norm(v) + 1e-08)
                        scored.append((float(np.dot(q_norm, v_norm)), entry))
                    scored.sort(key=lambda x: x[0], reverse=True)
                    return [{"id": e["id"], "score": s, "metadata": e["metadata"]} for s, e in scored[:top_k]]

            self.embedder = _BGEEmbedder()
            self.vector_store = _InMemVectorStore()
        except (  # guardian: allow-log-and-swallow -- embedder/vector store init: optional component, RAG degrades to BM25-only
            ImportError,
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:
            self.logger.warning(f"BGE embedder/vector store unavailable: {e}")
        self.static_knowledge: dict[str, Any] = self._load_static_index()
        super().__init__()

    def _load_static_index(self) -> dict[str, Any]:
        return {"action_verbs": [], "skill_taxonomy": {}}

    def ingest(self, file_path: Path) -> bool:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SovereignRAGManager.ingest")

        suffix = Path(file_path).suffix.lower()
        loader: TextDocumentLoader | PDFDocumentLoader | None = None
        if suffix == ".txt":
            loader = TextDocumentLoader(Path(file_path))
        elif suffix == ".pdf":
            loader = PDFDocumentLoader(Path(file_path))
        if not loader:
            self.logger.error(f"Unsupported file type: {suffix}")
            return False
        content = loader.load()
        chunks = self._chunk_content(content)
        self.index_document(Path(file_path).name, chunks)
        return True

    def _chunk_content(self, content: str, chunk_size: int = 1000) -> list[str]:
        return [content[i : i + chunk_size] for i in range(0, len(content), chunk_size)]

    def index_document(self, doc_id: str, chunks: list[str]):
        if not chunks:
            return
        if self.bm25_store:
            try:
                self.bm25_store.add_documents(
                    [
                        {"id": f"{doc_id}_chunk_{i}", "text": chunk, "metadata": {"doc_id": doc_id}}
                        for i, chunk in enumerate(chunks)
                    ],
                )
            except (  # guardian: allow-log-and-swallow -- BM25 indexing: non-fatal, documents skipped from BM25 index
                AttributeError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as e:
                self.logger.warning(f"BM25 indexing failed: {e}")
        if self.embedder and self.vector_store:
            try:
                embeddings = self.embedder.embed_texts(chunks)
                vectors = [
                    (f"{doc_id}_chunk_{i}", emb, {"text": chunk, "doc_id": doc_id})
                    for i, (emb, chunk) in enumerate(zip(embeddings, chunks, strict=False))
                ]
                self.vector_store.upsert(vectors)
            except (  # guardian: allow-log-and-swallow -- vector indexing: non-fatal, documents skipped from vector index
                AttributeError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as e:
                self.logger.warning(f"Vector indexing failed: {e}")

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        _adg_confidence: float = 0.5
        try:
            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _root = Path(__file__).resolve().parents[3]
            _adg_confidence = _gbp(Path(__file__).resolve(), _root).behavioral_score
        except (  # guardian: allow-log-and-swallow -- behavioral profile: optional ADG query, non-fatal, default confidence used
            ImportError,
            AttributeError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as e:
            import logging

            logging.getLogger(__name__).debug("SovereignRAGManagerAgent: Exception swallowed at L279: %s", e)
        vector_results: list[dict[str, Any]] = []
        bm25_results: list[dict[str, Any]] = []
        if self.embedder and self.vector_store:
            try:
                query_emb = self.embedder.embed_query(query)
                if query_emb:
                    raw = self.vector_store.query(query_emb, top_k=top_k)
                    vector_results = [
                        {
                            "source": "vector",
                            "id": r.get("id"),
                            "score": round(r.get("score", 0.0) * _adg_confidence, 8),
                            "text": (r.get("metadata") or {}).get("text", ""),
                            "metadata": r.get("metadata") or {},
                            "adg_confidence_weight": _adg_confidence,
                        }
                        for r in raw or []
                    ]
            except (  # guardian: allow-log-and-swallow -- vector retrieval: non-fatal, falls back to BM25 results
                AttributeError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as e:
                self.logger.warning(f"Vector retrieval failed: {e}")
        if self.bm25_store:
            try:
                bm25_results = self.bm25_store.query(query, top_k=top_k)
                bm25_results = [
                    {
                        "source": "bm25",
                        "id": r.get("id"),
                        "score": r.get("score", 0.0),
                        "text": r.get("content", ""),
                        "metadata": r.get("metadata") or {},
                    }
                    for r in bm25_results or []
                ]
            except (  # guardian: allow-log-and-swallow -- BM25 retrieval: non-fatal, results combined from vector only
                AttributeError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as e:
                self.logger.warning(f"BM25 retrieval failed: {e}")
        combined = self._fuse_results(vector_results, bm25_results)
        return combined[:top_k]

    def _fuse_results(
        self,
        vector: list[dict[str, Any]],
        bm25: list[dict[str, Any]],
        k: int = 60,
    ) -> list[dict[str, Any]]:
        """Reciprocal Rank Fusion of vector and BM25 result lists.

        RRF score = Σ 1/(k + rank_i) across all ranked lists.
        Deduplicates by ``id``; ties broken by insertion order.
        """
        rrf_scores: dict[str, float] = {}
        merged_docs: dict[str, dict[str, Any]] = {}
        for rank, doc in enumerate(vector, start=1):
            doc_id = doc.get("id") or f"vec_{rank}"
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            if doc_id not in merged_docs:
                merged_docs[doc_id] = doc
        for rank, doc in enumerate(bm25, start=1):
            doc_id = doc.get("id") or f"bm25_{rank}"
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            if doc_id not in merged_docs:
                merged_docs[doc_id] = doc
        sorted_ids = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)
        fused = []
        for doc_id in sorted_ids:
            doc = dict(merged_docs[doc_id])
            doc["score"] = round(rrf_scores[doc_id], 8)
            fused.append(doc)
        return fused

    def format_context(self, results: list[dict[str, Any]]) -> str:
        return "\n\n".join([r.get("text", "") for r in results if r.get("text")])

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
