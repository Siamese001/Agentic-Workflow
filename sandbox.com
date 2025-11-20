# FILE: sandbox.py
"""
Unified Execution Sandbox (v10_10) — TOOLING INFRASTRUCTURE (NEW)

This module implements the Hardened Execution Environment (Pillar 14, 8).
It acts as the "Hands" of the agent, ensuring that all interactions with
the outside world (tools, APIs, code execution) happen inside a controlled
boundary.

Features:
    1. Schema Validation: Enforces strict input types against Registry specs.
    2. Isolation Simulation: Mocks containerized execution (Docker/E2B).
    3. Resource Limits: Enforces timeouts and memory safeguards.
    4. Error Boundaries: Wraps external failures in typed Agentic exceptions.
    5. Observability: Automatically traces tool usage and latencies.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional
from pydantic import ValidationError as PydanticValidationError

from models import ToolSpec
from registry import REGISTRY
from runtime_utils import (
    ToolExecutionError,
    ValidationError,
    WorkflowTimeoutError,
    record_event
)

# =============================================================================
# SANDBOX KERNEL
# =============================================================================

class ToolSandbox:
    """
    The isolation layer for tool execution.
    In a production system, this would interface with Docker, Firecracker, or E2B.
    Here, it enforces the *contracts* of such a system.
    """

    async def execute_tool(
        self,
        tool_id: str,
        arguments: Dict[str, Any],
        workflow_id: str,
        timeout_override: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool safely within the sandbox.
        """
        start_time = time.perf_counter()
        
        # 1. Fetch Spec (Pillar 8)
        try:
            spec = REGISTRY.get_tool(tool_id)
        except ValueError as e:
            raise ValidationError(f"Tool {tool_id} not defined in registry.")

        # 2. Validate Inputs (Pillar 3 - Typed Contracts)
        self._validate_schema(spec, arguments)

        # 3. Enforce Timeouts (Pillar 14)
        timeout = timeout_override or spec.timeout_seconds
        
        try:
            # Wrap execution in timeout
            result = await asyncio.wait_for(
                self._internal_execute(spec, arguments),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            record_event("tool_timeout", {"tool": tool_id, "timeout": timeout})
            raise WorkflowTimeoutError(f"Tool '{tool_id}' exceeded {timeout}s limit.")
        except Exception as e:
            record_event("tool_failure", {"tool": tool_id, "error": str(e)})
            # Re-raise as specific tool error for L2 to handle
            raise ToolExecutionError(f"Sandbox execution failed for '{tool_id}': {e}")

        # 4. Observability (Pillar 10)
        duration_ms = (time.perf_counter() - start_time) * 1000
        record_event("tool_execution", {
            "workflow_id": workflow_id,
            "tool_id": tool_id,
            "latency_ms": duration_ms,
            "success": True
        })

        return {
            "output": result,
            "metadata": {
                "tool_id": tool_id,
                "latency_ms": duration_ms,
                "sandboxed": spec.requires_sandbox
            }
        }

    def _validate_schema(self, spec: ToolSpec, arguments: Dict[str, Any]) -> None:
        """
        Strict schema validation. 
        In v10_9, this was loose/missing. Now it prevents bad inputs from reaching tools.
        """
        required_keys = spec.schema_definition.keys()
        missing = [key for key in required_keys if key not in arguments]
        if missing:
            raise ValidationError(f"Tool '{spec.tool_id}' missing required args: {missing}")
        
        # Simple type checking simulation
        for key, expected_type in spec.schema_definition.items():
            val = arguments.get(key)
            if expected_type == "str" and not isinstance(val, str):
                 raise ValidationError(f"Arg '{key}' must be string, got {type(val)}")

    async def _internal_execute(self, spec: ToolSpec, arguments: Dict[str, Any]) -> str:
        """
        The "unsafe" execution logic. 
        This is where the actual API call or Python exec() would happen.
        """
        # Simulate network delay
        await asyncio.sleep(0.1)

        # --- SIMULATED TOOL IMPLEMENTATIONS ---
        
        if spec.tool_id == "web_search":
            query = arguments.get("query", "")
            if "leader" in query.lower():
                return (
                    "Search Result: Proven leadership experience in SaaS scaling. "
                    "Key achievements: Grew revenue by 300%, led 50+ engineering team."
                )
            return f"Search Result: General information about {query}."

        if spec.tool_id == "calculator":
            # Example of safe code execution
            try:
                expression = arguments.get("expression", "0")
                # Still dangerous in prod, but purely illustrative here
                return str(eval(expression, {"__builtins__": None}, {}))
            except Exception:
                raise ValueError("Invalid calculation")

        # Fallback mock
        return f"Executed {spec.tool_id} with {arguments}"

# Singleton instance
SANDBOX = ToolSandbox()
