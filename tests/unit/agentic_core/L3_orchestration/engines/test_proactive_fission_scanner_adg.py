"""ADG-driven tests for agentic_core/L3_orchestration/engines/proactive_fission_scanner.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.engines.proactive_fission_scanner  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.engines.proactive_fission_scanner  # noqa: F401
    """Module proactive_fission_scanner must be importable."""
    assert agentic_core.L3_orchestration.engines.proactive_fission_scanner is not None
