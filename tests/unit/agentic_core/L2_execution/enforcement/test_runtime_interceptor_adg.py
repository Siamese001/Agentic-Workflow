"""ADG importability contract for agentic_core/L2_execution/enforcement/runtime_interceptor.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.runtime_interceptor  # noqa: F401


def test_module_importable():
    """Module runtime_interceptor must be importable."""
    assert agentic_core.L2_execution.enforcement.runtime_interceptor is not None
