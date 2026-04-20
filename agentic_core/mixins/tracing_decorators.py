"""Tracing Decorators — Wave 1: Trace Semantics and IDs.

Provides @trace_cognitive, @trace_action, @trace_tool, @trace_orchestrator
decorators for automatic span creation on agent methods.

Design:
- Decorators automatically detect self/cls with tracing capabilities
- Automatic attribute extraction from method arguments
- Layer-appropriate span kinds (cognitive, action, tool, orchestrator)
- Graceful degradation when tracing unavailable
- Preserves function signatures and docstrings

Usage:
    class MyAgent(SovereignBaseAgent):
        @trace_cognitive(reasoning_mode="react")
        def analyze(self, query: str) -> dict:
            # Creates cognitive span with query as attribute
            return {"result": analysis}

        @trace_tool(tool_name="search")
        def search_data(self, query: str) -> list:
            # Creates tool span with query and result count
            return results
"""

from __future__ import annotations

import functools
import inspect
import logging
import time
from typing import Any, Callable, TypeVar

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)
from tqdm import tqdm

# Bootstrap ADG edge emission
emit_replay_key("tracing_decorators", "L6")
emit_determinism_digest("tracing_decorators", "tracing_decorators_digest")

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def _get_tracing_instance(args: tuple[Any, ...]) -> Any | None:
    """Extract instance with tracing capabilities from args."""
    if not args:
        return None
    instance = args[0]
    # Check for start_span method (indicates tracing capability)
    if hasattr(instance, "start_span") and callable(instance.start_span):
        return instance
    return None


def _extract_attributes(
    sig: inspect.Signature,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    extra_attrs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract attributes from function arguments."""
    bound = sig.bind_partial(*args, **kwargs)
    bound.apply_defaults()

    attributes: dict[str, Any] = {}

    # Add bound arguments (excluding self/cls)
    for name, value in tqdm(bound.arguments.items(), desc="Processing", unit="item"):
        if name in ("self", "cls"):
            continue
        # Convert to string representation for tracing
        try:
            if isinstance(value, (str, int, float, bool)):
                attributes[name] = value
            elif isinstance(value, (list, tuple)):
                attributes[f"{name}_count"] = len(value)
            elif isinstance(value, dict):
                attributes[f"{name}_keys"] = list(value.keys())[:10]  # Limit keys
        except (TypeError, ValueError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            # Skip values that can't be serialized
            import logging

            logging.getLogger(__name__).debug("tracing_decorators: Exception swallowed at L85: %s", e)

    if extra_attrs:
        attributes.update(extra_attrs)

    return attributes


def _make_operation_name(func: Callable[..., Any], suffix: str = "") -> str:
    """Generate operation name from function."""
    module = getattr(func, "__module__", "unknown")
    name = getattr(func, "__name__", "unknown")
    if suffix:
        return f"{module}.{name}.{suffix}"
    return f"{module}.{name}"


def trace_cognitive(
    reasoning_mode: str = "react",
    layer: str = "L1",
    extra_attrs: dict[str, Any] | None = None,
) -> Callable[[F], F]:
    """Decorator for cognitive/reasoning operations.

    Creates a cognitive span with reasoning_mode attribute.

    Args:
        reasoning_mode: Type of reasoning (react, cot, reflection, etc.)
        layer: Architecture layer (default L1)
        extra_attrs: Additional attributes to attach to span

    Usage:
        @trace_cognitive(reasoning_mode="chain_of_thought")
        def analyze_document(self, doc: str) -> dict:
            # Span created automatically
            return analysis_result
    """

    def decorator(func: F) -> F:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = _get_tracing_instance(args)

            if instance is None:
                # No tracing available, just run function
                return func(*args, **kwargs)

            operation_name = _make_operation_name(func)
            attributes = _extract_attributes(sig, args, kwargs, extra_attrs)
            attributes["reasoning_mode"] = reasoning_mode
            attributes["layer"] = layer
            attributes["span_kind"] = "cognitive"

            _emit_records_execution_trace(
                operation_name,
                str(getattr(LayerSegment, layer, "L1_COGNITION")),
                func.__name__,
            )

            try:
                with instance.start_span(operation_name, attributes) as span:
                    result = func(*args, **kwargs)
                    # Add result info to span
                    if isinstance(result, dict):
                        span.set_attribute("result_keys", list(result.keys()))
                    return result
            except (AttributeError, RuntimeError, TypeError) as e:
                logger.debug("Tracing error in %s: %s", operation_name, e)
                # Fallback: run without tracing
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def trace_action(
    action_name: str | None = None,
    layer: str = "L2",
    extra_attrs: dict[str, Any] | None = None,
) -> Callable[[F], F]:
    """Decorator for action/execution operations.

    Creates an action span for tool executions and side effects.

    Args:
        action_name: Name of the action (defaults to function name)
        layer: Architecture layer (default L2)
        extra_attrs: Additional attributes to attach to span

    Usage:
        @trace_action(action_name="file_write")
        def save_output(self, data: dict, path: str) -> bool:
            # Span tracks file write operation
            return success
    """

    def decorator(func: F) -> F:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = _get_tracing_instance(args)

            if instance is None:
                return func(*args, **kwargs)

            operation_name = action_name or _make_operation_name(func)
            attributes = _extract_attributes(sig, args, kwargs, extra_attrs)
            attributes["layer"] = layer
            attributes["span_kind"] = "action"

            _emit_records_execution_trace(
                operation_name,
                str(getattr(LayerSegment, layer, "L2_EXECUTION")),
                func.__name__,
            )

            try:
                with instance.start_span(operation_name, attributes) as span:
                    start_time = time.monotonic()
                    result = func(*args, **kwargs)
                    duration_ms = (time.monotonic() - start_time) * 1000
                    span.set_attribute("duration_ms", duration_ms)
                    return result
            except (AttributeError, RuntimeError, TypeError) as e:
                logger.debug("Tracing error in %s: %s", operation_name, e)
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def trace_tool(
    tool_name: str | None = None,
    layer: str = "L2",
    extra_attrs: dict[str, Any] | None = None,
) -> Callable[[F], F]:
    """Decorator for tool invocations.

    Creates a tool span for external tool/API calls.

    Args:
        tool_name: Name of the tool (defaults to function name)
        layer: Architecture layer (default L2)
        extra_attrs: Additional attributes to attach to span

    Usage:
        @trace_tool(tool_name="pinecone_query")
        def query_vectors(self, query: str, top_k: int = 5) -> list:
            # Span tracks vector search operation
            return matches
    """

    def decorator(func: F) -> F:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = _get_tracing_instance(args)

            if instance is None:
                return func(*args, **kwargs)

            operation_name = f"tool.{tool_name or func.__name__}"
            attributes = _extract_attributes(sig, args, kwargs, extra_attrs)
            attributes["tool_name"] = tool_name or func.__name__
            attributes["layer"] = layer
            attributes["span_kind"] = "tool"

            _emit_records_execution_trace(
                operation_name,
                str(getattr(LayerSegment, layer, "L2_EXECUTION")),
                func.__name__,
            )

            try:
                with instance.start_span(operation_name, attributes) as span:
                    start_time = time.monotonic()
                    result = func(*args, **kwargs)
                    duration_ms = (time.monotonic() - start_time) * 1000

                    # Record tool metrics
                    span.set_attribute("duration_ms", duration_ms)
                    if isinstance(result, list):
                        span.set_attribute("result_count", len(result))
                    elif isinstance(result, dict):
                        span.set_attribute("result_keys", list(result.keys()))

                    return result
            except (AttributeError, RuntimeError, TypeError) as e:
                logger.debug("Tracing error in %s: %s", operation_name, e)
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def trace_orchestrator(
    orchestrator_name: str | None = None,
    layer: str = "L3",
    extra_attrs: dict[str, Any] | None = None,
) -> Callable[[F], F]:
    """Decorator for orchestration operations.

    Creates an orchestrator span for workflow coordination.

    Args:
        orchestrator_name: Name of the orchestrator (defaults to function name)
        layer: Architecture layer (default L3)
        extra_attrs: Additional attributes to attach to span

    Usage:
        @trace_orchestrator(orchestrator_name="campaign_workflow")
        def run_campaign(self, config: dict) -> dict:
            # Span tracks full campaign orchestration
            return results
    """

    def decorator(func: F) -> F:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = _get_tracing_instance(args)

            if instance is None:
                return func(*args, **kwargs)

            operation_name = orchestrator_name or _make_operation_name(func)
            attributes = _extract_attributes(sig, args, kwargs, extra_attrs)
            attributes["orchestrator_name"] = orchestrator_name or func.__name__
            attributes["layer"] = layer
            attributes["span_kind"] = "orchestrator"

            _emit_records_execution_trace(
                operation_name,
                str(getattr(LayerSegment, layer, "L3_ORCHESTRATION")),
                func.__name__,
            )

            try:
                with instance.start_span(operation_name, attributes) as span:
                    start_time = time.monotonic()
                    result = func(*args, **kwargs)
                    duration_ms = (time.monotonic() - start_time) * 1000

                    span.set_attribute("duration_ms", duration_ms)
                    if isinstance(result, dict):
                        if "status" in result:
                            span.set_attribute("result_status", result["status"])
                        if "agent_count" in result:
                            span.set_attribute("agent_count", result["agent_count"])

                    return result
            except (AttributeError, RuntimeError, TypeError) as e:
                logger.debug("Tracing error in %s: %s", operation_name, e)
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def trace_router(
    router_name: str | None = None,
    layer: str = "L0",
    extra_attrs: dict[str, Any] | None = None,
) -> Callable[[F], F]:
    """Decorator for routing operations.

    Creates a router span for L0 routing decisions.

    Args:
        router_name: Name of the router (defaults to function name)
        layer: Architecture layer (default L0)
        extra_attrs: Additional attributes to attach to span

    Usage:
        @trace_router(router_name="intent_classifier")
        def classify_intent(self, query: str) -> str:
            # Span tracks routing decision
            return intent
    """

    def decorator(func: F) -> F:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = _get_tracing_instance(args)

            if instance is None:
                return func(*args, **kwargs)

            operation_name = router_name or _make_operation_name(func)
            attributes = _extract_attributes(sig, args, kwargs, extra_attrs)
            attributes["router_name"] = router_name or func.__name__
            attributes["layer"] = layer
            attributes["span_kind"] = "router"

            _emit_records_execution_trace(
                operation_name,
                str(getattr(LayerSegment, layer, "L0_ROUTING")),
                func.__name__,
            )

            try:
                with instance.start_span(operation_name, attributes) as span:
                    result = func(*args, **kwargs)
                    span.set_attribute("destination", str(result) if result else "unknown")
                    return result
            except (AttributeError, RuntimeError, TypeError) as e:
                logger.debug("Tracing error in %s: %s", operation_name, e)
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


# Convenience aliases for common patterns
trace_reasoning = trace_cognitive
trace_execution = trace_action

__all__ = [
    "trace_cognitive",
    "trace_reasoning",
    "trace_action",
    "trace_execution",
    "trace_tool",
    "trace_orchestrator",
    "trace_router",
]
