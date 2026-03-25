"""ADG-driven tests for agentic_core/utils/workflow_engines/sealed_interface_check_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.sealed_interface_check_enforcer as _mod  # noqa: F401


def test_module_importable():
    """Module sealed_interface_check_enforcer must be importable."""
    assert _mod is not None
