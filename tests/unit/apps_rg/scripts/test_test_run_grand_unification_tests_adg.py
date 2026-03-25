"""ADG-driven tests for apps_rg/scripts/test_run_grand_unification_tests.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.scripts.test_run_grand_unification_tests  # noqa: F401


def test_module_importable():
    """Module test_run_grand_unification_tests must be importable."""
    assert apps_rg.scripts.test_run_grand_unification_tests is not None
