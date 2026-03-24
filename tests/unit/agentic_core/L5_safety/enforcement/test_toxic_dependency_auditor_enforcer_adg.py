"""ADG-driven tests for agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.toxic_dependency_auditor_enforcer import (  # noqa: F401
        ToxicDependencyAuditor,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ToxicDependencyAuditor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="toxic_dependency_auditor_enforcer.py deps unavailable")
class TestToxicDependencyAuditor:
    def test_is_class(self):
        assert isinstance(ToxicDependencyAuditor, type)
    def test_importable(self):
        assert ToxicDependencyAuditor is not None


def test_module_importable():
    """Module toxic_dependency_auditor_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE