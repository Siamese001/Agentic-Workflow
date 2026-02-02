from __future__ import annotations

import asyncio

"""
[PHASE 20+/21] Meta-Learning Mixin - The DNA of Collective Intelligence.

The genetic trait that enables any agent to access the Hive Mind.
Integrates with L4_state/memory for persistence and Knowledge Graph for reasoning.

MANDATORY: All core agents should inherit this for collective learning.

Storage Layer Roles:
- Pinecone (via SemanticCacheManager): Raw semantic search of past experiences
- Memory MCP (via KnowledgeGraphBridge): Architectural Truths and synthesized facts
- Graph Memory Bridge (Phase 21): Entity registration and MASTERED_TASK relations

Hardening Features:
- Circuit Breaker (_lobotomized): Graceful degradation when Hive Mind unavailable
- Thread-Safe Initialization: RLock prevents race conditions during singleton load
- Serialization Guard: Protects primary workflow from learning failures
- Knowledge Graph Integration: Entity-driven discovery and cross-agent learning
- DNA Mapping (Phase 21): Agents register as entities, promoted memories create relations

Usage:
    class MyAgent(MetaLearningMixin, SovereignBaseAgent):
        def execute(self, task):
            return self.recall_or_execute(
                context=task.description,
                execution_fn=lambda: self._do_work(task)
            )

[SSOT] Integrates with L4_state/memory/SemanticCacheManager, KnowledgeGraphBridge, and GraphMemoryBridge.
"""


import hashlib
import logging
import threading
from collections.abc import Callable
from typing import Any

Logger = logging.getLogger(__name__)

from agentic_core.base_agents.BaseMetaLearner import BaseMetaLearner


class MetaLearningMixin(BaseMetaLearner):
    """
    Mixin that provides collective intelligence capabilities to agents.

    Enables agents to:
    1. Recall previous experiences from the Hive Mind (Pinecone)
    2. Learn new experiences for future agents
    3. Bypass execution if a cached result exists (recall_or_execute)
    4. Discover architectural context from Knowledge Graph (Memory MCP)
    5. Record synthesized truths for cross-agent learning

    The namespace is automatically derived from the agent's class name,
    ensuring DNA segregation between different agent types.

    Thread Safety:
        Uses RLock for thread-safe singleton initialization.
        Circuit breaker prevents repeated connection attempts on failure.

    Knowledge Graph Integration:
        On startup, agents auto-discover their context from the KG.
        Execution traces are reflected as synthesized truths, not raw logs.
    """

    _memory = None  # Lazy-loaded Hive Mind singleton
    _memory_lock = threading.RLock()  # Thread safety for initialization
    _lobotomized = False  # Circuit breaker state
    _kg_bridge = None  # Knowledge Graph Bridge singleton
    _kg_lock = threading.RLock()  # Thread safety for KG initialization
    _graph_bridge = None  # Graph Memory Bridge singleton (Phase 21)
    _graph_lock = threading.RLock()  # Thread safety for Graph Bridge initialization

    def __init__(self, *args, **kwargs):
        """
        DNA Activation: Connect to Hive Mind and Knowledge Graph on instantiation.

        Phase 21: Also registers agent as entity in Graph Memory Bridge.
        """
        # Lazy-load the Hive Mind singleton
        self._ensure_memory_connection()

        # Lazy-load the Knowledge Graph Bridge
        self._ensure_kg_connection()

        # Lazy-load the Graph Memory Bridge (Phase 21)
        self._ensure_graph_bridge_connection()

        # Auto-discover context from Knowledge Graph
        self._discovered_context = self._discover_agent_context()

        # Phase 21: Register this agent as an entity in the Graph Memory Bridge
        self._register_agent_entity()

        super().__init__(*args, **kwargs)

    def _ensure_memory_connection(self) -> None:
        """
        Ensure connection to the Hive Mind singleton (thread-safe).

        Uses double-checked locking pattern with circuit breaker.
        If connection fails, enters lobotomized state to prevent
        repeated connection attempts.
        """
        # Circuit breaker: Skip if already lobotomized
        if MetaLearningMixin._lobotomized:
            return

        # Double-checked locking for thread safety
        if MetaLearningMixin._memory is None:
            with MetaLearningMixin._memory_lock:
                if MetaLearningMixin._memory is None:
                    try:
                        from agentic_core.L4_state.memory.semantic_cache_manager_config import (
                            SemanticCacheManager,
                        )

                        MetaLearningMixin._memory = SemanticCacheManager.get_instance()
                        Logger.debug(f"[{self.__class__.__name__}] Connected to Hive Mind")
                    except Exception as e:
                        # Activate circuit breaker
                        MetaLearningMixin._lobotomized = True
                        Logger.critical(
                            f"[{self.__class__.__name__}] LOBOTOMY PROTOCOL ACTIVE: "
                            f"Hive Mind unavailable ({e})"
                        )

    def _ensure_kg_connection(self) -> None:
        """
        Ensure connection to the Knowledge Graph Bridge (thread-safe).

        Resilient Mode: If KG is unavailable, logs warning but doesn't crash.
        """
        if MetaLearningMixin._kg_bridge is None:
            with MetaLearningMixin._kg_lock:
                if MetaLearningMixin._kg_bridge is None:
                    try:
                        from agentic_core.base_agents.knowledge_graph_bridge import (
                            KnowledgeGraphBridge,
                        )

                        MetaLearningMixin._kg_bridge = KnowledgeGraphBridge.get_instance()

                        # Register this agent as an entity
                        MetaLearningMixin._kg_bridge.register_agent(
                            self.__class__.__name__, agent_type="Agent"
                        )

                        Logger.debug(f"[{self.__class__.__name__}] Connected to Knowledge Graph")
                    except Exception as e:
                        # KG is optional - don't crash, just log
                        Logger.warning(
                            f"[{self.__class__.__name__}] Knowledge Graph unavailable: {e}"
                        )

    def _ensure_graph_bridge_connection(self) -> None:
        """
        [PHASE 21] Ensure connection to the Graph Memory Bridge (thread-safe).

        Resilient Mode: If unavailable, logs warning but doesn't crash.
        """
        if MetaLearningMixin._graph_bridge is None:
            with MetaLearningMixin._graph_lock:
                if MetaLearningMixin._graph_bridge is None:
                    try:
                        from agentic_core.L4_state.memory.graph_memory_bridge_types import (
                            GraphMemoryBridge,
                        )

                        MetaLearningMixin._graph_bridge = GraphMemoryBridge.get_instance()
                        Logger.debug(
                            f"[{self.__class__.__name__}] Connected to Graph Memory Bridge"
                        )
                    except Exception as e:
                        # Graph bridge is optional - don't crash, just log
                        Logger.warning(
                            f"[{self.__class__.__name__}] Graph Memory Bridge unavailable: {e}"
                        )

    def _register_agent_entity(self) -> None:
        """
        [PHASE 21] Register this agent as an entity in the Graph Memory Bridge.

        Called automatically on agent __init__.
        Idempotent: Will not create duplicate entities.
        """
        if MetaLearningMixin._graph_bridge is None:
            return

        try:
            MetaLearningMixin._graph_bridge.create_agent_entity(
                agent_name=self.__class__.__name__,
                agent_type="Agent",
                observations=[f"Agent {self.__class__.__name__} initialized"],
            )
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Agent entity registration failed: {e}")

    def _discover_agent_context(self) -> dict[str, Any]:
        """
        Auto-discover context for this agent from the Knowledge Graph.

        Queries for:
        - Observations about this agent
        - Relations with other agents
        - Inherited rules and protocols
        - Known incompatibilities

        Returns:
            Dictionary with discovered context
        """
        if MetaLearningMixin._kg_bridge is None:
            return {}

        try:
            context = MetaLearningMixin._kg_bridge.discover_agent_context(self.__class__.__name__)

            if context.get("observations"):
                Logger.info(
                    f"[{self.__class__.__name__}] Discovered {len(context['observations'])} "
                    f"observations from Knowledge Graph"
                )

            return context
        except Exception as e:
            Logger.warning(f"[{self.__class__.__name__}] Context discovery failed: {e}")
            return {}

    @property
    def _namespace(self) -> str:
        """Get the namespace for this agent (class name for DNA segregation)."""
        return self.__class__.__name__

    def _generate_context_hash(self, context: str) -> str:
        """
        Generate a standardized context hash.

        Combines agent class name with input hash to prevent memory collisions
        between different agent types using the same prompt.

        Args:
            context: The context string

        Returns:
            SHA256 hash of namespace:context
        """
        key = f"{self._namespace}:{context}"
        return hashlib.sha256(key.encode()).hexdigest()

    def recall_experience(self, context: str) -> dict[str, Any] | None:
        """
        Consult the Hive Mind for a solution to the current context.

        Args:
            context: The context string to query

        Returns:
            Previous result if found with high confidence, None otherwise
        """
        # Circuit breaker check
        if MetaLearningMixin._lobotomized or MetaLearningMixin._memory is None:
            return None

        try:
            result = MetaLearningMixin._memory.recall(context, self._namespace)
            if result:
                Logger.info(
                    f"[{self._namespace}] INSTINCT TRIGGERED: Recalled previous experience."
                )
            return result
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Recall error: {e}")
            return None

    async def learn_experience(self, context: str, result: dict[str, Any]) -> None:
        """
        [PHASE 25] NOW ASYNC: Uses fire-and-forget pattern.
        """
        if MetaLearningMixin._lobotomized or MetaLearningMixin._memory is None:
            return

        # [PHASE 25] Async Fire-and-Forget Pattern
        try:
            # Validate serialization BEFORE spawning background task
            import json

            _ = json.dumps(result)

            asyncio.create_task(self._async_learn_experience(context, result))
            Logger.debug(f"[{self._namespace}] Experience queued (async).")
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Failed to queue learning: {e}")

    async def _async_learn_experience(self, context: str, result: dict[str, Any]) -> None:
        """Background task for async learning."""
        try:
            await MetaLearningMixin._memory.learn_async(context, self._namespace, result)
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Async learn failed: {e}")

    def recall_or_execute(
        self,
        context: str,
        execution_fn: Callable[[], Any],
    ) -> Any:
        """
        The Golden Path: Check memory first, execute only if necessary.

        This is the primary pattern for meta-learning. It:
        1. Checks if a cached result exists for the context
        2. If found, returns the cached result (bypassing execution)
        3. If not found, executes the function and caches the result

        Circuit Breaker: If lobotomized, executes directly without memory access.
        Serialization Guard: Learning failures don't crash the agent.

        Args:
            context: The prompt or input state to query
            execution_fn: The lambda/function to run if no memory exists

        Returns:
            Either the cached result or the execution result

        Example:
            def process_task(self, task):
                return self.recall_or_execute(
                    context=f"process:{task.id}:{task.hash}",
                    execution_fn=lambda: self._expensive_operation(task)
                )
        """
        # Circuit Breaker: If lobotomized, execute blindly
        if MetaLearningMixin._lobotomized:
            return execution_fn()

        # Step 1: Check memory
        cached = self.recall_experience(context)
        if cached is not None:
            return cached

        # Step 2: Execute (no cached result found)
        # We do NOT catch execution exceptions here - let them bubble up
        # The agent's logic should handle its own runtime errors.
        result = execution_fn()

        # Step 3: Learn (store result for future)
        # Wrapped in try/except to protect primary workflow
        try:
            if result is not None:
                # Auto-wrap non-dict results for storage
                payload = result
                if not isinstance(result, dict):
                    payload = {"result": result, "_wrapped": True}

                # Create async task for learning (fire-and-forget)
                asyncio.create_task(self.learn_experience(context, payload))
        except Exception as e:
            # Never crash the agent because learning failed
            Logger.warning(f"[{self._namespace}] DNA WRITE ERROR: Could not learn experience: {e}")

        return result

    def get_memory_stats(self) -> dict[str, Any] | None:
        """Get statistics from the Hive Mind."""
        if MetaLearningMixin._lobotomized or MetaLearningMixin._memory is None:
            return None

        try:
            return MetaLearningMixin._memory.get_statistics()
        except Exception:
            return None

    def get_kg_stats(self) -> dict[str, Any] | None:
        """Get statistics from the Knowledge Graph."""
        if MetaLearningMixin._kg_bridge is None:
            return None

        try:
            return MetaLearningMixin._kg_bridge.get_statistics()
        except Exception:
            return None

    def reflect_on_execution(
        self,
        task_id: str,
        status: str,
        error_type: str | None = None,
        error_message: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """
        Reflect on an execution and synthesize truths for the Knowledge Graph.

        Instead of just saving raw logs to Pinecone, this method:
        1. Creates relations based on execution outcome
        2. Adds observations for failures
        3. Tracks weak nodes in the architecture

        Args:
            task_id: Identifier for the task
            status: "success", "failure", or "timeout"
            error_type: Type of error if failed
            error_message: Error message if failed
            duration_ms: Execution duration in milliseconds
        """
        if MetaLearningMixin._kg_bridge is None:
            return

        try:
            from agentic_core.base_agents.knowledge_graph_bridge import (
                ExecutionTrace,
            )

            trace = ExecutionTrace(
                agent_name=self.__class__.__name__,
                task_id=task_id,
                status=status,
                error_type=error_type,
                error_message=error_message,
                duration_ms=duration_ms,
            )

            MetaLearningMixin._kg_bridge.reflect_on_execution(trace)
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Reflection failed: {e}")

    def record_agent_interaction(
        self,
        callee_agent: str,
        success: bool,
        error_type: str | None = None,
    ) -> None:
        """
        Record an interaction with another agent in the Knowledge Graph.

        This builds the sub-atomic trace map for identifying weak nodes.

        Args:
            callee_agent: The agent that was called
            success: Whether the interaction succeeded
            error_type: Type of error if failed
        """
        if MetaLearningMixin._kg_bridge is None:
            return

        try:
            MetaLearningMixin._kg_bridge.record_agent_interaction(
                caller_agent=self.__class__.__name__,
                callee_agent=callee_agent,
                success=success,
                error_type=error_type,
            )
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Interaction recording failed: {e}")

    def inherit_rules_from(self, parent_entity: str) -> None:
        """
        Establish rule inheritance from a parent entity.

        This enables cross-agent learning and rule propagation.
        Example: RouterAgent inherits from Global_Safety_Protocol

        Args:
            parent_entity: The entity providing rules
        """
        if MetaLearningMixin._kg_bridge is None:
            return

        try:
            MetaLearningMixin._kg_bridge.establish_inheritance(
                child_entity=self.__class__.__name__,
                parent_entity=parent_entity,
            )
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Inheritance setup failed: {e}")

    def mark_incompatible_with(self, other_entity: str, reason: str) -> None:
        """
        Mark this agent as incompatible with another entity.

        This is an architectural truth that prevents problematic combinations.

        Args:
            other_entity: The incompatible entity
            reason: Why they are incompatible
        """
        if MetaLearningMixin._kg_bridge is None:
            return

        try:
            MetaLearningMixin._kg_bridge.mark_incompatibility(
                entity_a=self.__class__.__name__,
                entity_b=other_entity,
                reason=reason,
            )
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Incompatibility marking failed: {e}")

    def add_architectural_observation(self, observation: str) -> None:
        """
        Add an architectural observation about this agent.

        Observations are synthesized truths, not raw logs.
        Examples:
        - "GovernorAgent tends to fail when RouterAgent timeout is < 500ms"
        - "Phase 4 requires Asset Z to be loaded"

        Args:
            observation: The synthesized truth to record
        """
        if MetaLearningMixin._kg_bridge is None:
            return

        try:
            MetaLearningMixin._kg_bridge.add_observation(
                entity_name=self.__class__.__name__,
                observation=observation,
            )
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Observation recording failed: {e}")

    def learn_with_feedback(
        self,
        context: str,
        result: dict[str, Any],
        feedback_score: float,
    ) -> bool:
        """
        [PHASE 21] Learn with explicit feedback score for DNA promotion.

        When feedback_score >= 0.8 (promotion threshold), the memory is:
        1. Promoted to Long-Term DNA (Pinecone)
        2. A MASTERED_TASK relation is created in the Graph Memory Bridge

        Args:
            context: The context string
            result: The result to store
            feedback_score: Feedback score (0.0 to 1.0)

        Returns:
            True if promoted to DNA, False otherwise
        """
        # Circuit breaker check
        if MetaLearningMixin._lobotomized or MetaLearningMixin._memory is None:
            return False

        try:
            # Store in working memory with feedback score
            MetaLearningMixin._memory.learn(context, self._namespace, result, feedback_score)

            # Check if this qualifies for promotion (>= 0.8)
            promotion_threshold = getattr(MetaLearningMixin._memory, "promotion_threshold", 0.8)

            if feedback_score >= promotion_threshold:
                # Promote to Long-Term DNA
                promoted = MetaLearningMixin._memory.promote_to_long_term(
                    context, self._namespace, result, feedback_score
                )

                if promoted:
                    # Phase 21: Create MASTERED_TASK relation in Graph Memory Bridge
                    # CRITICAL: Sanitize context before writing to Graph to prevent PII leaks
                    # We reuse the sanitizer from the memory instance if available
                    sanitized_context = context
                    if hasattr(MetaLearningMixin._memory, "sanitizer"):
                        sanitized_context = MetaLearningMixin._memory.sanitizer.sanitize(context)

                    self._create_mastered_task_relation(sanitized_context, feedback_score)
                    Logger.info(
                        f"[{self._namespace}] DNA PROMOTION: Memory promoted with "
                        f"feedback_score={feedback_score:.2f}"
                    )
                    return True

            return False

        except Exception as e:
            Logger.warning(f"[{self._namespace}] Learn with feedback failed: {e}")
            return False

    def _create_mastered_task_relation(
        self,
        context: str,
        feedback_score: float,
    ) -> None:
        """
        [PHASE 21] Create MASTERED_TASK relation when memory is promoted.

        Args:
            context: The task context (will be hashed for entity name)
            feedback_score: The feedback score that triggered promotion
        """
        if MetaLearningMixin._graph_bridge is None:
            return

        try:
            MetaLearningMixin._graph_bridge.create_mastered_task_relation(
                agent_name=self.__class__.__name__,
                task_description=context,
                feedback_score=feedback_score,
            )
        except Exception as e:
            Logger.warning(f"[{self._namespace}] MASTERED_TASK relation creation failed: {e}")

    def get_graph_stats(self) -> dict[str, Any] | None:
        """
        [PHASE 21] Get statistics from the Graph Memory Bridge.
        """
        if MetaLearningMixin._graph_bridge is None:
            return None

        try:
            return MetaLearningMixin._graph_bridge.get_statistics()
        except Exception:
            return None

    @classmethod
    def reset_lobotomy(cls) -> None:
        """
        Reset the circuit breaker state (for testing/recovery).

        WARNING: Only use this if you've fixed the underlying infrastructure issue.
        """
        cls._lobotomized = False
        cls._memory = None
        Logger.info("[MetaLearningMixin] Lobotomy state reset - will attempt reconnection")

    @classmethod
    def reset_kg(cls) -> None:
        """
        Reset the Knowledge Graph Bridge (for testing only).
        """
        cls._kg_bridge = None
        Logger.info("[MetaLearningMixin] Knowledge Graph Bridge reset")

    @classmethod
    def reset_graph_bridge(cls) -> None:
        """
        [PHASE 21] Reset the Graph Memory Bridge (for testing only).
        """
        cls._graph_bridge = None
        Logger.info("[MetaLearningMixin] Graph Memory Bridge reset")
