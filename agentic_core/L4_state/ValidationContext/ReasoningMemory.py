"""
Reasoning Memory - Expanded Short-Term Thought Storage

Provides expanded capacity for reasoning thoughts with persistence
and semantic memory integration for long-term retention.

Features:
- Expanded capacity (50 → 500 thoughts)
- Persistent storage to ledger/Redis
- Semantic memory offload for LRU evictions
- Relevance-based retrieval
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time
import hashlib
import json


@dataclass
class Thought:
    """Individual thought entry."""
    thought_id: str
    content: str
    thought_type: str  # "reasoning", "observation", "conclusion", "hypothesis"
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReasoningMemory:
    """
    Expanded Reasoning Memory - Short-term thought storage with persistence.

    Provides:
    - Expanded capacity (500 thoughts vs original 50)
    - LRU eviction with semantic memory offload
    - Persistence to ledger/file
    - Relevance-based retrieval
    """

    def __init__(
        self,
        capacity: int = 500,
        persist: bool = True,
        semantic_offload: bool = True
    ):
        """
        Initialize reasoning memory.

        Args:
            capacity: Maximum thoughts in memory (default 500, up from 50)
            persist: Whether to persist thoughts
            semantic_offload: Whether to offload evicted thoughts to semantic memory
        """
        self.thoughts: List[Thought] = []
        self.capacity = capacity
        self.persist = persist
        self.semantic_offload = semantic_offload
        self._semantic_memory = None

        # Statistics
        self.total_stored = 0
        self.total_evicted = 0
        self.total_retrieved = 0

        # Load persistent state
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

    def store(self, thought: Dict[str, Any]) -> str:
        """
        Store a thought in memory.

        Args:
            thought: Thought dictionary with content, type, etc.

        Returns:
            Thought ID
        """
        # Create thought object
        thought_id = thought.get("id", self._generate_id(thought))

        thought_obj = Thought(
            thought_id=thought_id,
            content=thought.get("content", thought.get("text", str(thought))),
            thought_type=thought.get("type", "reasoning"),
            context=thought.get("context", {}),
            confidence=thought.get("confidence", 0.8),
            metadata=thought.get("metadata", {})
        )

        # Add to memory
        self.thoughts.append(thought_obj)
        self.total_stored += 1

        # Check capacity and evict if needed
        while len(self.thoughts) > self.capacity:
            evicted = self.thoughts.pop(0)  # LRU - remove oldest
            self.total_evicted += 1

            # Offload to semantic memory
            if self.semantic_offload and self.semantic_memory:
                self.semantic_memory.add_thought({
                    "id": evicted.thought_id,
                    "text": evicted.content,
                    "type": evicted.thought_type,
                    "context": evicted.context,
                    "confidence": evicted.confidence
                })

        # Persist if enabled
        if self.persist:
            self._persist_thought(thought_obj)

        return thought_id

    def retrieve(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent thoughts.

        Args:
            count: Number of thoughts to retrieve

        Returns:
            List of thought dictionaries
        """
        self.total_retrieved += count
        return [self._thought_to_dict(t) for t in self.thoughts[-count:]]

    def retrieve_relevant(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant thoughts using semantic similarity.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of relevant thoughts
        """
        self.total_retrieved += top_k

        # First check in-memory thoughts with simple keyword matching
        in_memory_results = self._keyword_search(query, top_k)

        # If semantic memory available, also search there
        if self.semantic_memory:
            semantic_results = self.semantic_memory.query_thoughts(query, top_k)

            # Combine results, preferring in-memory (more recent)
            combined = in_memory_results + [
                r.get("content", r) for r in semantic_results
                if not any(self._is_duplicate(r, im) for im in in_memory_results)
            ]
            return combined[:top_k]

        return in_memory_results

    def retrieve_by_type(self, thought_type: str, count: int = 10) -> List[Dict[str, Any]]:
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

    def retrieve_high_confidence(self, threshold: float = 0.9, count: int = 10) -> List[Dict[str, Any]]:
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

    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simple keyword-based search in memory."""
        query_words = set(query.lower().split())

        scored = []
        for thought in self.thoughts:
            content_words = set(thought.content.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap, thought))

        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)

        return [self._thought_to_dict(t) for _, t in scored[:top_k]]

    def _is_duplicate(self, result: Dict, existing: Dict) -> bool:
        """Check if result is duplicate of existing."""
        result_content = result.get("content", result.get("text", ""))
        existing_content = existing.get("content", existing.get("text", ""))
        return result_content == existing_content

    def _generate_id(self, thought: Dict) -> str:
        """Generate unique ID for thought."""
        content = str(thought)
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
        return f"thought_{self.total_stored}_{hash_val}"

    def _thought_to_dict(self, thought: Thought) -> Dict[str, Any]:
        """Convert thought object to dictionary."""
        return {
            "id": thought.thought_id,
            "content": thought.content,
            "type": thought.thought_type,
            "context": thought.context,
            "confidence": thought.confidence,
            "timestamp": thought.timestamp,
            "metadata": thought.metadata
        }

    def _persist_thought(self, thought: Thought) -> None:
        """Persist thought to storage."""
        try:
            # Try to append to ledger
            Ledger.append({
                "type": "reasoning_memory",
                "thought": self._thought_to_dict(thought)
            })
        except ImportError:
            # Fallback: no-op for now
            pass

    def _load_persistent(self) -> None:
        """Load thoughts from persistent storage."""
        try:
            entries = Ledger.query({"type": "reasoning_memory"}, limit=self.capacity)
            for entry in entries:
                thought_dict = entry.get("thought", {})
                if thought_dict:
                    self.thoughts.append(Thought(
                        thought_id=thought_dict.get("id", ""),
                        content=thought_dict.get("content", ""),
                        thought_type=thought_dict.get("type", "reasoning"),
                        context=thought_dict.get("context", {}),
                        confidence=thought_dict.get("confidence", 0.8),
                        timestamp=thought_dict.get("timestamp", time.time()),
                        metadata=thought_dict.get("metadata", {})
                    ))
        except (ImportError, Exception):
            # No persistent storage available
            pass

    def clear(self) -> None:
        """Clear all thoughts."""
        self.thoughts.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "capacity": self.capacity,
            "current_size": len(self.thoughts),
            "total_stored": self.total_stored,
            "total_evicted": self.total_evicted,
            "total_retrieved": self.total_retrieved,
            "persist_enabled": self.persist,
            "semantic_offload_enabled": self.semantic_offload
        }


# Global instance
reasoning_memory = ReasoningMemory()
