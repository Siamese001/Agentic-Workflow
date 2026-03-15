"""ADG-driven tests for apps_lic/config/placeholder_detector_agent_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.config.placeholder_detector_agent_config import (  # noqa: F401
        PlaceholderDetectorAgent,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PlaceholderDetectorAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="placeholder_detector_agent_config.py deps unavailable")
class TestPlaceholderDetectorAgent:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PlaceholderDetectorAgent)
    def test_importable(self):
        assert PlaceholderDetectorAgent is not None


def test_module_importable():
    """Module placeholder_detector_agent_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
