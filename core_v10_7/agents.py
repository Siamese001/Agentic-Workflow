"""Agent base classes for v10.7."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from .constants import legacy_model_alias
from .services import track_metrics

if TYPE_CHECKING:  # pragma: no cover
    from .clients import AsyncBaseModelClient
    from .context import WorkflowContext

logger = logging.getLogger("core_v10_7")


# ============================================================================
# BaseAgent (v10.7-corrected)
# ============================================================================

class BaseAgent:
    """Base class for all agents with v10.7 context injection and service access."""

    def __init__(self, context: "WorkflowContext", debug_mode: bool = False):
        self.context = context
        self.config = context.config
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # v10.7 unified service injection
        self.prompt_manager = context.prompt_manager
        self.validator = context.response_validator
        self.budget_manager = context.context_budget_manager
        self.metrics = context.metrics_collector
        self.self_correction_manager = getattr(context, "self_correction_manager", None)
        self.policy_stack = getattr(context, "policy_stack", None)
        self.constitutional_engine = getattr(context, "constitutional_engine", None)
        self.prompt_injection_detector = getattr(context, "prompt_injection_detector", None)

        # v10.7 MCP integration
        self.mcp_clients = context.ensure_mcp_clients() if context.is_mcp_enabled() else {}

    # ----------------------------------------------------------------------
    # Logging Helpers
    # ----------------------------------------------------------------------

    def log_info(self, msg: str): 
        self.logger.info(f"[{self.__class__.__name__}] {msg}")

    def log_warning(self, msg: str): 
        self.logger.warning(f"[{self.__class__.__name__}] {msg}")

    def log_error(self, msg: str): 
        self.logger.error(f"[{self.__class__.__name__}] {msg}")

    def log_debug(self, msg: str):
        """Print debug logs only when explicitly enabled."""
        if self.debug_mode:
            self.logger.debug(f"[{self.__class__.__name__}] {msg}")

    # ----------------------------------------------------------------------
    # Feedback Logging (v10.7 Meta Learning)
    # ----------------------------------------------------------------------

    def log_feedback(self, workflow_id: str, task: str, feedback_type: str, details: Dict[str, Any]):
        """Write structured feedback entries to feedback log."""
        try:
            feedback_entry = {
                "timestamp": datetime.now().isoformat(),
                "workflow_id": workflow_id,
                "agent_name": self.__class__.__name__,
                "task": task,
                "feedback_type": feedback_type,
                "details": details,
                "metadata": {},
            }
            log_path = self.config.meta_loop_config.feedback_log_path
            os.makedirs(os.path.dirname(log_path), exist_ok=True)

            with open(log_path, "a") as f:
                json.dump(feedback_entry, f)
                f.write("\n")
        except Exception as e:
            self.log_error(f"Failed to log feedback: {e}")

    # ----------------------------------------------------------------------
    # LLM Client Retrieval (v10.7)
    # ----------------------------------------------------------------------

    def get_model_client(self, model_config_name: str) -> "AsyncBaseModelClient":
        """
        v10.7 dynamic model routing.
        Applies:
          - complexity-based routing
          - latency fallback
          - global failure injection (Fix #19/#24)
        """
        complexity = self.context.complexity
        model_key = model_config_name

        simple_key = f"{model_config_name}_simple"
        complex_key = f"{model_config_name}_complex"

        # --- 1. Complexity Routing ---
        if complexity == "simple" and hasattr(self.config.model_config, simple_key):
            model_key = simple_key
            self.log_debug(f"Complexity routing: using {simple_key}")
        elif complexity == "complex" and hasattr(self.config.model_config, complex_key):
            model_key = complex_key
            self.log_debug(f"Complexity routing: using {complex_key}")

        # --- 2. Latency-Based Fallback ---
        if model_key == complex_key:
            max_latency = self.config.performance_config.max_complex_model_latency_ms
            # FIXED: pull latency for the actual model key, not incorrect task name
            avg_latency = self.metrics.get_average_latency(
                agent_name=self.__class__.__name__,
                task_name=model_key,
            )

            if avg_latency and avg_latency > max_latency:
                self.log_warning(
                    f"LATENCY FALLBACK: {complex_key} avg latency "
                    f"({avg_latency:.0f}ms) > threshold ({max_latency}ms). "
                    f"Falling back to {simple_key}."
                )
                model_key = simple_key

                self.metrics.record(
                    agent_name=self.__class__.__name__,
                    task_name="latency_fallback",
                    duration_ms=0,
                    success=True,
                    metadata={
                        "complex_model": complex_key,
                        "avg_latency": avg_latency,
                        "simple_model": simple_key,
                    },
                )

        # --- 3. Resolve final model config ---
        if not hasattr(self.config.model_config, model_key):
            model_key = model_config_name

        model_cfg = getattr(self.config.model_config, model_key)

        client = self.context.get_model_client(
            provider=model_cfg.provider,
            model_name=legacy_model_alias(model_cfg.model_name),
        )

        # Inject runtime metadata
        client.workflow_id = self.context.workflow_id
        client.agent_name = self.__class__.__name__
        client.goal_state = self.prompt_manager.goal_state
        client.top_failures = self.prompt_manager.top_failures
        client.budget_manager = self.budget_manager
        client.latency_task_name = model_key

        return client

    # ----------------------------------------------------------------------
    # MCP Client Retrieval
    # ----------------------------------------------------------------------

    def get_mcp_client(self, name: str, default: Optional[Any] = None) -> Any:
        try:
            return self.context.get_mcp_client(name, default)
        except KeyError as exc:
            self.log_warning(str(exc))
            if default is not None:
                return default
            raise


# ============================================================================
# BaseTool — updated to v10.7 resiliency + caching
# ============================================================================

class BaseTool(BaseAgent):
    """Base interface for tools used by ReAct Conductors."""
    tool_name: str = "base_tool"

    @track_metrics("base_tool_run")
    async def run_async(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """
        Runs the tool with:
          - semantic + exact cache checks
          - runtime metrics
          - structured error envelope
        """

        # --- Sanitization: ensure tool_input is JSON-safe ---
        try:
            json.dumps(tool_input)
        except Exception:
            # Convert any non-serializable objects into safe strings
            tool_input = json.loads(json.dumps(tool_input, default=str))

        cache_manager = self.context.cache_manager

        # --- 1. Exact/semantic cache ---
        if self.config.caching_config.enable_tool_caching:
            cached = cache_manager.get_tool_cache(self.tool_name, tool_input)
            if cached:
                self.log_info(f"Tool Cache HIT: {self.tool_name}")
                return cached

        self.log_info(f"Tool Cache MISS: {self.tool_name}")

        # --- 2. Execute tool ---
        try:
            result = await self._run_async_internal(tool_input, workflow_id)
        except Exception as exc:
            self.log_error(f"Tool execution failed: {exc}")
            return {
                "status": "error",
                "error": str(exc),
                "tool": self.tool_name,
                "workflow_id": workflow_id,
            }

        # --- 3. Cache result ---
        if self.config.caching_config.enable_tool_caching:
            cache_manager.set_tool_cache(self.tool_name, tool_input, result)

        return result

    # Subclasses must implement internal logic
    async def _run_async_internal(self, tool_input: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        raise NotImplementedError(
            f"Tool {self.__class__.__name__} must implement _run_async_internal"
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.tool_name,
            "description": self.__doc__ or "No description provided.",
            "parameters": {"type": "object", "properties": {}},
        }


__all__ = [
    "BaseAgent",
    "BaseTool",
]
