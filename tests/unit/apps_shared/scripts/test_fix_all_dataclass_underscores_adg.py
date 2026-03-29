"""ADG-driven tests for apps_shared/scripts/fix_all_dataclass_underscores.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module fix_all_dataclass_underscores must be importable."""
    import apps_shared.scripts.fix_all_dataclass_underscores  # noqa: F401

    assert apps_shared.scripts.fix_all_dataclass_underscores is not None