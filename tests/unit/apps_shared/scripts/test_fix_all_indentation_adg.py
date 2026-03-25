"""ADG-driven tests for apps_shared/scripts/fix_all_indentation.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.fix_all_indentation  # noqa: F401


def test_module_importable():
    """Module fix_all_indentation must be importable."""
    assert apps_shared.scripts.fix_all_indentation is not None
