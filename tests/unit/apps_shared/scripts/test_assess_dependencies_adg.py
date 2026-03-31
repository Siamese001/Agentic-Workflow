"""ADG-driven tests for apps_shared/scripts/assess_dependencies.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module assess_dependencies must be importable."""
    import apps_shared.scripts.assess_dependencies  # noqa: F401

    assert apps_shared.scripts.assess_dependencies is not None
