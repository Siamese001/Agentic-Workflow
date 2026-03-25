"""ADG importability contract for agentic_core/L2_execution/enforcement/preventative_sandbox.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.preventative_sandbox  # noqa: F401


def test_module_importable():
    """Module preventative_sandbox must be importable."""
    assert agentic_core.L2_execution.enforcement.preventative_sandbox is not None
