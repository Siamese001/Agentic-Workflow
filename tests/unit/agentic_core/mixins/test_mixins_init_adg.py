"""ADG-driven tests for agentic_core/mixins/__init__.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    import agentic_core.mixins
    import agentic_core.mixins
#  # MOVED: import agentic_core.mixins
    assert agentic_core.mixins is not None


def test_is_package():
#  # MOVED: import agentic_core.mixins
    assert hasattr(agentic_core.mixins, "__path__")
