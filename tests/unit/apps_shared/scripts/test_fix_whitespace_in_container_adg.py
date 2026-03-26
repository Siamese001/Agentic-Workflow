"""ADG-driven tests for apps_shared/scripts/fix_whitespace_in_container.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fix_whitespace_in_container must be importable."""
    import apps_shared.scripts.fix_whitespace_in_container  # noqa: F401

    assert apps_shared.scripts.fix_whitespace_in_container is not None