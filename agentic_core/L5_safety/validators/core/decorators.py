from __future__ import annotations

"""
Decorators for Agent Standardization

This module provides decorators that standardize agent behavior,
ensuring consistent input/output handling and error containment.

DECORATORS:
    @standard_heal: Standardizes heal_repository() methods
        - Input normalization (ensures dry_run/execute exist)
        - Output normalization (converts legacy dicts to HealResult schema)
        - Error containment (catches crashes, returns valid HealResult)

USAGE:

    class MyAgent:
        @standard_heal
        def heal_repository(self, dry_run=True, execute=False, **kwargs):
            # Your healing logic here
            return {"renamed": 5}  # Legacy format - will be normalized
"""


import functools
import logging
import time
import traceback
from collections.abc import Callable
from typing import Any, TypeVar, cast

Logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


# Canonical HealResult schema keys
HEAL_RESULT_SCHEMA = {
    "violations_found": 0,
    "violations_fixed": 0,
    "status": "UNKNOWN",
    "errors": 0,
    "skipped": 0,
    "execution_time_ms": 0.0,
    "error_message": None,
}


def _warn_non_canonical_keys(result: dict[str, Any], agent_name: str) -> None:
    """
    Emit warnings for non-canonical keys in heal_repository return values.

    This helps developers migrate to canonical keys for better schema compliance.
    """
    if not isinstance(result, dict):
        return

    # Define canonical keys for validation
    canonical_keys = {
        "violations_found",
        "violations_fixed",
        "errors",
        "skipped",
        "status",
        "execution_time_ms",
        "error_message",
    }

    for key in result:
        if key not in canonical_keys:
            Logger.warning(
                f"[standard_heal] {agent_name}: Non-canonical key '{key}' detected. "
                f"Consider using canonical keys for better schema compliance. "
                f"See: agentic_core/L5_safety/validators/decorators.py"
            )


def _normalize_heal_result(
    result: Any, execution_time_ms: float, agent_name: str = ""
) -> dict[str, Any]:
    """
    Normalize a heal result to the canonical HealResult schema.

    Handles various legacy formats and converts them to the standard schema:
        {
            "violations_found": int,
            "violations_fixed": int,
            "status": str,  # 'PASS', 'FAIL', 'ERROR', 'SKIPPED'
            "errors": int,
            "skipped": int,
            "execution_time_ms": float,
            "error_message": Optional[str],
        }

    Args:
        result: Raw result from heal_repository (may be dict, int, bool, etc.)
        execution_time_ms: Execution time in milliseconds
        agent_name: Name of the agent (for warning messages)

    Returns:
        Normalized HealResult dictionary
    """
    # Warn about non-canonical keys (helps developers migrate)
    if isinstance(result, dict):
        _warn_non_canonical_keys(result, agent_name)

    # Start with default schema
    normalized: dict[str, Any] = {
        **HEAL_RESULT_SCHEMA,
        "execution_time_ms": execution_time_ms,
    }

    # Handle None result
    if result is None:
        normalized["status"] = "SKIPPED"
        normalized["skipped"] = 1
        return normalized

    # Handle boolean result
    if isinstance(result, bool):
        normalized["status"] = "PASS" if result else "FAIL"
        return normalized

    # Handle integer result (assume it's violation count)
    if isinstance(result, int):
        normalized["violations_found"] = result
        normalized["status"] = "PASS" if result == 0 else "FAIL"
        return normalized

    # Handle dict result
    if isinstance(result, dict):
        # Copy canonical keys directly
        for key in HEAL_RESULT_SCHEMA.keys():
            if key in result:
                normalized[key] = result[key]

        # Preserve error_message if present
        if "error_message" in result:
            normalized["error_message"] = result["error_message"]
        elif "error" in result:
            normalized["error_message"] = str(result["error"])
        elif "message" in result:
            normalized["error_message"] = result["message"]

        # Determine status if not explicitly set
        if normalized["status"] == "UNKNOWN":
            if normalized.get("error_message") or normalized.get("errors", 0) > 0:
                normalized["status"] = "ERROR"
            elif normalized.get("skipped", 0) > 0 and normalized.get("violations_found", 0) == 0:
                normalized["status"] = "SKIPPED"
            elif normalized.get("violations_found", 0) == 0:
                normalized["status"] = "PASS"
            elif normalized.get("violations_fixed", 0) >= normalized.get("violations_found", 0):
                normalized["status"] = "PASS"
            else:
                normalized["status"] = "FAIL"

        # Preserve original result for debugging
        normalized["_raw_result"] = result

        return normalized

    # Handle unexpected types
    Logger.warning(f"[standard_heal] Unexpected result type: {type(result)}")
    normalized["status"] = "ERROR"
    normalized["error_message"] = f"Unexpected result type: {type(result)}"
    return normalized


def _normalize_heal_inputs(kwargs: dict[str, Any]) -> tuple[bool, bool, dict[str, Any]]:
    """
    Normalize heal_repository inputs.

    Ensures dry_run and execute parameters exist with safe defaults.

    Args:
        kwargs: Keyword arguments passed to heal_repository

    Returns:
        Tuple of (dry_run, execute, remaining_kwargs)
    """
    # Extract dry_run with safe default (True = safe, no changes)
    dry_run = kwargs.pop("dry_run", True)

    # Extract execute with safe default (False = no changes)
    execute = kwargs.pop("execute", False)

    # Ensure boolean types
    if not isinstance(dry_run, bool):
        dry_run = bool(dry_run)
    if not isinstance(execute, bool):
        execute = bool(execute)

    return dry_run, execute, kwargs


def standard_heal(func: F) -> F:
    """
    Decorator that standardizes heal_repository() methods.

    This decorator provides:
    1. Input Normalization: Ensures dry_run and execute args exist with safe defaults
    2. Output Normalization: Converts legacy dicts to canonical HealResult schema
    3. Error Containment: Catches crashes and returns valid HealResult with status='ERROR'

    UPDATED: Supports Phase 20 HealerMixin signature (depth, _call_path).

    Usage:
        class MyAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, depth=0, _call_path=None, **kwargs):
                # Your healing logic
                return {"renamed": 5}  # Will be normalized to {"violations_fixed": 5, ...}

    Args:
        func: The heal_repository method to decorate

    Returns:
        Decorated function with standardized behavior
    """

    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
        start_time = time.time()
        agent_name = self.__class__.__name__

        try:
            # Input normalization
            dry_run, execute, remaining_kwargs = _normalize_heal_inputs(kwargs)

            # Extract Phase 20 signature parameters with defaults
            depth = remaining_kwargs.pop("depth", 0)
            _call_path = remaining_kwargs.pop("_call_path", None)

            Logger.debug(
                f"[standard_heal] {agent_name}.{func.__name__} "
                f"(dry_run={dry_run}, execute={execute}, depth={depth})"
            )

            # Call the actual method with Phase 20 signature
            result = func(
                self,
                *args,
                dry_run=dry_run,
                execute=execute,
                depth=depth,
                _call_path=_call_path,
                **remaining_kwargs,
            )

            # Output normalization (pass agent_name for warning messages)
            execution_time_ms = (time.time() - start_time) * 1000
            normalized = _normalize_heal_result(result, execution_time_ms, agent_name)

            Logger.debug(
                f"[standard_heal] {agent_name}.{func.__name__} completed: "
                f"status={normalized['status']}, "
                f"violations={normalized['violations_found']}, "
                f"fixed={normalized['violations_fixed']}"
            )

            return normalized

        except Exception as e:
            # Error containment - never let the method crash
            execution_time_ms = (time.time() - start_time) * 1000

            Logger.error(
                f"[standard_heal] {agent_name}.{func.__name__} crashed: {e}\n"
                f"{traceback.format_exc()}"
            )

            return {
                **HEAL_RESULT_SCHEMA,
                "status": "ERROR",
                "errors": 1,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
                "_exception_type": type(e).__name__,
                "_traceback": traceback.format_exc(),
            }

    return cast(F, wrapper)


def standard_heal_async(func: F) -> F:
    """
    Async version of @standard_heal decorator.

    Provides the same standardization for async heal_repository methods.

    UPDATED: Supports Phase 20 HealerMixin signature (depth, _call_path).

    Usage:
        class MyAgent:
            @standard_heal_async
            async def heal_repository(self, dry_run=True, execute=False, depth=0, _call_path=None, **kwargs):
                # Your async healing logic
                return {"renamed": 5}
    """

    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
        start_time = time.time()
        agent_name = self.__class__.__name__

        try:
            # Input normalization
            dry_run, execute, remaining_kwargs = _normalize_heal_inputs(kwargs)

            # Extract Phase 20 signature parameters with defaults
            depth = remaining_kwargs.pop("depth", 0)
            _call_path = remaining_kwargs.pop("_call_path", None)

            Logger.debug(
                f"[standard_heal_async] {agent_name}.{func.__name__} "
                f"(dry_run={dry_run}, execute={execute}, depth={depth})"
            )

            # Call the actual async method with Phase 20 signature
            result = await func(
                self,
                *args,
                dry_run=dry_run,
                execute=execute,
                depth=depth,
                _call_path=_call_path,
                **remaining_kwargs,
            )

            # Output normalization (pass agent_name for warning messages)
            execution_time_ms = (time.time() - start_time) * 1000
            normalized = _normalize_heal_result(result, execution_time_ms, agent_name)

            return normalized

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            Logger.error(
                f"[standard_heal_async] {agent_name}.{func.__name__} crashed: {e}\n"
                f"{traceback.format_exc()}"
            )

            return {
                **HEAL_RESULT_SCHEMA,
                "status": "ERROR",
                "errors": 1,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
            }

    return cast(F, wrapper)


__all__ = [
    "standard_heal",
    "standard_heal_async",
    "HEAL_RESULT_SCHEMA",
]
