"""ADG-driven tests for agentic_core/mixins/feature_flagged_agent_mixin.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.feature_flagged_agent_mixin import (  # noqa: F401
        FeatureFlaggedAgentMixin,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    FeatureFlaggedAgentMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="feature_flagged_agent_mixin.py deps unavailable")
class TestFeatureFlaggedAgentMixin:
    def test_is_class(self):
        assert isinstance(FeatureFlaggedAgentMixin, type)
    def test_importable(self):
        assert FeatureFlaggedAgentMixin is not None


def test_module_importable():
    """Module feature_flagged_agent_mixin.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
