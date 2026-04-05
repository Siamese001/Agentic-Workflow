"""ADG Tracing Hooks - Automatic Runtime ADG collection for sovereign agents.

Provides automatic tracing hooks that integrate with the agent execution lifecycle
to ensure comprehensive Runtime ADG collection without manual intervention.

HOOKS:
- Agent initialization tracing
- Method execution tracing
- Agent interaction tracing
- Error and exception tracing
- Resource usage tracing

USAGE:
    from agentic_core.mixins.adg_tracing_hooks import with_adg_tracing

    @with_adg_tracing
    class MyAgent:
        def __init__(self):
            # Automatically traced
            pass

        def execute(self):
            # Automatically traced
            pass
"""

import functools
import logging
import time
from typing import Any, Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from agentic_core.mixins.integrated_tracing_mixin import (
    IntegratedTracingMixin,
)

emit_determinism_digest("adg_tracing_hooks", "adg_tracing_hooks_digest")
record_execution_trace("adg_tracing_hooks", "adg_tracing_hooks_trace")

Logger = logging.getLogger(__name__)


def with_adg_tracing(cls: type) -> type:
    """
    Class decorator to automatically add ADG tracing hooks to a class.

    This decorator automatically wraps key methods with tracing hooks
    and ensures the class inherits from IntegratedTracingMixin.

    Args:
        cls: Class to decorate

    Returns:
        Decorated class with ADG tracing hooks
    """
    # Ensure class inherits from IntegratedTracingMixin
    if not issubclass(cls, IntegratedTracingMixin):
        # Create a new class that inherits from both
        class TracedClass(cls, IntegratedTracingMixin):
            pass

        TracedClass.__name__ = cls.__name__
        TracedClass.__qualname__ = cls.__qualname__
        decorated_cls = TracedClass
    else:
        decorated_cls = cls

    # Wrap key methods with tracing hooks
    if hasattr(decorated_cls, '__init__'):
        decorated_cls.__init__ = _trace_agent_init(decorated_cls.__init__)

    if hasattr(decorated_cls, 'execute'):
        decorated_cls.execute = _trace_agent_execute(decorated_cls.execute)

    # Wrap common agent methods
    for method_name in ['run', 'process', 'handle', 'invoke']:
        if hasattr(decorated_cls, method_name):
            original_method = getattr(decorated_cls, method_name)
            wrapped_method = _trace_agent_method(original_method, method_name)
            setattr(decorated_cls, method_name, wrapped_method)

    return decorated_cls


def _trace_agent_init(func: Callable) -> Callable:
    """Decorator to trace agent initialization."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        class_name = self.__class__.__name__

        # Initialize tracing if not already done
        if hasattr(self, '_tracing_service_name'):
            service_name = self._tracing_service_name
        else:
            service_name = class_name
            if hasattr(self, '__init__'):
                # Try to initialize IntegratedTracingMixin if not already done
                try:
                    IntegratedTracingMixin.__init__(self, service_name=service_name)
                except Exception as e:
                    Logger.warning(f"[ADG_HOOKS] Failed to initialize tracing for {class_name}: {e}")

        # Trace initialization
        if hasattr(self, 'start_span'):
            with self.start_span("agent_init", {"class": class_name, "args_count": len(args), "kwargs_count": len(kwargs)}):
                try:
                    result = func(self, *args, **kwargs)
                    return result
                except Exception as e:
                    Logger.error(f"[ADG_HOOKS] Agent initialization failed for {class_name}: {e}")
                    raise
        else:
            return func(self, *args, **kwargs)

    return wrapper


def _trace_agent_execute(func: Callable) -> Callable:
    """Decorator to trace agent execute method."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        class_name = self.__class__.__name__

        # Extract mission from arguments if available
        mission = kwargs.get('mission', args[0] if args else 'unknown')

        # Trace execution with orchestrator span
        if hasattr(self, 'start_span'):
            with self.start_span("agent_execute", {
                "class": class_name,
                "mission": str(mission),
                "args_count": len(args),
                "kwargs_count": len(kwargs),
            }) as span:
                try:
                    start_time = time.time()
                    result = func(self, *args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000

                    # Add execution metadata
                    span.set_attribute("execution_duration_ms", duration_ms)
                    span.set_attribute("execution_success", True)

                    return result

                except Exception as e:
                    span.set_attribute("execution_success", False)
                    span.set_attribute("error_type", type(e).__name__)
                    span.set_attribute("error_message", str(e))
                    Logger.error(f"[ADG_HOOKS] Agent execution failed for {class_name}: {e}")
                    raise
        else:
            return func(self, *args, **kwargs)

    return wrapper


def _trace_agent_method(func: Callable, method_name: str) -> Callable:
    """Decorator to trace general agent methods."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        class_name = self.__class__.__name__

        # Trace method execution
        if hasattr(self, 'start_span'):
            with self.start_span(f"agent_{method_name}", {
                "class": class_name,
                "method": method_name,
                "args_count": len(args),
                "kwargs_count": len(kwargs),
            }) as span:
                try:
                    start_time = time.time()
                    result = func(self, *args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000

                    # Add method execution metadata
                    span.set_attribute("method_duration_ms", duration_ms)
                    span.set_attribute("method_success", True)

                    # Add result type if available
                    if result is not None:
                        span.set_attribute("result_type", type(result).__name__)

                    return result

                except Exception as e:
                    span.set_attribute("method_success", False)
                    span.set_attribute("error_type", type(e).__name__)
                    span.set_attribute("error_message", str(e))
                    Logger.error(f"[ADG_HOOKS] Agent method {method_name} failed for {class_name}: {e}")
                    raise
        else:
            return func(self, *args, **kwargs)

    return wrapper


class ADGTracingHookManager:
    """
    Manager for ADG tracing hooks with global configuration.

    Provides centralized control over tracing hook behavior and
    automatic agent discovery and tracing setup.
    """

    def __init__(self) -> None:
        self._hooked_classes: set[type] = set()
        self._global_hooks_enabled: bool = True
        self._auto_discovery_enabled: bool = True

    def enable_global_hooks(self, enabled: bool = True) -> None:
        """Enable or disable global tracing hooks."""
        self._global_hooks_enabled = enabled
        Logger.info(f"[ADG_HOOKS] Global hooks {'enabled' if enabled else 'disabled'}")

    def enable_auto_discovery(self, enabled: bool = True) -> None:
        """Enable or disable automatic agent discovery."""
        self._auto_discovery_enabled = enabled
        Logger.info(f"[ADG_HOOKS] Auto-discovery {'enabled' if enabled else 'disabled'}")

    def hook_class(self, cls: type) -> type:
        """
        Apply ADG tracing hooks to a class.

        Args:
            cls: Class to hook

        Returns:
            Hooked class
        """
        if not self._global_hooks_enabled:
            return cls

        if cls in self._hooked_classes:
            return cls  # Already hooked

        hooked_cls = with_adg_tracing(cls)
        self._hooked_classes.add(hooked_cls)

        Logger.info(f"[ADG_HOOKS] Applied tracing hooks to {cls.__name__}")
        return hooked_cls

    def hook_existing_instances(self) -> int:
        """
        Hook existing agent instances that don't have tracing.

        Returns:
            Number of instances hooked
        """
        hooked_count = 0

        # This would require instance tracking - for now, just log
        if self._auto_discovery_enabled:
            Logger.info("[ADG_HOOKS] Auto-discovery of existing instances not implemented")

        return hooked_count

    def get_hook_status(self) -> dict[str, Any]:
        """
        Get status of tracing hook manager.

        Returns:
            Dictionary with hook status
        """
        return {
            "global_hooks_enabled": self._global_hooks_enabled,
            "auto_discovery_enabled": self._auto_discovery_enabled,
            "hooked_classes_count": len(self._hooked_classes),
            "hooked_classes": [cls.__name__ for cls in self._hooked_classes],
        }


# Global hook manager instance
_hook_manager = ADGTracingHookManager()


def get_hook_manager() -> ADGTracingHookManager:
    """Get the global ADG tracing hook manager."""
    return _hook_manager


def trace_agent_method(method_name: str | None = None):
    """
    Decorator to trace a specific agent method.

    Args:
        method_name: Custom method name for tracing (defaults to actual method name)

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        trace_name = method_name or func.__name__
        return _trace_agent_method(func, trace_name)

    return decorator


def trace_cognitive_operation(reasoning_mode: str = "react"):
    """
    Decorator specifically for cognitive operations.

    Args:
        reasoning_mode: Reasoning mode for the operation

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            class_name = self.__class__.__name__

            if hasattr(self, 'start_span'):
                with self.start_span(f"cognitive_{func.__name__}", {
                    "class": class_name,
                    "operation": func.__name__,
                    "reasoning_mode": reasoning_mode,
                    "cognitive_operation": True,
                }) as span:
                    try:
                        result = func(self, *args, **kwargs)
                        span.set_attribute("cognitive_success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("cognitive_success", False)
                        span.set_attribute("error_type", type(e).__name__)
                        raise
            else:
                return func(self, *args, **kwargs)

        return wrapper

    return decorator


def trace_tool_operation(tool_name: str | None = None):
    """
    Decorator specifically for tool operations.

    Args:
        tool_name: Name of the tool (defaults to method name)

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        tool = tool_name or func.__name__

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            class_name = self.__class__.__name__

            if hasattr(self, 'start_span'):
                with self.start_span(f"tool_{tool}", {
                    "class": class_name,
                    "tool_name": tool,
                    "tool_operation": True,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                }) as span:
                    try:
                        result = func(self, *args, **kwargs)
                        span.set_attribute("tool_success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("tool_success", False)
                        span.set_attribute("error_type", type(e).__name__)
                        raise
            else:
                return func(self, *args, **kwargs)

        return wrapper

    return decorator
