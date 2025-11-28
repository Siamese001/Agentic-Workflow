"""Agent base classes for v10.7."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from .constants import legacy_model_alias
from .services import track_metrics

if TYPE_CHECKING:  # pragma: no cover - typing helpers
    from .clients import AsyncBaseModelClient
    from .context import WorkflowContext

logger = logging.getLogger("core_v10_7")


class BaseAgent:
    """Base class for all agents with v10.7 context injection"""
    
    def __init__(self, context: 'WorkflowContext', debug_mode: bool = False):
        self.context = context
        self.config = context.config
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        self.prompt_manager = context.prompt_manager
        self.validator = context.response_validator
        self.budget_manager = context.context_budget_manager
        self.metrics = context.metrics_collector
        self.mcp_clients = context.ensure_mcp_clients() if context.is_mcp_enabled() else {}

    def log_info(self, message: str): self.logger.info(f"[{self.__class__.__name__}] {message}")
    def log_warning(self, message: str): self.logger.warning(f"[{self.__class__.__name__}] {message}")
    def log_error(self, message: str): self.logger.error(f"[{self.__class__.__name__}] {message}")
    def log_debug(self, message: str):
        if self.debug_mode: self.logger.debug(f"[{self.__class__.__name__}] {message}")
    
    def log_feedback(self, workflow_id: str, task: str, feedback_type: str, details: Dict[str, Any]):
        try:
            feedback_entry = {
                "timestamp": datetime.now().isoformat(), "workflow_id": workflow_id,
                "agent_name": self.__class__.__name__, "task": task,
                "feedback_type": feedback_type, "details": details, "metadata": {}
            }
            feedback_log_path = self.config.meta_loop_config.feedback_log_path
            os.makedirs(os.path.dirname(feedback_log_path), exist_ok=True)
            with open(feedback_log_path, 'a') as f:
                json.dump(feedback_entry, f)
                f.write('\n')
        except Exception as e:
            self.log_error(f"Failed to log feedback: {e}")
    
    def get_model_client(self, model_config_name: str) -> "AsyncBaseModelClient":
        """
        v10.7 (Fix #15): Gets model client.
        Routes based on complexity, cost, and latency.
        """
        
        complexity = self.context.complexity
        model_key = model_config_name
        
        simple_key = f"{model_config_name}_simple"
        complex_key = f"{model_config_name}_complex"
        
        # 1. Dynamic Model Routing (Fix #2)
        if complexity == "simple" and hasattr(self.config.model_config, simple_key):
            model_key = simple_key
            self.log_debug(f"Dynamic routing: Using '{simple_key}' for simple task")
        elif complexity == "complex" and hasattr(self.config.model_config, complex_key):
            model_key = complex_key
            self.log_debug(f"Dynamic routing: Using '{complex_key}' for complex task")
        
        # 2. Cost/Latency-Based Routing (Fix #15)
        if model_key == complex_key:
            max_latency = self.config.performance_config.max_complex_model_latency_ms
            avg_latency = self.metrics.get_average_latency(
                "AsyncBaseModelClient", complex_key # Task name must match client
            )
            if avg_latency and avg_latency > max_latency:
                self.log_warning(
                    f"LATENCY FALLBACK: {complex_key} avg latency ({avg_latency:.0f}ms) "
                    f"> threshold ({max_latency}ms). Falling back to {simple_key}."
                )
                model_key = simple_key
                # Log this fallback as a warning event
                self.metrics.record(
                    agent_name=self.__class__.__name__,
                    task_name="latency_fallback",
                    duration_ms=0,
                    success=True,
                    metadata={"complex_model": complex_key, "avg_latency": avg_latency}
                )
        
        if not hasattr(self.config.model_config, model_key):
            model_key = model_config_name
            
        model_config = getattr(self.config.model_config, model_key)

        client = self.context.get_model_client(
            model_config.provider,
            legacy_model_alias(model_config.model_name),
        )
        client.workflow_id = self.context.workflow_id
        client.agent_name = self.__class__.__name__
        # v10.7 (Fix #19, #24): Inject prompt context
        client.goal_state = self.prompt_manager.goal_state
        client.top_failures = self.prompt_manager.top_failures
        client.budget_manager = self.budget_manager

        return client

    def get_mcp_client(self, name: str, default: Optional[Any] = None) -> Any:
        """Retrieve a configured MCP client by name."""

        try:
            return self.context.get_mcp_client(name, default)
        except KeyError as exc:
            self.log_warning(str(exc))
            if default is not None:
                return default
            raise
        
# ============================================================================
# v10.7: BASE TOOL INTERFACE (Preserved)
# ============================================================================

class BaseTool(BaseAgent):
    """Base interface for tools used by ReAct Conductors"""
    tool_name: str = "base_tool"
    
    @track_metrics('base_tool_run')
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """v10.7: Wrapper to implement tool caching."""
        if not self.config.caching_config.enable_tool_caching:
            return await self._run_async_internal(tool_input, workflow_id)
            
        cache_manager = self.context.cache_manager
        cached_result = cache_manager.get_tool_cache(self.tool_name, tool_input)
        
        if cached_result:
            self.log_info(f"Tool Cache HIT: {self.tool_name}")
            return cached_result
        
        self.log_info(f"Tool Cache MISS: {self.tool_name}")
        result = await self._run_async_internal(tool_input, workflow_id)
        
        cache_manager.set_tool_cache(self.tool_name, tool_input, result)
        return result

    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Subclasses must implement their logic here"""
        raise NotImplementedError(f"Tool {self.__class__.__name__} must implement _run_async_internal")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.tool_name,
            "description": self.__doc__ or "No description",
            "parameters": {"type": "object", "properties": {}}
        }


__all__ = ["BaseAgent", "BaseTool"]

# ============================================================================
# ROW 6: ASYNC LLM CLIENTS (v10.7: Fix #29 - Idempotency)
# ============================================================================

