"""ADG importability contract for agentic_core/runtime/types/circuit_breaker_types.py."""
from __future__ import annotations

import agentic_core.runtime.types.circuit_breaker_types  # noqa: F401


def test_module_importable():
    """Module circuit_breaker_types must be importable."""
    assert agentic_core.runtime.types.circuit_breaker_types is not None
