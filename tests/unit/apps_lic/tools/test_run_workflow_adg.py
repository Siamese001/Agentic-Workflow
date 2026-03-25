"""ADG-driven tests for apps_lic/tools/run_workflow.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.run_workflow  # noqa: F401


def test_module_importable():
    """Module run_workflow must be importable."""
    assert apps_lic.tools.run_workflow is not None
