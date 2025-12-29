# Sovereign RAG Manager
# Territory: agentic_core/knowledge (cross-subfolder orchestrator)
# Canon Key 9 - Retrieval-Augmented Generation integration

import json
from pathlib import Path
from typing import List, Dict, Optional

# Internal imports referencing the mandated structure
try:
    from agentic_core.knowledge.document_loaders.text_loader import TextDocumentLoader
    from agentic_core.knowledge.static_index.action_verbs import ACTION_VERBS, STRONG_VERBS
    from agentic_core.knowledge.research_cache.cache_store import ResearchCache
except ImportError:
    # Fallback to avoid mission failure if sub-modules are mid-relocation
    ACTION_VERBS, STRONG_VERBS = {}, []

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

    def _load_static_index(self) -> Dict:
        """Load all hard-coded knowledge bases for immediate retrieval."""
        return {
            "action_verbs": {
                "categories": ACTION_VERBS,
                "strong_verbs": STRONG_VERBS,
            },
        }

    def retrieve(
        self,
        query: str,
        domain: str = "general",
        top_k: int = 5,
        use_cache: bool = True,
    ) -> List[Dict]:
        """
        Sovereign retrieval — combines cache and static facts.
        """
        results: List[Dict] = []

        # 1. Check Research Cache (persisted external knowledge)
        if use_cache:
            cached = self.cache.query(query, top_k=top_k)
            if cached:
                results.extend([{"source": "research_cache", "content": c} for c in cached])

        # 2. Add Static Knowledge (Canonically defined facts)
        if any(kw in query.lower() for kw in ["verb", "action", "resume", "writing"]):
            results.append({
                "source": "static_index.action_verbs",
                "content": json.dumps(self.static_knowledge["action_verbs"], indent=2)
            })

        return results[:top_k]

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
            context_parts.append(f"Source: {source.upper()}\nContent:\n{content}\n")

        return "\n".join(context_parts)

def get_rag_manager(project_root: Path) -> SovereignRAGManager:
    return SovereignRAGManager(project_root)
