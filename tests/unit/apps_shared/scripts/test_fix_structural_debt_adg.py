"""ADG-driven tests for apps_shared/scripts/fix_structural_debt.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fix_structural_debt must be importable."""
    import apps_shared.scripts.fix_structural_debt  # noqa: F401

    assert apps_shared.scripts.fix_structural_debt is not None
