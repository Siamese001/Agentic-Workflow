"""
[PHASE 20] Meta-Learning Mixin - The DNA of Collective Intelligence.

The genetic trait that enables any agent to access the Hive Mind.
Integrates with L4_state/memory for persistence.

MANDATORY: All core agents should inherit this for collective learning.

Hardening Features:
- Circuit Breaker (_lobotomized): Graceful degradation when Hive Mind unavailable
- Thread-Safe Initialization: RLock prevents race conditions during singleton load
- Serialization Guard: Protects primary workflow from learning failures

Usage:
    class MyAgent(MetaLearningMixin, SovereignBaseAgent):
        def execute(self, task):
            return self.recall_or_execute(
                context=task.description,
                execution_fn=lambda: self._do_work(task)
            )

[SSOT] Integrates with L4_state/memory/SemanticCacheManager.
"""
from __future__ import annotations

import hashlib
import logging
import threading
from typing import Any, Callable, Optional

Logger = logging.getLogger(__name__)


class MetaLearningMixin:
    """
    Mixin that provides collective intelligence capabilities to agents.
    
    Enables agents to:
    1. Recall previous experiences from the Hive Mind
    2. Learn new experiences for future agents
    3. Bypass execution if a cached result exists (recall_or_execute)
    
    The namespace is automatically derived from the agent's class name,
    ensuring DNA segregation between different agent types.
    
    Thread Safety:
        Uses RLock for thread-safe singleton initialization.
        Circuit breaker prevents repeated connection attempts on failure.
    """
    
    _memory = None  # Lazy-loaded singleton
    _memory_lock = threading.RLock()  # Thread safety for initialization
    _lobotomized = False  # Circuit breaker state
    
    def __init__(self, *args, **kwargs):
        """
        DNA Activation: Connect to Hive Mind immediately upon instantiation.
        """
        # Lazy-load the Hive Mind singleton
        self._ensure_memory_connection()
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
    
    @classmethod
    def reset_lobotomy(cls) -> None:
        """
        Reset the circuit breaker state (for testing/recovery).
        
        WARNING: Only use this if you've fixed the underlying infrastructure issue.
        """
        cls._lobotomized = False
        cls._memory = None
        Logger.info("[MetaLearningMixin] Lobotomy state reset - will attempt reconnection")
