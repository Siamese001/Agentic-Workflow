"""ADG-driven tests for L2_execution/audit/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    import agentic_core.L2_execution.audit
    assert agentic_core.L2_execution.audit is not None


def test_is_package():
    import agentic_core.L2_execution.audit
    assert hasattr(agentic_core.L2_execution.audit, "__path__")
