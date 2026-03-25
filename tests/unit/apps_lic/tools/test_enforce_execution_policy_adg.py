"""ADG-driven tests for apps_lic/tools/enforce_execution_policy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.enforce_execution_policy  # noqa: F401


def test_module_importable():
    """Module enforce_execution_policy must be importable."""
    assert apps_lic.tools.enforce_execution_policy is not None
