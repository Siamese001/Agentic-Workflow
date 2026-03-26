"""ADG-driven tests for agentic_core/L3_orchestration/engines/sovereign_mcp_router.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.engines.sovereign_mcp_router  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.engines.sovereign_mcp_router  # noqa: F401
    """Module sovereign_mcp_router must be importable."""
    assert agentic_core.L3_orchestration.engines.sovereign_mcp_router is not None
