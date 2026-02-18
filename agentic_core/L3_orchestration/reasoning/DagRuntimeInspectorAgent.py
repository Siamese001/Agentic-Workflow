"""CONSOLIDATED: DagRuntimeInspectorAgent → InspectorExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""


def _get_DagRuntimeInspectorAgent():
    """Lazy load InspectorExecutor to avoid upward import."""
    from agentic_core.L5_safety.reasoning.InspectorExecutor import InspectorExecutor

    return InspectorExecutor


# For backward compatibility, provide a lazy accessor
DagRuntimeInspectorAgent = None  # Will be set on first access


def __getattr__(name):
    """Module-level lazy loading for backward compatibility."""
    global DagRuntimeInspectorAgent
    if name == "DagRuntimeInspectorAgent":
        if DagRuntimeInspectorAgent is None:
            DagRuntimeInspectorAgent = _get_DagRuntimeInspectorAgent()
        return DagRuntimeInspectorAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["DagRuntimeInspectorAgent"]
