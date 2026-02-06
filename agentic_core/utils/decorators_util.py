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
import os
import time
import traceback
from collections.abc import Callable
from typing import Any, TypeVar, cast

from agentic_core.runtime.exceptions import HealExecutionError

Logger = logging.getLogger(__name__)

# Environment variable to control whether heal errors should raise exceptions
# Set to "1" or "true" to enable strict mode (raises on error)
HEAL_STRICT_MODE = os.environ.get("HEAL_STRICT_MODE", "false").lower() in ("1", "true")

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

# Legacy key mappings to canonical keys
LEGACY_KEY_MAPPINGS = {
    # violations_found mappings
    "violations": "violations_found",
    "issues": "violations_found",
    "problems": "violations_found",
    "findings": "violations_found",
    "count": "violations_found",
    # violations_fixed mappings
    "fixed": "violations_fixed",
    "repaired": "violations_fixed",
    "healed": "violations_fixed",
    "resolved": "violations_fixed",
    "renamed": "violations_fixed",  # Common legacy key
    "moved": "violations_fixed",
    "deleted": "violations_fixed",
    "created": "violations_fixed",
    # errors mappings
    "error_count": "errors",
    "failures": "errors",
    # skipped mappings
    "skip_count": "skipped",
    "ignored": "skipped",
}


def _normalize_heal_result(result: Any, execution_time_ms: float) -> dict[str, Any]:
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

    Returns:
        Normalized HealResult dictionary
    """
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
        # First, map legacy keys to canonical keys
        for legacy_key, canonical_key in LEGACY_KEY_MAPPINGS.items():
            if legacy_key in result and canonical_key not in result:
                value = result[legacy_key]
                if isinstance(value, int | float):
                    normalized[canonical_key] = int(value)

        # Then, copy canonical keys directly
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

    Usage:
        class MyAgent:
            @standard_heal
            def heal_repository(self, dry_run=True, execute=False, **kwargs):
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

            Logger.debug(
                f"[standard_heal] {agent_name}.{func.__name__} (dry_run={dry_run}, execute={execute})",
            )

            # Call the actual method
            result = func(self, *args, dry_run=dry_run, execute=execute, **remaining_kwargs)

            # Output normalization
            execution_time_ms = (time.time() - start_time) * 1000
            normalized = _normalize_heal_result(result, execution_time_ms)

            Logger.debug(
                f"[standard_heal] {agent_name}.{func.__name__} completed: "
                f"status={normalized['status']}, "
                f"violations={normalized['violations_found']}, "
                f"fixed={normalized['violations_fixed']}",
            )

            return normalized

        except Exception as e:
            # Error handling with optional strict mode
            execution_time_ms = (time.time() - start_time) * 1000

            Logger.error(
                f"[standard_heal] {agent_name}.{func.__name__} crashed: {e}\n{traceback.format_exc()}",
            )

            # In strict mode, raise HealExecutionError for proper error propagation
            if HEAL_STRICT_MODE:
                raise HealExecutionError(
                    agent_name=agent_name,
                    method_name=func.__name__,
                    message=f"Heal operation failed: {e}",
                    original_error=e,
                ) from e

            # Legacy behavior: return error dict for backward compatibility
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

    Usage:
        class MyAgent:
            @standard_heal_async
            async def heal_repository(self, dry_run=True, execute=False, **kwargs):
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

            Logger.debug(
                f"[standard_heal_async] {agent_name}.{func.__name__} (dry_run={dry_run}, execute={execute})",
            )

            # Call the actual async method
            result = await func(self, *args, dry_run=dry_run, execute=execute, **remaining_kwargs)

            # Output normalization
            execution_time_ms = (time.time() - start_time) * 1000
            normalized = _normalize_heal_result(result, execution_time_ms)

            return normalized

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            Logger.error(
                f"[standard_heal_async] {agent_name}.{func.__name__} crashed: {e}\n{traceback.format_exc()}",
            )

            # In strict mode, raise HealExecutionError for proper error propagation
            if HEAL_STRICT_MODE:
                raise HealExecutionError(
                    agent_name=agent_name,
                    method_name=func.__name__,
                    message=f"Async heal operation failed: {e}",
                    original_error=e,
                ) from e

            # Legacy behavior: return error dict for backward compatibility
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


__all__ = [
    "standard_heal",
    "standard_heal_async",
    "HEAL_RESULT_SCHEMA",
]
