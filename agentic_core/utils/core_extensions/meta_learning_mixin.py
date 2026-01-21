"""
[PHASE 20+] Meta-Learning Mixin - The DNA of Collective Intelligence.

The genetic trait that enables any agent to access the Hive Mind.
Integrates with L4_state/memory for persistence and Knowledge Graph for reasoning.

MANDATORY: All core agents should inherit this for collective learning.

Storage Layer Roles:
- Pinecone (via SemanticCacheManager): Raw semantic search of past experiences
- Memory MCP (via KnowledgeGraphBridge): Architectural Truths and synthesized facts

Hardening Features:
- Circuit Breaker (_lobotomized): Graceful degradation when Hive Mind unavailable
- Thread-Safe Initialization: RLock prevents race conditions during singleton load
- Serialization Guard: Protects primary workflow from learning failures
- Knowledge Graph Integration: Entity-driven discovery and cross-agent learning

Usage:
    class MyAgent(MetaLearningMixin, SovereignBaseAgent):
        def execute(self, task):
            return self.recall_or_execute(
                context=task.description,
                execution_fn=lambda: self._do_work(task)
            )

[SSOT] Integrates with L4_state/memory/SemanticCacheManager and KnowledgeGraphBridge.
"""
from __future__ import annotations

import hashlib
import logging
import threading
import time
from typing import Any, Callable, Optional

Logger = logging.getLogger(__name__)


class MetaLearningMixin:
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
    
    def __init__(self, *args, **kwargs):
        """
        DNA Activation: Connect to Hive Mind and Knowledge Graph on instantiation.
        """
        # Lazy-load the Hive Mind singleton
        self._ensure_memory_connection()
        
        # Lazy-load the Knowledge Graph Bridge
        self._ensure_kg_connection()
        
        # Auto-discover context from Knowledge Graph
        self._discovered_context = self._discover_agent_context()
        
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
                        from agentic_core.L4_state.memory.SemanticCacheManager import (
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
                        from agentic_core.utils.core_extensions.knowledge_graph_bridge import (
                            KnowledgeGraphBridge,
                        )
                        MetaLearningMixin._kg_bridge = KnowledgeGraphBridge.get_instance()
                        
                        # Register this agent as an entity
                        MetaLearningMixin._kg_bridge.register_agent(
                            self.__class__.__name__,
                            agent_type="Agent"
                        )
                        
                        Logger.debug(f"[{self.__class__.__name__}] Connected to Knowledge Graph")
                    except Exception as e:
                        # KG is optional - don't crash, just log
                        Logger.warning(
                            f"[{self.__class__.__name__}] Knowledge Graph unavailable: {e}"
                        )
    
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
            context = MetaLearningMixin._kg_bridge.discover_agent_context(
                self.__class__.__name__
            )
            
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
    
    def recall_experience(self, context: str) -> Optional[dict[str, Any]]:
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
                Logger.info(f"[{self._namespace}] INSTINCT TRIGGERED: Recalled previous experience.")
            return result
        except Exception as e:
            Logger.warning(f"[{self._namespace}] Recall error: {e}")
            return None
    
    def learn_experience(self, context: str, result: dict[str, Any]) -> None:
        """
        Teach the Hive Mind the result of the current action.
        
        Includes serialization guard to protect primary workflow from
        learning failures (e.g., non-serializable results).
        
        Args:
            context: The context string
            result: The result to store for future recall
        """
        # Circuit breaker check
        if MetaLearningMixin._lobotomized or MetaLearningMixin._memory is None:
            return
        
        try:
            MetaLearningMixin._memory.learn(context, self._namespace, result)
            Logger.debug(f"[{self._namespace}] Experience committed to Hive Mind.")
        except Exception as e:
            # Never crash the agent because learning failed
            Logger.warning(f"[{self._namespace}] Failed to learn (serialization/connection): {e}")
    
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
                
                self.learn_experience(context, payload)
        except Exception as e:
            # Never crash the agent because learning failed
            Logger.warning(f"[{self._namespace}] DNA WRITE ERROR: Could not learn experience: {e}")
        
        return result
    
    def get_memory_stats(self) -> Optional[dict[str, Any]]:
        """Get statistics from the Hive Mind."""
        if MetaLearningMixin._lobotomized or MetaLearningMixin._memory is None:
            return None
        
        try:
            return MetaLearningMixin._memory.get_statistics()
        except Exception:
            return None
    
    def get_kg_stats(self) -> Optional[dict[str, Any]]:
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
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
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
            from agentic_core.utils.core_extensions.knowledge_graph_bridge import (
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
        error_type: Optional[str] = None,
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
