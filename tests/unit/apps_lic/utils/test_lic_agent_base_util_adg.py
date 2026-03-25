"""ADG-driven tests for apps_lic/utils/lic_agent_base_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.utils.lic_agent_base_util  # noqa: F401


def test_module_importable():
    """Module lic_agent_base_util must be importable."""
    assert apps_lic.utils.lic_agent_base_util is not None
