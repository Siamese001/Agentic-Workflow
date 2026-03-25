"""ADG-driven tests for apps_lic/reasoning/OutreachLearningAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.OutreachLearningAgent  # noqa: F401


def test_module_importable():
    """Module OutreachLearningAgent must be importable."""
    assert apps_lic.reasoning.OutreachLearningAgent is not None
