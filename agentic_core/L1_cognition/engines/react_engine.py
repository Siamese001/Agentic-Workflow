"""ReAct Engine — canonical location in L1_cognition/engines/.

Re-exports ReActEngine, ReActTrace, ReActStep, and create_react_engine from
the existing implementation in react_config.py so callers can import from
the correct layer path:

    from agentic_core.L1_cognition.engines.react_engine import ReActEngine

The original react_config.py is kept intact (no deletion) to avoid breaking
any existing imports.
"""

from __future__ import annotations

from agentic_core.L1_cognition.config.react_config import (  # noqa: F401
    ReActEngine,
    ReActStep,
    ReActTrace,
    ReasoningMode,
    create_react_engine,
)

__all__ = [
    "ReActEngine",
    "ReActStep",
    "ReActTrace",
    "ReasoningMode",
    "create_react_engine",
]
