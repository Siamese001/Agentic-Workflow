"""
meta_learning_engine.py - Core Logic for Recall/Execute and Knowledge Graph Bridging

[MIXIN REFACTOR] Extracted from meta_learning_mixin.py (643 lines).
Contains the core algorithms and KG interaction logic:
  - KnowledgeGraphBridge connection and context discovery
  - recall_or_execute (the Golden Path)
  - Execution reflection and agent interaction recording
  - Architectural observation and inheritance management

Naming convention: *_engine.py = core logic (may use class state for KG bridge,
but does NOT depend on Agent self / SovereignBaseAgent).
"""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any

from agentic_core.utils.meta_learning_storage_util import MetaLearningStorage

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)


class MetaLearningEngine:
    """Core meta-learning logic: KG bridging, recall/execute, reflection.

    Operates on agent_name (str) rather than requiring Agent self.
    Uses MetaLearningStorage for Pinecone/Graph access.
    """

    _kg_bridge = None
    _kg_lock = threading.RLock()

    # ── KnowledgeGraphBridge ─────────────────────────────────────────

    @classmethod
    def ensure_kg_connection(cls, agent_name: str) -> None:
        """Connect to KnowledgeGraphBridge singleton (thread-safe)."""
        if cls._kg_bridge is None:
            with cls._kg_lock:
                if cls._kg_bridge is None:
                    try:
                        from agentic_core.base_agents.knowledge_graph_bridge import (
                            KnowledgeGraphBridge,
                        )

                        cls._kg_bridge = KnowledgeGraphBridge.get_instance()
                        cls._kg_bridge.register_agent(agent_name, agent_type="Agent")
                        Logger.debug(f"[{agent_name}] Connected to Knowledge Graph")
                    except Exception as e:
                        # TODO: Handle specific exception properly
                        raise  # Re-raise after logging/handling
                        Logger.warning(f"[{agent_name}] Knowledge Graph unavailable: {e}")

    @classmethod
    def discover_agent_context(cls, agent_name: str) -> dict[str, Any]:
        """Auto-discover context for an agent from the Knowledge Graph."""
        if cls._kg_bridge is None:
            return {}

        try:
            context = cls._kg_bridge.discover_agent_context(agent_name)
            if context.get("observations"):
                Logger.info(
                    f"[{agent_name}] Discovered {len(context['observations'])} "
                    f"observations from Knowledge Graph",
                )
            return context
        except Exception as e:
            Logger.warning(f"[{agent_name}] Context discovery failed: {e}")
            return {}

    # ── The Golden Path ──────────────────────────────────────────────

    @classmethod
    def recall_or_execute(
        cls,
        agent_name: str,
        context: str,
        execution_fn: Any,
    ) -> Any:
        """Check memory first, execute only if necessary.

        1. If lobotomized → execute directly
        2. Query Pinecone for cached result
        3. If miss → execute, then fire-and-forget learn

        Args:
            agent_name: Agent class name (namespace).
            context: The prompt or input state to query.
            execution_fn: Callable to run if no memory exists.

        Returns:
            Either the cached result or the execution result.
        """
        if MetaLearningStorage._lobotomized:
            return execution_fn()

        cached = MetaLearningStorage.recall(context, agent_name)
        if cached is not None:
            return cached

        result = execution_fn()

        try:
            if result is not None:
                payload = result
                if not isinstance(result, dict):
                    payload = {"result": result, "_wrapped": True}
                asyncio.create_task(MetaLearningStorage.learn_async(context, agent_name, payload))
        except Exception as e:
            Logger.warning(f"[{agent_name}] DNA WRITE ERROR: Could not learn experience: {e}")

        return result

    # ── Reflection & Interaction ─────────────────────────────────────

    @classmethod
    def reflect_on_execution(
        cls,
        agent_name: str,
        task_id: str,
        status: str,
        error_type: str | None = None,
        error_message: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """Reflect on execution and synthesize truths for the Knowledge Graph."""
        if cls._kg_bridge is None:
            return

        try:
            from agentic_core.base_agents.knowledge_graph_bridge import ExecutionTrace

            trace = ExecutionTrace(
                agent_name=agent_name,
                task_id=task_id,
                status=status,
                error_type=error_type,
                error_message=error_message,
                duration_ms=duration_ms,
            )
            cls._kg_bridge.reflect_on_execution(trace)
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.warning(f"[{agent_name}] Reflection failed: {e}")

    @classmethod
    def record_agent_interaction(
        cls,
        caller_agent: str,
        callee_agent: str,
        success: bool,
        error_type: str | None = None,
    ) -> None:
        """Record an interaction between agents in the Knowledge Graph."""
        if cls._kg_bridge is None:
            return

        try:
            cls._kg_bridge.record_agent_interaction(
                caller_agent=caller_agent,
                callee_agent=callee_agent,
                success=success,
                error_type=error_type,
            )
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.warning(f"[{caller_agent}] Interaction recording failed: {e}")

    @classmethod
    def inherit_rules_from(cls, child_entity: str, parent_entity: str) -> None:
        """Establish rule inheritance from a parent entity."""
        if cls._kg_bridge is None:
            return

        try:
            cls._kg_bridge.establish_inheritance(
                child_entity=child_entity,
                parent_entity=parent_entity,
            )
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.warning(f"[{child_entity}] Inheritance setup failed: {e}")

    @classmethod
    def mark_incompatible_with(
        cls,
        entity_a: str,
        entity_b: str,
        reason: str,
    ) -> None:
        """Mark two entities as incompatible."""
        if cls._kg_bridge is None:
            return

        try:
            cls._kg_bridge.mark_incompatibility(
                entity_a=entity_a,
                entity_b=entity_b,
                reason=reason,
            )
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.warning(f"[{entity_a}] Incompatibility marking failed: {e}")

    @classmethod
    def add_architectural_observation(cls, agent_name: str, observation: str) -> None:
        """Add an architectural observation about an agent."""
        if cls._kg_bridge is None:
            return

        try:
            cls._kg_bridge.add_observation(
                entity_name=agent_name,
                observation=observation,
            )
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.warning(f"[{agent_name}] Observation recording failed: {e}")

    @classmethod
    def get_kg_stats(cls) -> dict[str, Any] | None:
        """Get statistics from the Knowledge Graph."""
        if cls._kg_bridge is None:
            return None
        try:
            return cls._kg_bridge.get_statistics()
        except Exception:
            return None

    @classmethod
    def reset_kg(cls) -> None:
        """Reset the Knowledge Graph Bridge (testing only)."""
        cls._kg_bridge = None
        Logger.info("[MetaLearningEngine] Knowledge Graph Bridge reset")
