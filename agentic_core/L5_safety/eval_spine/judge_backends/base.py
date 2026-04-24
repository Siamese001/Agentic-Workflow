"""Base types and helpers for judge backends.

A judge backend is a callable compatible with the existing
``DimScorer`` type alias in :mod:`trace_grader`. Expressing the contract
here (rather than duplicating) keeps backends and the grader in lockstep.
"""

from __future__ import annotations

from agentic_core.L5_safety.eval_spine.trace_grader import DimScorer

# Public re-export under a stable name. ``JudgeBackend`` is the name the
# rest of the codebase will reference; ``DimScorer`` remains the grader's
# internal type alias.
JudgeBackend = DimScorer


def backend_name(backend: JudgeBackend) -> str:
    """Return a short, stable identifier for a backend (for telemetry)."""
    if backend is None:
        return "<none>"
    cls = type(backend)
    # Callable classes report their class name; plain functions report
    # ``<module>.<qualname>``.
    if cls.__name__ == "function":
        module = getattr(backend, "__module__", "?")
        qualname = getattr(backend, "__qualname__", getattr(backend, "__name__", "?"))
        return f"{module}.{qualname}"
    return cls.__name__


__all__ = ["JudgeBackend", "backend_name"]
