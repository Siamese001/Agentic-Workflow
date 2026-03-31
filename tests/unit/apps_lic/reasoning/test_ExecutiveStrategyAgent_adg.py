"""ADG-driven tests for apps_lic/reasoning/ExecutiveStrategyAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module ExecutiveStrategyAgent must be importable."""
    import apps_lic.reasoning.ExecutiveStrategyAgent  # noqa: F401

    assert apps_lic.reasoning.ExecutiveStrategyAgent is not None
