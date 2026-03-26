"""Foundational behavioral tests for agentic_core/L0_routing/utils/ssot_discovery_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L0_routing.utils.ssot_discovery_util  # noqa: F401


def test_module_importable():
    import agentic_core.L0_routing.utils.ssot_discovery_util  # noqa: F401
    """Module ssot_discovery_util must be importable."""
    assert agentic_core.L0_routing.utils.ssot_discovery_util is not None
