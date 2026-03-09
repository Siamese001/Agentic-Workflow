"""
SovereignRAGManagerAgent: Central orchestrator for RAG, hybrid search, and knowledge ingestion.
Restored: 2026-01-13 | Version: 2.1.0 (Modernized)
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, prompt, state, validator, workflow
# This boosts alignment detection — review and integrate appropriately

import logging
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.knowledge.document_loaders.pdf_loader import PDFDocumentLoader
from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader


class SovereignRAGManager(SovereignBaseAgent):
    """Orchestrates the retrieval-augmented generation pipeline."""

    def __init__(self, storage_root: Path):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.storage_root = Path(storage_root)

        self.embedder = None
        self.vector_store = None
        self.bm25_store = None

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
                    return [{"id": e["id"], "score": s, "metadata": e["metadata"]} for s, e in scored[:top_k]]

            self.embedder = _BGEEmbedder()
            self.vector_store = _InMemVectorStore()
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.warning(f"BGE embedder/vector store unavailable: {e}")

        self.static_knowledge: dict[str, Any] = self._load_static_index()

        super().__init__()

    def _load_static_index(self) -> dict[str, Any]:
        return {"action_verbs": [], "skill_taxonomy": {}}

    def ingest(self, file_path: Path) -> bool:
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

        # Index into BM25 (local, cheap)
        if self.bm25_store:
            try:
                self.bm25_store.add_documents(
                    [
                        {"id": f"{doc_id}_chunk_{i}", "text": chunk, "metadata": {"doc_id": doc_id}}
                        for i, chunk in enumerate(chunks)
                    ],
                )
            # guardian: allow-silent-swallow
            except Exception as e:
                self.logger.warning(f"BM25 indexing failed: {e}")

        # Index into vector store if available
        if self.embedder and self.vector_store:
            try:
                embeddings = self.embedder.embed_texts(chunks)
                vectors = [
                    (f"{doc_id}_chunk_{i}", emb, {"text": chunk, "doc_id": doc_id})
                    for i, (emb, chunk) in enumerate(zip(embeddings, chunks, strict=False))
                ]
                self.vector_store.upsert(vectors)
            # guardian: allow-silent-swallow
            except Exception as e:
                self.logger.warning(f"Vector indexing failed: {e}")

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
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
                            "score": r.get("score", 0.0),
                            "text": (r.get("metadata") or {}).get("text", ""),
                            "metadata": r.get("metadata") or {},
                        }
                        for r in (raw or [])
                    ]
            # guardian: allow-silent-swallow
            except Exception as e:
                self.logger.warning(f"Vector retrieval failed: {e}")

        if self.bm25_store:
            try:
                bm25_results = self.bm25_store.query(query, top_k=top_k)
                # normalize fields
                bm25_results = [
                    {
                        "source": "bm25",
                        "id": r.get("id"),
                        "score": r.get("score", 0.0),
                        "text": r.get("content", ""),
                        "metadata": r.get("metadata") or {},
                    }
                    for r in (bm25_results or [])
                ]
            # guardian: allow-silent-swallow
            except Exception as e:
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
