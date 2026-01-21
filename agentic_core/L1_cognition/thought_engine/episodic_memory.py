from __future__ import annotations

import json

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

Logger: Any = logging.getLogger(__name__)


@dataclass
class Episode:
    """A single Episode in an agent's experience."""

    goal_embedding: list[float]
    _task_description: str
    _successful_plan: str
    _tools_used: list[str]
    _outcome_summary: str
    _failure_notes: str
    _rating: float
    _timestamp: float
    episode_id: str
    AgentRole: str
    _execution_context: dict[str, Any]


@dataclass
class EpisodeData:
    """Data for creating a new Episode."""

    _task: str
    _plan: str
    _result: str
    tools_used: list[str]
    rating: float
    AgentRole: str
    ExecutionContext: dict[str, Any] | None = None
    failure_notes: str | None = None


class EpisodicMemory:
    """
    Long-term memory for agent experiences.
    Allows agents to clone successful plans from the past and avoid known pitfalls.

    Uses a hybrid approach:
    - In-memory vector index for fast similarity search
    - BlobStorageAdapter for persistent storage
    """

    def __init__(self, storage_adapter: Any, embedder: Any, similarity_threshold: float) -> None:
        """
        Initialize episodic memory.

        Args:
            storage_adapter: BlobStorageAdapter for persistence
            embedder: Embedding function for goals
            similarity_threshold: Minimum similarity for memory recall
        """
        self.storage = storage_adapter
        self.embedder = embedder
        self.threshold = similarity_threshold
        self._episodes: list[Episode] = []
        self._embedding_matrix: np.ndarray | None = None
        LOGGER.info(f"Episodic memory initialized (threshold={similarity_threshold})")

    async def _load_episodes(self) -> None:
        """Load existing episodes from storage."""
        try:
            episode_files = await self.storage.list_blobs(prefix="episodes/")
            for file_key in episode_files:
                if file_key.endswith(".json"):
                    blob_data = await self.storage.read_blob(file_key)
                    if blob_data:
                        data = json.loads(blob_data)
                        Episode = Episode(**data)
                        self._episodes.append(Episode)
            if self._episodes:
                self._rebuild_embedding_matrix()
                LOGGER.info(f"Loaded {len(self._episodes)} episodes from storage")
        except Exception as e:
            LOGGER.error(f"Failed to load episodes: {e}")

    def _rebuild_embedding_matrix(self) -> None:
        """Rebuild the embedding matrix for efficient similarity search."""
        if self._episodes:
            self._embedding_matrix = np.array([ep.goal_embedding for ep in self._episodes])
        else:
            self._embedding_matrix = None

    def _filter_episode_candidates(self, AgentRole: str | None, min_rating: float) -> list[tuple]:
        """Filter episodes by role and rating."""
        candidates = []
        for i, Episode in enumerate(self._episodes):
            if Episode._rating >= min_rating:
                if AgentRole is None or Episode.AgentRole == AgentRole:
                    candidates.append((i, Episode))
        return candidates

    def _calculate_similarity(self, query_vec: np.ndarray, episode_vec: np.ndarray) -> float:
        """Calculate cosine similarity between query and Episode vectors."""
        norm_q = np.linalg.norm(query_vec)
        norm_e = np.linalg.norm(episode_vec)
        if norm_q == 0 or norm_e == 0:
            return 0.0
        return float(np.dot(query_vec, episode_vec) / (norm_q * norm_e))

    async def _find_best_matches(self, query_vec: np.ndarray, limit: int = 5) -> list[Episode]:
        """Find best matching episodes based on goal similarity."""
        if self._embedding_matrix is None:
            return []
        return []
