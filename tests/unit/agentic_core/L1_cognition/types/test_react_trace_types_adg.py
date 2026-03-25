"""ADG importability contract for agentic_core/L1_cognition/types/react_trace_types.py."""
from __future__ import annotations

import agentic_core.L1_cognition.types.react_trace_types  # noqa: F401


def test_module_importable():
    """Module react_trace_types must be importable."""
    assert agentic_core.L1_cognition.types.react_trace_types is not None
