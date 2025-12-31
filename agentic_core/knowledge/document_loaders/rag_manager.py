# Sovereign RAG Manager
# Territory: agentic_core/knowledge (cross-subfolder orchestrator)
# Canon Key 9 - Retrieval-Augmented Generation integration

import json
from pathlib import Path
from typing import List, Dict, Optional

# Internal imports referencing the mandated structure
try:
    from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader
    from agentic_core.knowledge.document_loaders.pdf_loader import PDFDocumentLoader
    from agentic_core.knowledge.document_loaders.html_loader import HTMLDocumentLoader
    from agentic_core.knowledge.document_loaders.csv_loader import CSVDocumentLoader
    from agentic_core.knowledge.static_index.action_verbs import ACTION_VERBS, STRONG_VERBS
    from agentic_core.knowledge.static_index.skill_taxonomy import SKILL_TAXONOMY, ALL_SKILLS
    from agentic_core.knowledge.research_cache.cache_store import ResearchCache
except ImportError:
    # Fallback to avoid mission failure if sub-modules are mid-relocation
    ACTION_VERBS, STRONG_VERBS = {}, []
    SKILL_TAXONOMY, ALL_SKILLS = {}, []
    TextDocumentLoader = None
    PDFDocumentLoader = None
    HTMLDocumentLoader = None
    CSVDocumentLoader = None

class SovereignRAGManager:
    """
    Sovereign RAG orchestrator — combines ingested docs, static facts, and cached research.

    Responsibilities:
    - Aggregate static knowledge from static_index/
    - Retrieve cached insights from research_cache/
    - Format retrieval results into prompt-ready context strings.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.cache_dir = project_root / "agentic_core" / "knowledge" / "research_cache"
        self.cache = ResearchCache(self.cache_dir)
        self.static_knowledge = self._load_static_index()
        
        # Optional: Initialize vector store, embedder, and BM25 if available
        try:
            from agentic_core.semantic_memory.embeddings.gemini_embedder import GeminiEmbedder
            from agentic_core.semantic_memory.store.pinecone_store import PineconeVectorStore
            from agentic_core.semantic_memory.store.bm25_store import get_bm25_store
            self.embedder = GeminiEmbedder()
            self.vector_store = PineconeVectorStore()
            self.bm25_store = get_bm25_store()
        except (ImportError, ValueError):
            # Vector search unavailable - will fall back to keyword/static only
            self.embedder = None
            self.vector_store = None
            self.bm25_store = None
        
        # Optional: Initialize LLM engine for reranking
        self.engine = None

    def _load_static_index(self) -> Dict:
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

    def index_document(self, doc_id: str, text_chunks: List[str], metadata: dict = None) -> None:
        """Index document chunks into vector store and BM25 index."""
        try:
            # Vector indexing
            if self.embedder and self.vector_store:
                embeddings = self.embedder.embed_texts(text_chunks)
                vectors = [
                    (f"{doc_id}_{i}", emb, {"text": chunk, **(metadata or {})})
                    for i, (emb, chunk) in enumerate(zip(embeddings, text_chunks))
                ]
                self.vector_store.upsert(vectors)
            
            # BM25 indexing
            if self.bm25_store:
                self.bm25_store.add_documents([
                    {"id": f"{doc_id}_{i}", "text": chunk, "metadata": metadata or {}}
                    for i, chunk in enumerate(text_chunks)
                ])
            print(f"Indexed {len(text_chunks)} chunks for {doc_id}")
        except Exception as e:
            print(f"Document indexing failed: {e}")

    async def retrieve(
        self,
        query: str,
        domain: str = "general",
        top_k: int = 5,
        use_cache: bool = True,
    ) -> List[Dict]:
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
        if self.bm25_store:
            bm25_candidates = self.bm25_store.query(query, top_k=top_k * 3)

        # Static domain boost: Prioritize SSOT taxonomies
        static_boost = []
        query_lower = query.lower()
        if "verb" in query_lower or "action" in query_lower:
            static_boost.append({
                "id": "static_verbs",
                "source": "static_index.action_verbs",
                "content": json.dumps(self.static_knowledge["action_verbs"], indent=2),
                "score": 0.95
            })
        if any(skill.lower() in query_lower for skill in ALL_SKILLS[:50]):
            static_boost.append({
                "id": "static_skills",
                "source": "static_index.skill_taxonomy",
                "content": json.dumps(SKILL_TAXONOMY, indent=2),
                "score": 0.95
            })

        # 2. Reciprocal Rank Fusion (RRF)
        fused_candidates = self._rrf_fusion(vector_candidates, bm25_candidates, k=60)
        
        # Add static boost to fused results
        all_candidates = fused_candidates + static_boost

        # 3. Final LLM reranking for high precision
        final_results = await self._llm_rerank(query, all_candidates[:top_k * 2], top_k)

        return final_results or [{"source": "fallback", "content": "No relevant knowledge found.", "score": 0.0}]

    def _rrf_fusion(self, vector_list: List[Dict], bm25_list: List[Dict], k: int = 60) -> List[Dict]:
        """Reciprocal Rank Fusion — combines multiple retrieval scores."""
        scores = {}
        
        for rank, item in enumerate(vector_list):
            item_id = item.get("id", f"vec_{rank}")
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank)
            
        for rank, item in enumerate(bm25_list):
            item_id = item.get("id", f"bm25_{rank}")
            scores[item_id] = scores.get(item_id, 0) + 1 / (k + rank)
            
        # Map IDs back to full document objects
        all_items = {item.get("id", f"item_{i}"): item for i, item in enumerate(vector_list + bm25_list)}
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # Update scores with RRF scores
        result = []
        for doc_id in sorted_ids:
            if doc_id in all_items:
                item = all_items[doc_id].copy()
                item["score"] = scores[doc_id]
                result.append(item)
        
        return result

    async def _llm_rerank(self, query: str, candidates: List[Dict], top_k: int) -> List[Dict]:
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
                task="Rerank retrieval results",
                round_num=1,
                fission_active=False
            )
            # Extract indices from JSON response
            import json as json_lib
            indices = json_lib.loads(response)
            return [candidates[i] for i in indices if i < len(candidates)][:top_k]
        except Exception as e:
            print(f"Reranking failed: {e}")
            return candidates[:top_k]

    def get_context_for_task(self, task: str, domain: str = "general") -> str:
        """
        Converts raw retrievals into a formatted context block for LLM instructions.
        Ensures agents operate under Sovereign Truth.
        """
        retrievals = self.retrieve(task, domain=domain)
        if not retrievals:
            return "No relevant sovereign knowledge found."

        context_parts = ["### RELEVANT SOVEREIGN KNOWLEDGE"]
        for r in retrievals:
            source = r["source"]
            content = r["content"]
            score = r.get("score", 0.0)
            context_parts.append(f"[{source.upper()} | relevance: {score:.2f}]\n{content}\n")

        return "\n".join(context_parts)

def get_rag_manager(project_root: Path) -> SovereignRAGManager:
    return SovereignRAGManager(project_root)
