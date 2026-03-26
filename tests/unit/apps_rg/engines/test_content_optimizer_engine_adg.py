"""ADG-driven tests for apps_rg/engines/content_optimizer_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module content_optimizer_engine must be importable."""
    import apps_rg.engines.content_optimizer_engine  # noqa: F401

    assert apps_rg.engines.content_optimizer_engine is not None
