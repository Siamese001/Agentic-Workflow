"""ADG-driven tests for apps_lic/reasoning/HOP9IntegrationAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.reasoning.HOP9IntegrationAgent  # noqa: F401


def test_module_importable():
    """Module HOP9IntegrationAgent must be importable."""
    assert apps_lic.reasoning.HOP9IntegrationAgent is not None
