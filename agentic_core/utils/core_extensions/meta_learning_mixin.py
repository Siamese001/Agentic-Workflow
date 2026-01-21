"""
[PHASE 20] Meta-Learning Mixin - The DNA of Collective Intelligence.

The genetic trait that enables any agent to access the Hive Mind.
Integrates with L4_state/memory for persistence.

MANDATORY: All core agents should inherit this for collective learning.

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
    """
    
    _memory = None  # Lazy-loaded singleton
    
    def __init__(self, *args, **kwargs):
        """
        DNA Activation: Connect to Hive Mind immediately upon instantiation.
        """
        # Lazy-load the Hive Mind singleton
        self._ensure_memory_connection()
        super().__init__(*args, **kwargs)
    
    def _ensure_memory_connection(self) -> None:
        """Ensure connection to the Hive Mind singleton."""
        if MetaLearningMixin._memory is None:
            try:
                from agentic_core.L4_state.memory.SemanticCacheManager import (
                    SemanticCacheManager,
                )
                MetaLearningMixin._memory = SemanticCacheManager.get_instance()
                Logger.debug(f"[{self.__class__.__name__}] Connected to Hive Mind")
            except Exception as e:
                Logger.warning(f"[{self.__class__.__name__}] Hive Mind unavailable: {e}")
    
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
        if MetaLearningMixin._memory is None:
            return None
        
        try:
            result = MetaLearningMixin._memory.recall(context, self._namespace)
            if result:
                Logger.info(f"[{self._namespace}] INSTINCT TRIGGERED: Recalled previous experience.")
            return result
        except Exception as e:
            Logger.debug(f"[{self._namespace}] Recall failed: {e}")
            return None
    
    def learn_experience(self, context: str, result: dict[str, Any]) -> None:
        """
        Teach the Hive Mind the result of the current action.
        
        Args:
            context: The context string
            result: The result to store for future recall
        """
        if MetaLearningMixin._memory is None:
            return
        
        try:
            MetaLearningMixin._memory.learn(context, self._namespace, result)
            Logger.debug(f"[{self._namespace}] Experience learned and stored.")
        except Exception as e:
            Logger.debug(f"[{self._namespace}] Learn failed: {e}")
    
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
        # Step 1: Check memory
        cached = self.recall_experience(context)
        if cached is not None:
            return cached
        
        # Step 2: Execute (no cached result found)
        try:
            result = execution_fn()
        except Exception as e:
            Logger.error(f"[{self._namespace}] Execution failed: {e}")
            raise
        
        # Step 3: Learn (store result for future)
        if result is not None:
            # Convert to dict if needed for storage
            if isinstance(result, dict):
                self.learn_experience(context, result)
            else:
                self.learn_experience(context, {"result": result})
        
        return result
    
    def get_memory_stats(self) -> Optional[dict[str, Any]]:
        """Get statistics from the Hive Mind."""
        if MetaLearningMixin._memory is None:
            return None
        
        try:
            return MetaLearningMixin._memory.get_statistics()
        except Exception:
            return None
