"""ADG-driven tests for apps_lic/reasoning/HOP9IntegrationAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module HOP9IntegrationAgent must be importable."""
    import apps_lic.reasoning.HOP9IntegrationAgent  # noqa: F401

    assert apps_lic.reasoning.HOP9IntegrationAgent is not None
