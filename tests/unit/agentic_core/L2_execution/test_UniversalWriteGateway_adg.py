"""ADG importability contract for agentic_core/L2_execution/UniversalWriteGateway.py."""
from __future__ import annotations

import agentic_core.L2_execution.UniversalWriteGateway  # noqa: F401


def test_module_importable():
    """Module UniversalWriteGateway must be importable."""
    assert agentic_core.L2_execution.UniversalWriteGateway is not None
