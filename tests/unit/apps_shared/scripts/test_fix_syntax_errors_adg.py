"""ADG-driven tests for apps_shared/scripts/fix_syntax_errors.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module fix_syntax_errors must be importable."""
    import apps_shared.scripts.fix_syntax_errors  # noqa: F401

    assert apps_shared.scripts.fix_syntax_errors is not None
