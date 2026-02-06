from __future__ import annotations

"""
Episodic Memory - Expanded Mission/Episode Storage

Provides expanded capacity for mission episodes with semantic index
integration for long-term pattern access.

Features:
- Expanded capacity (20 → 200 episodes)
- Semantic index integration for similarity retrieval
- Automatic offload of old episodes to semantic memory
- Mission history retention across sessions
"""


import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Episode:
    """Individual episode entry."""

    episode_id: str
    summary: str
    mission_type: str  # "task", "healing", "reasoning", "execution"
    outcome: str  # "success", "failure", "partial"
    steps: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    reward: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class EpisodicMemory:
    """
    Expanded Episodic Memory - Mission history storage with semantic indexing.

    Provides:
    - Expanded capacity (200 episodes vs original 20)
    - Semantic index integration for similarity search
    - Automatic offload of evicted episodes
    - Mission pattern extraction
    """

    def __init__(self, capacity: int = 200, embed_index: bool = True):
        """
        Initialize episodic memory.

        Args:
            capacity: Maximum episodes in memory (default 200, up from 20)
            embed_index: Whether to use semantic indexing
        """
        self.episodes: list[Episode] = []
        self.capacity = capacity
        self.embed_index = embed_index
        self._semantic_memory = None

        # Statistics
        self.total_stored = 0
        self.total_evicted = 0
        self.success_count = 0
        self.failure_count = 0

    @property
    def semantic_index(self):
        """Lazy load semantic memory."""
        if self._semantic_memory is None and self.embed_index:
            try:
                from .SemanticMemory import semantic_memory

                self._semantic_memory = semantic_memory
            except ImportError:
                self._semantic_memory = None
        return self._semantic_memory

    def store_episode(self, episode: dict[str, Any]) -> str:
        """
        Store an episode in memory.

        Args:
            episode: Episode dictionary with summary, outcome, etc.

        Returns:
            Episode ID
        """
        # Create episode object
        episode_id = episode.get("id", self._generate_id(episode))

        episode_obj = Episode(
            episode_id=episode_id,
            summary=episode.get("summary", episode.get("description", str(episode))),
            mission_type=episode.get("type", episode.get("mission_type", "task")),
            outcome=episode.get("outcome", "unknown"),
            steps=episode.get("steps", []),
            context=episode.get("context", {}),
            duration_ms=episode.get("duration_ms", 0.0),
            reward=episode.get("reward", 0.0),
            metadata=episode.get("metadata", {}),
        )

        # Track outcomes
        if episode_obj.outcome == "success":
            self.success_count += 1
        elif episode_obj.outcome == "failure":
            self.failure_count += 1

        # Add to memory
        self.episodes.append(episode_obj)
        self.total_stored += 1

        # Add to semantic index immediately for searchability
        if self.semantic_index:
            self.semantic_index.add_episode(
                {
                    "id": episode_id,
                    "summary": episode_obj.summary,
                    "type": episode_obj.mission_type,
                    "outcome": episode_obj.outcome,
                },
            )

        # Check capacity and evict if needed
        while len(self.episodes) > self.capacity:
            self.episodes.pop(0)  # LRU - remove oldest
            self.total_evicted += 1

            # Already in semantic index, so no additional action needed

        return episode_id

    def retrieve(self, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve recent episodes.

        Args:
            count: Number of episodes to retrieve

        Returns:
            List of episode dictionaries
        """
        return [self._episode_to_dict(e) for e in self.episodes[-count:]]

    def retrieve_relevant(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Retrieve relevant episodes using semantic similarity.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of relevant episodes
        """
        # First check in-memory episodes with keyword matching
        in_memory_results = self._keyword_search(query, top_k)

        # If semantic index available, also search there
        if self.semantic_index:
            semantic_results = self.semantic_index.query_episodes(query, top_k)

            # Combine results
            seen_ids = {r.get("id") for r in in_memory_results}
            for result in semantic_results:
                if result.get("id") not in seen_ids:
                    in_memory_results.append(result.get("content", result))

        return in_memory_results[:top_k]

    def retrieve_by_outcome(self, outcome: str, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve episodes by outcome.

        Args:
            outcome: Outcome to filter by ("success", "failure", "partial")
            count: Number of results

        Returns:
            List of matching episodes
        """
        matching = [e for e in self.episodes if e.outcome == outcome]
        return [self._episode_to_dict(e) for e in matching[-count:]]

    def retrieve_successes(self, count: int = 10) -> list[dict[str, Any]]:
        """Retrieve successful episodes."""
        return self.retrieve_by_outcome("success", count)

    def retrieve_failures(self, count: int = 10) -> list[dict[str, Any]]:
        """Retrieve failed episodes."""
        return self.retrieve_by_outcome("failure", count)

    def retrieve_by_type(self, mission_type: str, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve episodes by mission type.

        Args:
            mission_type: Type to filter by
            count: Number of results

        Returns:
            List of matching episodes
        """
        matching = [e for e in self.episodes if e.mission_type == mission_type]
        return [self._episode_to_dict(e) for e in matching[-count:]]

    def retrieve_high_reward(self, threshold: float = 0.5, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve high-reward episodes.

        Args:
            threshold: Minimum reward
            count: Number of results

        Returns:
            List of high-reward episodes
        """
        matching = [e for e in self.episodes if e.reward >= threshold]
        matching.sort(key=lambda x: x.reward, reverse=True)
        return [self._episode_to_dict(e) for e in matching[:count]]

    def get_success_rate(self) -> float:
        """Get overall success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def _keyword_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Simple keyword-based search in memory."""
        query_words = set(query.lower().split())

        scored = []
        for episode in self.episodes:
            content_words = set(episode.summary.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap, episode))

        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)

        return [self._episode_to_dict(e) for _, e in scored[:top_k]]

    def _generate_id(self, episode: dict) -> str:
        """Generate unique ID for episode."""
        content = str(episode)
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
        return f"episode_{self.total_stored}_{hash_val}"

    def _episode_to_dict(self, episode: Episode) -> dict[str, Any]:
        """Convert episode object to dictionary."""
        return {
            "id": episode.episode_id,
            "summary": episode.summary,
            "type": episode.mission_type,
            "outcome": episode.outcome,
            "steps": episode.steps,
            "context": episode.context,
            "timestamp": episode.timestamp,
            "duration_ms": episode.duration_ms,
            "reward": episode.reward,
            "metadata": episode.metadata,
        }

    def clear(self) -> None:
        """Clear all episodes."""
        self.episodes.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "capacity": self.capacity,
            "current_size": len(self.episodes),
            "total_stored": self.total_stored,
            "total_evicted": self.total_evicted,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.get_success_rate(),
            "embed_index_enabled": self.embed_index,
        }


# Global instance
episodic_memory = EpisodicMemory()
