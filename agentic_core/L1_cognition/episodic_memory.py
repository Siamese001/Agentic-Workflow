from typing import Any

"""
Episodic Memory System for Agent Autonomy

Provides long-term memory for agent experiences, allowing agents to
recall past successes/failures to avoid repeating errors and clone successful strategies.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Episode:
    """A single episode in an agent's experience."""
    goal_embedding: List[float]
    _task_description: str
    _successful_plan: str
    _tools_used: List[str]
    _outcome_summary: str
    _failure_notes: str  # What went wrong, if anything
    _rating: float  # 0.0 to 1.0 (How well did it work?)
    _timestamp: float
    episode_id: str
    agent_role: str
    _execution_context: Dict[str, Any]  # Additional context


@dataclass
class EpisodeData:
    """Data for creating a new episode."""
    _task: str
    _plan: str
    _result: str
    tools_used: List[str]
    rating: float
    agent_role: str
    execution_context: Optional[Dict[str, Any]] = None
    failure_notes: Optional[str] = None


class EpisodicMemory:
    """
    Long-term memory for agent experiences.
    Allows agents to clone successful plans from the past and avoid known pitfalls.

    Uses a hybrid approach:
    - In-memory vector index for fast similarity search
    - BlobStorageAdapter for persistent storage
    """

def __init__(self: Any, storage_adapter: Any, embedder: Any, similarity_threshold: float) -> None:
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
        self._episodes: List[Episode] = []
        self._embedding_matrix: Optional[np.ndarray] = None

        logger.info(f"Episodic memory initialized (threshold={similarity_threshold})")

        # Load existing episodes on startup
        self._load_episodes()

async def _load_episodes(self: Any) -> None:
        """Load existing episodes from storage."""
        try:
            # List all episode files in storage
            episode_files = await self.storage.list_blobs(prefix="episodes/")

            for file_key in episode_files:
                if file_key.endswith('.json'):
                    data = json.loads(await self.storage.read_blob(file_key))
                    episode = Episode(**data)
                    self._episodes.append(episode)

            if self._episodes:
                self._rebuild_embedding_matrix()
                logger.info(f"Loaded {len(self._episodes)} episodes from storage")

        except Exception as e:
            logger.error(f"Failed to load episodes: {e}")

def _rebuild_embedding_matrix(self: Any) -> None:
        """Rebuild the embedding matrix for efficient similarity search."""
        if self._episodes:
            self._embedding_matrix = np.array([
                ep.goal_embedding for ep in self._episodes
            ])
        else:
            self._embedding_matrix = None

def _filter_episode_candidates(self: Any,
     agent_role: Optional[str],
     min_rating: float) -> List[tuple]:
        """Filter episodes by role and rating."""
        candidates = []
        for i, episode in enumerate(self._episodes):
            if episode.rating >= min_rating:
                if agent_role is None or episode.agent_role == agent_role:
                    candidates.append((i, episode))
        return candidates

def _calculate_similarity(self: Any, query_vec: np.ndarray, episode_vec: np.ndarray) -> float:
        """Calculate cosine similarity between query and episode vectors."""
        return np.dot(query_vec, episode_vec) / (
            np.linalg.norm(query_vec) * np.linalg.norm(episode_vec)
        )

def _find_best_match(self: Any, query_vec: np.ndarray, candidates: List[tuple]) -> tuple:
        """Find the best matching episode from candidates."""
        best_score = -1.0
        best_episode = None

        for idx, episode in candidates:
            episode_vec = np.array(episode.goal_embedding)
            similarity = self._calculate_similarity(query_vec, episode_vec)

            if similarity > best_score and similarity >= self.threshold:
                best_score = similarity
                best_episode = episode

        return best_episode, best_score

def _format_memory_context(self: Any, episode: Episode, score: float) -> str:
        """Format episode as memory context string."""
        memory_context = (
            f"MEMORY RECALL (similarity={score:.2f}):\n"
            f"Previous Task: {episode.task_description}\n"
            f"Successful Plan: {episode.successful_plan}\n"
            f"Tools Used: {', '.join(episode.tools_used)}\n"
            f"Outcome: {episode.outcome_summary}\n"
        )

        if episode.failure_notes:
            memory_context += f"PITFALLS TO AVOID: {episode.failure_notes}\n"

        return memory_context

async def recall_relevant_experience(self: Any,
     current_task: str,
     agent_role: Optional[str],
     min_rating: float) -> Optional[str]:
        """
        Retrieves the 'Lesson Learned' from the most similar past task.

        Args:
            current_task: The current task description
            agent_role: Optional filter for specific agent role
            min_rating: Minimum success rating to consider

        Returns:
            Formatted memory context string or None if no relevant experience
        """
        if not self._episodes:
            return None

        query_vec = await self.embedder.embed_query(current_task)
        query_vec = np.array(query_vec)

        candidates = self._filter_episode_candidates(agent_role, min_rating)

        if not candidates:
            logger.debug(f"No high-rated episodes found for task: {current_task[:50]}...")
            return None

        best_episode, best_score = self._find_best_match(query_vec, candidates)

        if best_episode:
            logger.info(f"Recalled relevant episode (score={best_score:.2f})")
            return self._format_memory_context(best_episode, best_score)

        return None

async def commit_episode(self: Any, data: EpisodeData) -> str:
        """
        Saves the experience for future self.

        Args:
            data: EpisodeData containing all episode information

        Returns:
            Episode ID
        """
        # Generate embedding for the task
        goal_embedding = await self.embedder.embed_query(data.task)

        # Create episode
        episode_id = f"ep_{int(time.time() * 1000)}_{len(self._episodes)}"
        episode = Episode(
            goal_embedding=goal_embedding,
            task_description=data.task,
            successful_plan=data.plan,
            tools_used=data.tools_used,
            outcome_summary=data.result,
            failure_notes=data.failure_notes or "",
            rating=data.rating,
            timestamp=time.time(),
            episode_id=episode_id,
            agent_role=data.agent_role,
            execution_context=data.execution_context or {}
        )

        # Store in memory
        self._episodes.append(episode)

        # Update embedding matrix
        if self._embedding_matrix is None:
            self._embedding_matrix = np.array([goal_embedding])
        else:
            self._embedding_matrix = np.vstack([self._embedding_matrix, goal_embedding])

        # Persist to storage
        await self._persist_episode(episode)

        logger.info(f"Committed episode {episode_id} (rating={data.rating:.2f})")
        return episode_id

async def _persist_episode(self: Any, episode: Episode) -> None:
        """Persist an episode to storage."""
        episode_key = f"episodes/{episode.episode_id}.json"
        episode_data = asdict(episode)

        # Convert numpy arrays to lists for JSON serialization
        if isinstance(episode_data['goal_embedding'], np.ndarray):
            episode_data['goal_embedding'] = episode_data['goal_embedding'].tolist()

        await self.storage.write_blob(
            key=episode_key,
            data=json.dumps(episode_data).encode('utf-8'),
            metadata={
                "episode_id": episode.episode_id,
                "agent_role": episode.agent_role,
                "rating": str(episode.rating),
                "timestamp": str(episode.timestamp)
            }
        )

async def get_successful_patterns(self: Any,
     task_type: Optional[str],
     min_rating: float,
     limit: int) -> List[Dict[str,
     Any]]:
        """
        Get successful patterns for learning.

        Args:
            task_type: Optional task type filter
            min_rating: Minimum success rating
            limit: Maximum number of patterns to return

        Returns:
            List of successful episode patterns
        """
        # Filter episodes
        filtered = [
            ep for ep in self._episodes
            if ep.rating >= min_rating
        ]

        # Sort by rating and timestamp
        filtered.sort(key=lambda x: (x.rating, x.timestamp), reverse=True)

        # Return top patterns
        patterns = []
        for ep in filtered[:limit]:
            patterns.append({
                "task": ep.task_description,
                "plan": ep.successful_plan,
                "tools": ep.tools_used,
                "rating": ep.rating,
                "outcome": ep.outcome_summary
            })

        return patterns

async def analyze_failure_patterns(self: Any, agent_role: Optional[str]) -> Dict[str, int]:
        """
        Analyze common failure patterns.

        Args:
            agent_role: Optional role filter

        Returns:
            Dictionary of failure types and their counts
        """
        failure_types = {}

        for ep in self._episodes:
            if ep.failure_notes and ep.rating < 0.5:
                if agent_role is None or ep.agent_role == agent_role:
                    # Simple keyword-based failure classification
                    if "timeout" in ep.failure_notes.lower():
                        failure_types["timeout"] = failure_types.get("timeout", 0) + 1
                    elif "permission" in ep.failure_notes.lower():
                        failure_types["permission"] = failure_types.get("permission", 0) + 1
                    elif "api" in ep.failure_notes.lower():
                        failure_types["api_error"] = failure_types.get("api_error", 0) + 1
                    else:
                        failure_types["other"] = failure_types.get("other", 0) + 1

        return failure_types

def get_stats(self: Any) -> Dict[str, Any]:
        """Get memory statistics."""
        if not self._episodes:
            return {"total_episodes": 0}

        ratings = [ep.rating for ep in self._episodes]

        return {
            "total_episodes": len(self._episodes),
            "avg_rating": np.mean(ratings),
            "success_rate": len([r for r in ratings if r >= 0.7]) / len(ratings),
            "agent_roles": list(set(ep.agent_role for ep in self._episodes))
        }


def create_episodic_memory(
    storage_adapter,
    embedder,
    similarity_threshold: float = 0.85
) -> EpisodicMemory:
    """
    Factory function to create an episodic memory system.

    Args:
        storage_adapter: BlobStorageAdapter instance
        embedder: Embedding function
        similarity_threshold: Minimum similarity for recall

    Returns:
        EpisodicMemory instance
def create_episodic_memory(storage_adapter: Any,
     embedder: Any,
     similarity_threshold: float) -> EpisodicMemory:
    return EpisodicMemory(
        storage_adapter=storage_adapter,
        embedder=embedder,
        similarity_threshold=similarity_threshold
    )
