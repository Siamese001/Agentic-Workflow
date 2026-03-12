"""ADG-driven tests for L1_cognition/config/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    import agentic_core.L1_cognition.config
    assert agentic_core.L1_cognition.config is not None


def test_is_package():
    import agentic_core.L1_cognition.config
    assert hasattr(agentic_core.L1_cognition.config, "__path__")
