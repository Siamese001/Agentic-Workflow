"""ADG-driven tests for apps_shared/reasoning/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module reasoning must be importable."""
    import apps_shared.reasoning.__init__ as _mod  # noqa: F401

    assert _mod is not None