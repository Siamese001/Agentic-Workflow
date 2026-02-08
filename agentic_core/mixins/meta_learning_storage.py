"""
meta_learning_storage.py - Pinecone/Vector DB Interaction Layer

[MIXIN REFACTOR] Extracted from meta_learning_mixin.py (643 lines).
Manages all connections to storage backends:
  - SemanticCacheManager (Pinecone) for experience recall/learn
  - GraphMemoryBridge for entity registration and MASTERED_TASK relations

Thread-safe singleton initialization with circuit breaker.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import threading
from typing import Any

Logger = logging.getLogger(__name__)


class MetaLearningStorage:
    """Thread-safe storage layer for meta-learning backends.

    Class-level singletons with circuit breaker for graceful degradation.
    """

    _memory = None
    _memory_lock = threading.RLock()
    _lobotomized = False

    _graph_bridge = None
    _graph_lock = threading.RLock()

    # ── SemanticCacheManager (Pinecone) ──────────────────────────────

    @classmethod
    def ensure_memory_connection(cls, agent_name: str) -> None:
        """Connect to SemanticCacheManager singleton (thread-safe, circuit-breaker)."""
        if cls._lobotomized:
            return

        if cls._memory is None:
            with cls._memory_lock:
                if cls._memory is None:
                    try:
                        from agentic_core.L4_state.memory.semantic_cache_manager_config import (
                            SemanticCacheManager,
                        )

                        cls._memory = SemanticCacheManager.get_instance()
                        Logger.debug(f"[{agent_name}] Connected to Hive Mind")
                    except Exception as e:
                        cls._lobotomized = True
                        Logger.critical(
                            f"[{agent_name}] LOBOTOMY PROTOCOL ACTIVE: "
                            f"Hive Mind unavailable ({e})",
                        )

    @classmethod
    def recall(cls, context: str, namespace: str) -> dict[str, Any] | None:
        """Query Pinecone for a cached experience."""
        if cls._lobotomized or cls._memory is None:
            return None

        try:
            result = cls._memory.recall(context, namespace)
            if result:
                Logger.info(f"[{namespace}] INSTINCT TRIGGERED: Recalled previous experience.")
            return result
        except Exception as e:
            Logger.warning(f"[{namespace}] Recall error: {e}")
            return None

    @classmethod
    async def learn_async(cls, context: str, namespace: str, result: dict[str, Any]) -> None:
        """Async write to Pinecone (fire-and-forget safe)."""
        if cls._lobotomized or cls._memory is None:
            return

        try:
            _ = json.dumps(result)  # serialization guard
            await cls._memory.learn_async(context, namespace, result)
        except Exception as e:
            Logger.warning(f"[{namespace}] Async learn failed: {e}")

    @classmethod
    def learn_with_feedback(
        cls,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float,
    ) -> bool:
        """Learn with feedback score, promoting to long-term DNA if threshold met."""
        if cls._lobotomized or cls._memory is None:
            return False

        try:
            cls._memory.learn(context, namespace, result, feedback_score)

            promotion_threshold = getattr(cls._memory, "promotion_threshold", 0.8)
            if feedback_score >= promotion_threshold:
                promoted = cls._memory.promote_to_long_term(
                    context, namespace, result, feedback_score,
                )
                if promoted:
                    sanitized_context = context
                    if hasattr(cls._memory, "sanitizer"):
                        sanitized_context = cls._memory.sanitizer.sanitize(context)
                    cls._create_mastered_task_relation(namespace, sanitized_context, feedback_score)
                    Logger.info(
                        f"[{namespace}] DNA PROMOTION: Memory promoted with "
                        f"feedback_score={feedback_score:.2f}",
                    )
                    return True

            return False
        except Exception as e:
            Logger.warning(f"[{namespace}] Learn with feedback failed: {e}")
            return False

    @classmethod
    def get_memory_stats(cls) -> dict[str, Any] | None:
        """Get statistics from the Hive Mind."""
        if cls._lobotomized or cls._memory is None:
            return None
        try:
            return cls._memory.get_statistics()
        except Exception:
            return None

    # ── GraphMemoryBridge ────────────────────────────────────────────

    @classmethod
    def ensure_graph_bridge_connection(cls, agent_name: str) -> None:
        """Connect to GraphMemoryBridge singleton (thread-safe)."""
        if cls._graph_bridge is None:
            with cls._graph_lock:
                if cls._graph_bridge is None:
                    try:
                        from agentic_core.L4_state.memory.graph_memory_bridge_types import (
                            GraphMemoryBridge,
                        )

                        cls._graph_bridge = GraphMemoryBridge.get_instance()
                        Logger.debug(f"[{agent_name}] Connected to Graph Memory Bridge")
                    except Exception as e:
                        Logger.warning(f"[{agent_name}] Graph Memory Bridge unavailable: {e}")

    @classmethod
    def register_agent_entity(cls, agent_name: str) -> None:
        """Register agent as entity in graph bridge (idempotent)."""
        if cls._graph_bridge is None:
            return
        try:
            cls._graph_bridge.create_agent_entity(
                agent_name=agent_name,
                agent_type="Agent",
                observations=[f"Agent {agent_name} initialized"],
            )
        except Exception as e:
            Logger.warning(f"[{agent_name}] Agent entity registration failed: {e}")

    @classmethod
    def _create_mastered_task_relation(
        cls,
        agent_name: str,
        context: str,
        feedback_score: float,
    ) -> None:
        """Create MASTERED_TASK relation when memory is promoted."""
        if cls._graph_bridge is None:
            return
        try:
            cls._graph_bridge.create_mastered_task_relation(
                agent_name=agent_name,
                task_description=context,
                feedback_score=feedback_score,
            )
        except Exception as e:
            Logger.warning(f"[{agent_name}] MASTERED_TASK relation creation failed: {e}")

    @classmethod
    def get_graph_stats(cls) -> dict[str, Any] | None:
        """Get statistics from the Graph Memory Bridge."""
        if cls._graph_bridge is None:
            return None
        try:
            return cls._graph_bridge.get_statistics()
        except Exception:
            return None

    # ── Resets (testing) ─────────────────────────────────────────────

    @classmethod
    def reset_lobotomy(cls) -> None:
        """Reset the circuit breaker state."""
        cls._lobotomized = False
        cls._memory = None
        Logger.info("[MetaLearningStorage] Lobotomy state reset")

    @classmethod
    def reset_graph_bridge(cls) -> None:
        """Reset the Graph Memory Bridge."""
        cls._graph_bridge = None
        Logger.info("[MetaLearningStorage] Graph Memory Bridge reset")

    # ── Utility ──────────────────────────────────────────────────────

    @staticmethod
    def generate_context_hash(namespace: str, context: str) -> str:
        """Deterministic context hash for DNA segregation."""
        key = f"{namespace}:{context}"
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    @property
    def is_lobotomized(cls) -> bool:
        """Check circuit breaker state."""
        return cls._lobotomized
