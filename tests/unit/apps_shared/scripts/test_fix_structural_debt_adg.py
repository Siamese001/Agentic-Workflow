"""ADG-driven tests for apps_shared/scripts/fix_structural_debt.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.fix_structural_debt  # noqa: F401


def test_module_importable():
    """Module fix_structural_debt must be importable."""
    assert apps_shared.scripts.fix_structural_debt is not None
