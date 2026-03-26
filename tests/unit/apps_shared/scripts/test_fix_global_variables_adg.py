"""ADG-driven tests for apps_shared/scripts/fix_global_variables.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fix_global_variables must be importable."""
    import apps_shared.scripts.fix_global_variables  # noqa: F401

    assert apps_shared.scripts.fix_global_variables is not None