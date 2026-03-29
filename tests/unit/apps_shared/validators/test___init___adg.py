"""ADG-driven tests for apps_shared/validators/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module validators must be importable."""
    import apps_shared.validators.__init__ as _mod  # noqa: F401

    assert _mod is not None