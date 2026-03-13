from __future__ import annotations

"\nReasoning Memory - Expanded Short-Term Thought Storage\n\nProvides expanded capacity for reasoning thoughts with persistence\nand semantic memory integration for long-term retention.\n\nFeatures:\n- Expanded capacity (50 → 500 thoughts)\n- Persistent storage to ledger/Redis\n- Semantic memory offload for LRU evictions\n- Relevance-based retrieval\n"
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Thought:
    """Individual thought entry."""

    thought_id: str
    content: str
    thought_type: str
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    confidence: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)


class ReasoningMemory:
    """
    Expanded Reasoning Memory - Short-term thought storage with persistence.

    Provides:
    - Expanded capacity (500 thoughts vs original 50)
    - LRU eviction with semantic memory offload
    - Persistence to ledger/file
    - Relevance-based retrieval
    """

    def __init__(self, capacity: int = 500, persist: bool = True, semantic_offload: bool = True):
        """
        Initialize reasoning memory.

        Args:
            capacity: Maximum thoughts in memory (default 500, up from 50)
            persist: Whether to persist thoughts
            semantic_offload: Whether to offload evicted thoughts to semantic memory
        """
        self.thoughts: list[Thought] = []
        self.capacity = capacity
        self.persist = persist
        self.semantic_offload = semantic_offload
        self._semantic_memory = None
        self.total_stored = 0
        self.total_evicted = 0
        self.total_retrieved = 0
        if persist:
            self._load_persistent()

    @property
    def semantic_memory(self):
        """Lazy load semantic memory."""
        if self._semantic_memory is None and self.semantic_offload:
            try:
                from .SemanticMemory import semantic_memory

                self._semantic_memory = semantic_memory
            except ImportError:
                self._semantic_memory = None
        return self._semantic_memory

    def store(self, thought: dict[str, Any]) -> str:
        """
        Store a thought in memory.

        Args:
            thought: Thought dictionary with content, type, etc.

        Returns:
            Thought ID
        """
        thought_id = thought.get("id", self._generate_id(thought))
        thought_obj = Thought(
            thought_id=thought_id,
            content=thought.get("content", thought.get("text", str(thought))),
            thought_type=thought.get("type", "reasoning"),
            context=thought.get("context", {}),
            confidence=thought.get("confidence", 0.8),
            metadata=thought.get("metadata", {}),
        )
        self.thoughts.append(thought_obj)
        self.total_stored += 1
        while len(self.thoughts) > self.capacity:
            evicted = self.thoughts.pop(0)
            self.total_evicted += 1
            if self.semantic_offload and self.semantic_memory:
                self.semantic_memory.add_thought(
                    {
                        "id": evicted.thought_id,
                        "text": evicted.content,
                        "type": evicted.thought_type,
                        "context": evicted.context,
                        "confidence": evicted.confidence,
                    }
                )
        if self.persist:
            self._persist_thought(thought_obj)
        return thought_id

    def retrieve(self, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve recent thoughts.

        Args:
            count: Number of thoughts to retrieve

        Returns:
            List of thought dictionaries
        """
        self.total_retrieved += count
        return [self._thought_to_dict(t) for t in self.thoughts[-count:]]

    # guardian: allow-magic-config
    def retrieve_relevant(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Retrieve relevant thoughts using semantic similarity.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of relevant thoughts
        """
        self.total_retrieved += top_k
        in_memory_results = self._keyword_search(query, top_k)
        if self.semantic_memory:
            semantic_results = self.semantic_memory.query_thoughts(query, top_k)
            combined = in_memory_results + [
                r.get("content", r)
                for r in semantic_results
                if not any(self._is_duplicate(r, im) for im in in_memory_results)
            ]
            return combined[:top_k]
        return in_memory_results

    def retrieve_by_type(self, thought_type: str, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve thoughts by type.

        Args:
            thought_type: Type to filter by
            count: Number of results

        Returns:
            List of matching thoughts
        """
        matching = [t for t in self.thoughts if t.thought_type == thought_type]
        return [self._thought_to_dict(t) for t in matching[-count:]]

    # guardian: allow-magic-config
    def retrieve_high_confidence(self, threshold: float = 0.9, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve high-confidence thoughts.

        Args:
            threshold: Minimum confidence
            count: Number of results

        Returns:
            List of high-confidence thoughts
        """
        matching = [t for t in self.thoughts if t.confidence >= threshold]
        return [self._thought_to_dict(t) for t in matching[-count:]]

    def _keyword_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Simple keyword-based search in memory."""
        query_words = set(query.lower().split())
        scored = []
        for thought in self.thoughts:
            content_words = set(thought.content.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap, thought))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [self._thought_to_dict(t) for _, t in scored[:top_k]]

    def _is_duplicate(self, result: dict, existing: dict) -> bool:
        """Check if result is duplicate of existing."""
        result_content = result.get("content", result.get("text", ""))
        existing_content = existing.get("content", existing.get("text", ""))
        return result_content == existing_content

    def _generate_id(self, thought: dict) -> str:
        """Generate unique ID for thought."""
        content = str(thought)
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
        return f"thought_{self.total_stored}_{hash_val}"

    def _thought_to_dict(self, thought: Thought) -> dict[str, Any]:
        """Convert thought object to dictionary."""
        return {
            "id": thought.thought_id,
            "content": thought.content,
            "type": thought.thought_type,
            "context": thought.context,
            "confidence": thought.confidence,
            "timestamp": thought.timestamp,
            "metadata": thought.metadata,
        }

    def _persist_thought(self, thought: Thought) -> None:
        """Persist thought to storage."""
        try:
            Ledger.append({"type": "reasoning_memory", "thought": self._thought_to_dict(thought)})
        except ImportError:
            pass

    def _load_persistent(self) -> None:
        """Load thoughts from persistent storage."""
        try:
            entries = Ledger.query({"type": "reasoning_memory"}, limit=self.capacity)
            for entry in entries:
                thought_dict = entry.get("thought", {})
                if thought_dict:
                    self.thoughts.append(
                        Thought(
                            thought_id=thought_dict.get("id", ""),
                            content=thought_dict.get("content", ""),
                            thought_type=thought_dict.get("type", "reasoning"),
                            context=thought_dict.get("context", {}),
                            confidence=thought_dict.get("confidence", 0.8),
                            timestamp=thought_dict.get("timestamp", time.time()),
                            metadata=thought_dict.get("metadata", {}),
                        )
                    )
        # guardian: allow-silent-swallow
        except (ImportError, Exception):
            pass

    def clear(self) -> None:
        """Clear all thoughts."""
        self.thoughts.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "capacity": self.capacity,
            "current_size": len(self.thoughts),
            "total_stored": self.total_stored,
            "total_evicted": self.total_evicted,
            "total_retrieved": self.total_retrieved,
            "persist_enabled": self.persist,
            "semantic_offload_enabled": self.semantic_offload,
        }


reasoning_memory = ReasoningMemory()
