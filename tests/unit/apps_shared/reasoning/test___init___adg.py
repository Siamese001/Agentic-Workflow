"""ADG-driven tests for apps_shared/reasoning/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.reasoning.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module reasoning must be importable."""
    assert _mod is not None
