"""ADG-driven tests for apps_lic/reasoning/OutreachSignalRouterAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module OutreachSignalRouterAgent must be importable."""
    import apps_lic.reasoning.OutreachSignalRouterAgent  # noqa: F401

    assert apps_lic.reasoning.OutreachSignalRouterAgent is not None
