"""ADG importability contract for agentic_core/L2_execution/enforcement/key_source.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.key_source  # noqa: F401


def test_module_importable():
    """Module key_source must be importable."""
    assert agentic_core.L2_execution.enforcement.key_source is not None
