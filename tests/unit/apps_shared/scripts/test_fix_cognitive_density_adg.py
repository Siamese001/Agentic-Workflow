"""ADG-driven tests for apps_shared/scripts/fix_cognitive_density.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module fix_cognitive_density must be importable."""
    import apps_shared.scripts.fix_cognitive_density  # noqa: F401

    assert apps_shared.scripts.fix_cognitive_density is not None
