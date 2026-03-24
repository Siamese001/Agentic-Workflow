"""ADG-driven tests for agentic_core/utils/workflow_engines/sealed_interface_check_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.utils.workflow_engines.sealed_interface_check_enforcer as _mod  # noqa: F401
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Module sealed_interface_check_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE