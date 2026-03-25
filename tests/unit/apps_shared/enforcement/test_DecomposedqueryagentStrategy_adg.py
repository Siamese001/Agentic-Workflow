"""ADG-driven tests for apps_shared/enforcement/DecomposedqueryagentStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.enforcement.DecomposedqueryagentStrategy  # noqa: F401


def test_module_importable():
    """Module DecomposedqueryagentStrategy must be importable."""
    assert apps_shared.enforcement.DecomposedqueryagentStrategy is not None
