"""ADG-driven tests for L1_cognition/engines/domain_manager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.engines.domain_manager  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.engines.domain_manager  # noqa: F401
    """Module domain_manager must be importable."""
    assert agentic_core.L1_cognition.engines.domain_manager is not None
