from __future__ import annotations

"""
Sovereign RAG Orchestrator

Zero-Ambiguity Standard: Renamed from SovereignRAGManager.py to SovereignRagOrchestrator.py
Category: ORCHESTRATOR (Manages RAG pipeline)

Territory: agentic_core/knowledge (cross-subfolder orchestrator)
Canon Key 9 - Retrieval-Augmented Generation integration
"""

import json
from pathlib import Path

from agentic_core.utils.timeout_decorator_util import timeout

# Internal imports referencing the mandated structure
try:
    from agentic_core.semantic_memory.embeddings.core_embedder import (
        _embedding_cache,
        clear_embedding_cache,  # noqa: F401
    )

    from agentic_core.knowledge.document_loaders.csv_loader import CSVDocumentLoader
    from agentic_core.knowledge.document_loaders.html_loader import HTMLDocumentLoader
    from agentic_core.knowledge.document_loaders.pdf_loader import PDFDocumentLoader
    from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader
    from agentic_core.knowledge.research_cache.cache_store_util import ResearchCache
    from agentic_core.knowledge.static_index.action_verbs_types import ACTION_VERBS, STRONG_VERBS
    from agentic_core.knowledge.static_index.skill_taxonomy_types import ALL_SKILLS, SKILL_TAXONOMY
except ImportError:
    # Fallback to avoid mission failure if sub-modules are mid-relocation
    ACTION_VERBS, STRONG_VERBS = {}, []
    SKILL_TAXONOMY, ALL_SKILLS = {}, []
    TextDocumentLoader = None
    PDFDocumentLoader = None
    HTMLDocumentLoader = None
    CSVDocumentLoader = None
    ResearchCache = None
    _embedding_cache = {}
    clear_embedding_cache = lambda: None  # noqa: E731


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
        self.cache_dir = project_root / "agentic_core" / "knowledge" / "research_cache"
        self.cache = ResearchCache(self.cache_dir) if ResearchCache is not None else None
        self.static_knowledge = self._load_static_index()

        # Optional: Expose embedding cache stats
        try:
            self.embedding_cache_stats = lambda: {
                "size": len(_embedding_cache),
                "maxsize": _embedding_cache.maxsize,
            }
        except:
            self.embedding_cache_stats = lambda: {"size": 0, "maxsize": 0}

        # BGE-m3 embedder + in-memory vector store (replaces ghost semantic_memory imports)
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

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
                    import numpy as np
                    if not self._store or query_emb is None:
                        return []
                    q = np.array(query_emb, dtype=np.float32)
                    q_norm = q / (np.linalg.norm(q) + 1e-8)
                    scored = []
                    for entry in self._store.values():
                        v = np.array(entry["embedding"], dtype=np.float32)
                        v_norm = v / (np.linalg.norm(v) + 1e-8)
                        scored.append((float(np.dot(q_norm, v_norm)), entry))
                    scored.sort(key=lambda x: x[0], reverse=True)
                    return [
                        {"id": e["id"], "score": s, "metadata": e["metadata"]}
                        for s, e in scored[:top_k]
                    ]

            self.embedder = _BGEEmbedder()
            self.vector_store = _InMemVectorStore()
            self.Bm25Store = None
        except (ImportError, Exception):
            # Vector search unavailable - will fall back to keyword/static only
            self.embedder = None
            self.vector_store = None
            self.Bm25Store = None

        # Optional: Initialize LLM engine for reranking
        self.engine = None

    def _load_static_index(self) -> dict:
        """Load all hard-coded knowledge bases for immediate retrieval."""
        return {
            "action_verbs": {
                "categories": ACTION_VERBS,
                "strong_verbs": STRONG_VERBS,
            },
        }

    def ingest(self, file_path: Path):
        """Routes ingestion to the appropriate loader based on suffix."""
        suffix = file_path.suffix.lower()
        if suffix in {".txt", ".md", ".markdown"}:
            if TextDocumentLoader:
                return TextDocumentLoader.load(file_path)
        elif suffix == ".pdf":
            if PDFDocumentLoader:
                return PDFDocumentLoader.load(file_path)
        elif suffix in {".html", ".htm"}:
            if HTMLDocumentLoader:
                return HTMLDocumentLoader.load(file_path)
        elif suffix == ".csv":
            # Return structured records for tabular ingestion
            if CSVDocumentLoader:
                return CSVDocumentLoader.load(file_path)
        raise ValueError(f"Unsupported format: {file_path.suffix}")

    def index_document(self, doc_id: str, text_chunks: list[str], metadata: dict = None) -> None:
        """Index document chunks into vector store and BM25 index."""
        try:
            # Vector indexing
            if self.embedder and self.vector_store:
                embeddings = self.embedder.embed_texts(text_chunks)
                vectors = [
                    (f"{doc_id}_{i}", emb, {"text": chunk, **(metadata or {})})
                    for i, (emb, chunk) in enumerate(zip(embeddings, text_chunks, strict=False))
                ]
                self.vector_store.upsert(vectors)

            # BM25 indexing
            if self.Bm25Store:
                self.Bm25Store.add_documents(
                    [
                        {"id": f"{doc_id}_{i}", "text": chunk, "metadata": metadata or {}}
                        for i, chunk in enumerate(text_chunks)
                    ],
                )
            print(f"Indexed {len(text_chunks)} chunks for {doc_id}")
        except Exception as e:
            print(f"Document indexing failed: {e}")

    async def retrieve(
        self,
        query: str,
        domain: str = "general",
        top_k: int = 5,
        use_cache: bool = True,
    ) -> list[dict]:
        """
        Ultra-hardened hybrid retrieval with RRF fusion and LLM reranking.
        """
        # 1. Parallel hybrid retrieval
        vector_candidates = []
        bm25_candidates = []

        # Vector Search
        if hasattr(self, "vector_store") and self.vector_store:
            try:
                query_emb = self.embedder.embed_query(query)
                raw_results = self.vector_store.query(query_emb, top_k=top_k * 3)
                vector_candidates = [
                    {
                        "id": res.get("id", f"vec_{i}"),
                        "source": "vector_store",
                        "content": res["metadata"].get("text", ""),
                        "score": res["score"],
                    }
                    for i, res in enumerate(raw_results)
                ]
            except Exception as e:
                print(f"Vector search failed: {e}")

        # BM25 Search
        if self.Bm25Store:
            bm25_candidates = self.Bm25Store.query(query, top_k=top_k * 3)

        # Static domain boost: Prioritize SSOT taxonomies
        static_boost = []
        query_lower = query.lower()
        if "verb" in query_lower or "action" in query_lower:
            static_boost.append(
                {
                    "id": "static_verbs",
                    "source": "static_index.action_verbs",
                    "content": json.dumps(self.static_knowledge["action_verbs"], indent=2),
                    "score": 0.95,
                },
            )
        if any(skill.lower() in query_lower for skill in ALL_SKILLS[:50]):
            static_boost.append(
                {
                    "id": "static_skills",
                    "source": "static_index.skill_taxonomy",
                    "content": json.dumps(SKILL_TAXONOMY, indent=2),
                    "score": 0.95,
                },
            )

        # 2. Reciprocal Rank Fusion (RRF)
        fused_candidates = self._rrf_fusion(vector_candidates, bm25_candidates, k=60)

        # Add static boost to fused results
        all_candidates = fused_candidates + static_boost

        # 3. Final LLM reranking for high precision
        final_results = await self._llm_rerank(query, all_candidates[: top_k * 2], top_k)

        return final_results or [
            {"source": "fallback", "content": "No relevant knowledge found.", "score": 0.0},
        ]

    def _rrf_fusion(self, vector_list: list[dict], bm25_list: list[dict], k: int = 60) -> list[dict]:
        """
        Implements Reciprocal Rank Fusion (RRF) to combine results from multiple retrieval strategies.
        RRF Score = sum(1 / (k + rank))
        """
        k = 60.0  # Standard RRF constant
        fused_scores = {}
        doc_map = {}

        # Helper to process a result list
        def process_list(results_list):
            for rank, item in enumerate(results_list):
                doc_id = item.get("id") or hash(item.get("text", ""))
                if doc_id not in doc_map:
                    doc_map[doc_id] = item
                    fused_scores[doc_id] = 0.0
                fused_scores[doc_id] += 1.0 / (k + rank + 1)

        process_list(vector_list)
        process_list(bm25_list)

        # Sort by RRF score descending
        sorted_doc_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)

        # Reconstruct list
        final_results = [doc_map[doc_id] for doc_id in sorted_doc_ids]

        return final_results

    async def _llm_rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        """Final precision reranking via LLM judgment."""
        if not self.engine or not candidates:
            return candidates[:top_k]

        rerank_prompt = f"""Task: Rank these passages by relevance to the user query.
Query: {query}
Passages:
{json.dumps([{"idx": i, "text": c["content"][:500]} for i, c in enumerate(candidates)], indent=2)}

Output ONLY a JSON list of indices in order of relevance (e.g., [2, 0, 1])."""

        try:
            response = await self.engine.resilient_mutation(
                file_path="rag_rerank",
                code=rerank_prompt,
                Task="Rerank retrieval results",
                round_num=1,
                fission_active=False,
            )
            # Extract indices from JSON response
            import json as json_lib

            indices = json_lib.loads(response)
            return [candidates[i] for i in indices if i < len(candidates)][:top_k]
        except Exception as e:
            print(f"Reranking failed: {e}")
            return candidates[:top_k]

    def get_context_for_task(self, Task: str, domain: str = "general") -> str:
        """
        Converts raw retrievals into a formatted context block for LLM instructions.
        Ensures agents operate under Sovereign Truth.
        """
        retrievals = self.retrieve(Task, domain=domain)
        if not retrievals:
            return "No relevant sovereign knowledge found."

        context_parts = ["### RELEVANT SOVEREIGN KNOWLEDGE"]
        for r in retrievals:
            r["source"]
            r["content"]

        return "\n".join(context_parts)

    @timeout(300)
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


# Backward compatibility alias
SovereignRAGManager = SovereignRagOrchestrator


def get_rag_manager(project_root: Path) -> SovereignRagOrchestrator:
    return SovereignRagOrchestrator(project_root)
