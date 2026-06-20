"""Auto-wrap concrete engine `execute` methods with `seal_step()`.

Plan: `.codex/plans/runtime-adg-tier3-broader-adoption-8f2d1c.md`

This module exposes one primitive, `install_seal_step_autowrap(cls)`, that
base engine classes call from `__init_subclass__`. Whenever a concrete
subclass defines `execute`, the method is replaced with a wrapper that
emits an `L2.step.seal` span around the original call via the ambient
runtime-ADG adapter.

Design rules
------------
1. Fail-open: when no adapter is active (unit tests, CLI runs), the
   wrapped method behaves identically to the original.
2. Supports both synchronous and `async def execute` via runtime
   detection with `inspect.iscoroutinefunction`.
3. Idempotent: wrapping twice is a no-op (flag attribute guards it).
4. Zero per-subclass edits — one call in the base class's
   `__init_subclass__` covers every concrete subclass forever.
"""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable


_WRAPPED_ATTR = "__seal_step_wrapped__"


def _build_step_id(cls: type, method_name: str) -> str:
    """Stable identifier for this step across runs of the same subclass."""
    return f"{cls.__module__}.{cls.__name__}.{method_name}"


def _wrap_sync(fn: Callable, cls: type, method_name: str) -> Callable:
    engine_label = cls.__name__
    step_id = _build_step_id(cls, method_name)

    @functools.wraps(fn)
    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        # Lazy import: avoid circular imports at class-definition time.
        from agentic_core.L6_system_learning.runtime_span_emitter import (  # noqa: PLC0415
            get_current_adapter,
            seal_step,
        )

        adapter = get_current_adapter()
        with seal_step(
            adapter,
            step_id=step_id,
            trace_id="",
            component=engine_label,
        ) as bag:
            result = fn(self, *args, **kwargs)
            bag["output"] = result
        return result

    setattr(wrapper, _WRAPPED_ATTR, True)
    return wrapper


def _wrap_async(fn: Callable, cls: type, method_name: str) -> Callable:
    engine_label = cls.__name__
    step_id = _build_step_id(cls, method_name)

    @functools.wraps(fn)
    async def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        from agentic_core.L6_system_learning.runtime_span_emitter import (  # noqa: PLC0415
            get_current_adapter,
            seal_step,
        )

        adapter = get_current_adapter()
        with seal_step(
            adapter,
            step_id=step_id,
            trace_id="",
            component=engine_label,
        ) as bag:
            result = await fn(self, *args, **kwargs)
            bag["output"] = result
        return result

    setattr(wrapper, _WRAPPED_ATTR, True)
    return wrapper


def install_seal_step_autowrap(cls: type, method_name: str = "execute") -> None:
    """Wrap `cls.<method_name>` with seal_step if it is a concrete method.

    Called from a base class's `__init_subclass__`:

        class BaseXxxEngine(ABC):
            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                install_seal_step_autowrap(cls)

    Safe to call on abstract classes, classes that don't define the method
    at all, or classes already wrapped — all become no-ops.
    """
    if method_name not in cls.__dict__:
        return  # subclass didn't override; nothing to wrap here
    fn = cls.__dict__[method_name]
    if not callable(fn):
        return
    if getattr(fn, _WRAPPED_ATTR, False):
        return  # already wrapped
    if getattr(fn, "__isabstractmethod__", False):
        return  # abstract declaration in an intermediate class

    if inspect.iscoroutinefunction(fn):
        wrapped = _wrap_async(fn, cls, method_name)
    else:
        wrapped = _wrap_sync(fn, cls, method_name)

    setattr(cls, method_name, wrapped)


__all__ = ["install_seal_step_autowrap"]
