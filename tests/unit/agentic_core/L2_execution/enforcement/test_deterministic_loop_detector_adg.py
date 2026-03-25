"""ADG importability contract for agentic_core/L2_execution/enforcement/deterministic_loop_detector.py."""
from __future__ import annotations

import agentic_core.L2_execution.enforcement.deterministic_loop_detector  # noqa: F401


def test_module_importable():
    """Module deterministic_loop_detector must be importable."""
    assert agentic_core.L2_execution.enforcement.deterministic_loop_detector is not None
