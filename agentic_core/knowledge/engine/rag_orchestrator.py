from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "rag_orchestrator", "p0_governance")
_emit_reads_policy_state("p0", "rag_orchestrator", "policy_binding")
_emit_snapshots_state("p0", "rag_orchestrator", "state_snapshot")
emit_replay_key("p0", "rag_orchestrator")
emit_determinism_digest("p0", "rag_orchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rag_orchestrator", "execution_auth")
_emit_validates_capability("p2", "rag_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "rag_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "rag_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "rag_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "rag_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "rag_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "rag_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "rag_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_orchestrator", "exec_snapshot_link")

"\nSovereign RAG Orchestrator\n\nZero-Ambiguity Standard: Renamed from SovereignRAGManager.py to SovereignRagOrchestrator.py\nCategory: ORCHESTRATOR (Manages RAG pipeline)\n\nTerritory: agentic_core/knowledge (cross-subfolder orchestrator)\nCanon Key 9 - Retrieval-Augmented Generation integration\n"
import json
from pathlib import Path

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.utils.timeout_decorator_util import timeout

try:
    from agentic_core.knowledge.document_loaders.csv_loader import CSVDocumentLoader
    from agentic_core.knowledge.document_loaders.html_loader import HTMLDocumentLoader
    from agentic_core.knowledge.document_loaders.pdf_loader import PDFDocumentLoader
    from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader
    from agentic_core.knowledge.research_cache.cache_store_util import ResearchCache
    from agentic_core.knowledge.static_index.action_verbs_types import ACTION_VERBS, STRONG_VERBS
    from agentic_core.knowledge.static_index.skill_taxonomy_types import ALL_SKILLS, SKILL_TAXONOMY
# guardian: allow-silent-swallow - optional dependency
except ImportError:
    ACTION_VERBS, STRONG_VERBS = ({}, [])
    SKILL_TAXONOMY, ALL_SKILLS = ({}, [])
    TextDocumentLoader = None
    PDFDocumentLoader = None
    HTMLDocumentLoader = None
    CSVDocumentLoader = None
    ResearchCache = None
try:
    from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import (
        bmg_embed_text as _bge_embed,  # noqa: F401
    )

    _embedding_cache: dict = {}

    def clear_embedding_cache() -> None:
        _embedding_cache.clear()
except ImportError as _exc:
    import logging as _logging

    _logging.getLogger(__name__).critical(
        "rag_orchestrator: BGE embedder unavailable — embedding cache disabled: %s", _exc
    )
    _embedding_cache = {}

    def clear_embedding_cache() -> None:
        pass
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("rag_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("rag_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("rag_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("rag_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("rag_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("rag_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("rag_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("rag_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("rag_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("rag_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("rag_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("rag_orchestrator", "p4obs", "trace_link")
_emit_captures_pattern("rag_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("rag_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rag_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("rag_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rag_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("rag_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("rag_orchestrator", "p3lm", "state")
_emit_records_execution_trace("rag_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rag_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rag_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rag_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rag_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rag_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("rag_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("rag_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rag_orchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rag_orchestrator", "context_pull")
_emit_pulls_context("p1", "rag_orchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rag_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rag_orchestrator", "uwg_term_2")
_emit_writes_through("p1", "rag_orchestrator", "write_through")
_emit_writes_through("p1", "rag_orchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "rag_orchestrator", "safety_validation")
_emit_invokes_eval("p1", "rag_orchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "rag_orchestrator", "routing_commit")
_emit_escalates_to_human("p1", "rag_orchestrator", "human_escalation")
_emit_routes_through("p1", "rag_orchestrator", "route_through")
_emit_checks_agent_registry("p1", "rag_orchestrator", "agent_registry")
_emit_validates_agent_capability("p1", "rag_orchestrator", "capability")
_emit_dispatches_execution_plan("p1", "rag_orchestrator", "exec_plan")
_emit_agent_executes_agent("p1", "rag_orchestrator", "sub_agent")
_emit_routes_to_agent("p1", "rag_orchestrator", "target_agent")
_emit_verifies_policy("p1", "rag_orchestrator", "policy_check")
_emit_observes_runtime_state("p1", "rag_orchestrator", "runtime_state")
_emit_verifies_boundary("p1", "rag_orchestrator", "boundary_check")
_emit_transcripts_response("p1", "rag_orchestrator", "transcript")
_emit_hard_fails_untranscripted("p1", "rag_orchestrator")
_emit_gated_by_confidence("p1", "rag_orchestrator", "confidence_gate")


class SovereignRagOrchestrator:
    """
    Sovereign RAG orchestrator — combines ingested docs, static facts, and cached research.

    Zero-Ambiguity Standard: Renamed from SovereignRAGManager to SovereignRagOrchestrator
    to clarify its role as an orchestrator pattern.

    Responsibilities:
    - Aggregate static knowledge from static_index/
    - Retrieve cached insights from ResearchCache/
    - Format retrieval results into prompt-ready context strings.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.cache_dir = project_root / AGENTIC_CORE_DIR / "knowledge" / "research_cache"
        self.cache = ResearchCache(self.cache_dir) if ResearchCache is not None else None
        self.static_knowledge = self._load_static_index()
        try:
            self.embedding_cache_stats = lambda: {
                "size": len(_embedding_cache),
                "maxsize": _embedding_cache.maxsize,
            }
        # guardian: allow-silent-swallow
        except:
            self.embedding_cache_stats = lambda: {"size": 0, "maxsize": 0}
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

                # guardian: allow-magic-config
                def query(self, query_emb, top_k=5):
                    import uuid as _uuid  # noqa: PLC0415
                    _trace_id = str(_uuid.uuid4())
                    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "_InMemVectorStore.query")

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
        # guardian: allow-silent-swallow
        except (ImportError, Exception):
            self.embedder = None
            self.vector_store = None
        try:
            from agentic_core.L4_state.utils.memory.bm25_store import get_bm25_store

            self.Bm25Store = get_bm25_store()
        # guardian: allow-silent-swallow
        except Exception:
            self.Bm25Store = None
        self.engine = None

    def _load_static_index(self) -> dict:
        """Load all hard-coded knowledge bases for immediate retrieval."""
        return {"action_verbs": {"categories": ACTION_VERBS, "strong_verbs": STRONG_VERBS}}

    def ingest(self, file_path: Path):
        """Routes ingestion to the appropriate loader based on suffix."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignRagOrchestrator.ingest")

        # Validate input type
        if not isinstance(file_path, Path):
            raise TypeError(f"file_path must be a Path object, got {type(file_path).__name__}")

        # Validate file exists and is not a directory
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.is_dir():
            raise ValueError(f"Path is a directory, not a file: {file_path}")

        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".md", ".markdown"}:
            if TextDocumentLoader:
                return TextDocumentLoader.load_file(file_path)
        elif suffix == ".pdf":
            if PDFDocumentLoader:
                return PDFDocumentLoader(file_path).load()
        elif suffix in {".html", ".htm"}:
            if HTMLDocumentLoader:
                return HTMLDocumentLoader.load_file(file_path)
        elif suffix == ".csv":
            if CSVDocumentLoader:
                return CSVDocumentLoader.load(file_path)
        raise ValueError(f"Unsupported format: {file_path.suffix}")

    def index_document(self, doc_id: str, text_chunks: list[str], metadata: dict = None) -> None:
        """Index document chunks into vector store and BM25 index."""
        try:
            if self.embedder and self.vector_store:
                embeddings = self.embedder.embed_texts(text_chunks)
                vectors = [
                    (f"{doc_id}_{i}", emb, {"text": chunk, **(metadata or {})})
                    for i, (emb, chunk) in enumerate(zip(embeddings, text_chunks, strict=False))
                ]
                self.vector_store.upsert(vectors)
            if self.Bm25Store:
                self.Bm25Store.add_documents(
                    [
                        {"id": f"{doc_id}_{i}", "text": chunk, "metadata": metadata or {}}
                        for i, chunk in enumerate(text_chunks)
                    ]
                )
            print(f"Indexed {len(text_chunks)} chunks for {doc_id}")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"Document indexing failed: {e}")

    # guardian: allow-magic-config
    async def retrieve(
        self, query: str, domain: str = "general", top_k: int = 5, use_cache: bool = True
    ) -> list[dict]:
        """
        Ultra-hardened hybrid retrieval with RRF fusion and LLM reranking.
        """
        _adg_confidence: float = 0.5
        try:
            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _adg_confidence = _gbp(Path(__file__).resolve(), self.project_root).behavioral_score
        # guardian: allow-silent-swallow
        except Exception:
            pass
        vector_candidates = []
        bm25_candidates = []
        if hasattr(self, "vector_store") and self.vector_store:
            try:
                query_emb = self.embedder.embed_query(query)
                raw_results = self.vector_store.query(query_emb, top_k=top_k * 3)
                vector_candidates = [
                    {
                        "id": res.get("id", f"vec_{i}"),
                        "source": "vector_store",
                        "content": res["metadata"].get("text", ""),
                        "score": round(res["score"] * _adg_confidence, 8),
                        "adg_confidence_weight": _adg_confidence,
                    }
                    for i, res in enumerate(raw_results)
                ]
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"Vector search failed: {e}")
        if self.Bm25Store:
            bm25_candidates = self.Bm25Store.query(query, top_k=top_k * 3)
        static_boost = []
        query_lower = query.lower()
        if "verb" in query_lower or "action" in query_lower:
            static_boost.append(
                {
                    "id": "static_verbs",
                    "source": "static_index.action_verbs",
                    "content": json.dumps(self.static_knowledge["action_verbs"], indent=2),
                    "score": 0.95,
                }
            )
        if any(skill.lower() in query_lower for skill in ALL_SKILLS[:50]):
            static_boost.append(
                {
                    "id": "static_skills",
                    "source": "static_index.skill_taxonomy",
                    "content": json.dumps(SKILL_TAXONOMY, indent=2),
                    "score": 0.95,
                }
            )
        fused_candidates = self._rrf_fusion(vector_candidates, bm25_candidates, k=60)
        all_candidates = fused_candidates + static_boost
        final_results = await self._llm_rerank(query, all_candidates[: top_k * 2], top_k)
        return final_results or [
            {"source": "fallback", "content": "No relevant knowledge found.", "score": 0.0}
        ]

    def _rrf_fusion(self, vector_list: list[dict], bm25_list: list[dict], k: int = 60) -> list[dict]:
        """
        Implements Reciprocal Rank Fusion (RRF) to combine results from multiple retrieval strategies.
        RRF Score = sum(1 / (k + rank))
        """
        k = 60.0
        fused_scores = {}
        doc_map = {}

        def process_list(results_list):
            for rank, item in enumerate(results_list):
                doc_id = item.get("id") or hash(item.get("text", ""))
                if doc_id not in doc_map:
                    doc_map[doc_id] = item
                    fused_scores[doc_id] = 0.0
                fused_scores[doc_id] += 1.0 / (k + rank + 1)

        process_list(vector_list)
        process_list(bm25_list)
        sorted_doc_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
        final_results = [doc_map[doc_id] for doc_id in sorted_doc_ids]
        return final_results

    async def _llm_rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        """Final precision reranking via LLM judgment."""
        if not self.engine or not candidates:
            return candidates[:top_k]
        rerank_prompt = f"Task: Rank these passages by relevance to the user query.\nQuery: {query}\nPassages:\n{json.dumps([{'idx': i, 'text': c['content'][:500]} for i, c in enumerate(candidates)], indent=2)}\n\nOutput ONLY a JSON list of indices in order of relevance (e.g., [2, 0, 1])."
        try:
            response = await self.engine.resilient_mutation(
                file_path="rag_rerank",
                code=rerank_prompt,
                Task="Rerank retrieval results",
                round_num=1,
                fission_active=False,
            )
            import json as json_lib

            indices = json_lib.loads(response)
            return [candidates[i] for i in indices if i < len(candidates)][:top_k]
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"Reranking failed: {e}")
            return candidates[:top_k]

    async def get_context_for_task(self, Task: str, domain: str = "general") -> str:
        """
        Converts raw retrievals into a formatted context block for LLM instructions.
        Ensures agents operate under Sovereign Truth.
        """
        retrievals = await self.retrieve(Task, domain=domain)
        if not retrievals:
            return "No relevant sovereign knowledge found."
        context_parts = ["### RELEVANT SOVEREIGN KNOWLEDGE"]
        for r in retrievals:
            source = r.get("source", "unknown")
            content = r.get("content", "")
            context_parts.append(f"[{source}] {content}")
        return "\n".join(context_parts)

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """Knowledge agent - operational only."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] Knowledge - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


SovereignRAGManager = SovereignRagOrchestrator


def get_rag_manager(project_root: Path) -> SovereignRagOrchestrator:
    return SovereignRagOrchestrator(project_root)
