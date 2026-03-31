"""ADG-driven tests for apps_lic/reasoning/OutreachProactiveAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module OutreachProactiveAgent must be importable."""
    import apps_lic.reasoning.OutreachProactiveAgent  # noqa: F401

    assert apps_lic.reasoning.OutreachProactiveAgent is not None
