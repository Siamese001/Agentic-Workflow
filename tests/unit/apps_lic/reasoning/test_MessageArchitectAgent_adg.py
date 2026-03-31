"""ADG-driven tests for apps_lic/reasoning/MessageArchitectAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module MessageArchitectAgent must be importable."""
    import apps_lic.reasoning.MessageArchitectAgent as _mod  # noqa: F401

    assert _mod is not None
