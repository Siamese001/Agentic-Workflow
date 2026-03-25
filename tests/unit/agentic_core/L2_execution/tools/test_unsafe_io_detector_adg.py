"""ADG importability contract for agentic_core/L2_execution/tools/unsafe_io_detector.py."""
from __future__ import annotations

import agentic_core.L2_execution.tools.unsafe_io_detector  # noqa: F401


def test_module_importable():
    """Module unsafe_io_detector must be importable."""
    assert agentic_core.L2_execution.tools.unsafe_io_detector is not None
