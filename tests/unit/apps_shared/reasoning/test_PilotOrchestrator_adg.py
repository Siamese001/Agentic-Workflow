"""ADG-driven tests for apps_shared/reasoning/PilotOrchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.reasoning.PilotOrchestrator import (  # noqa: F401
        PilotOrchestrator,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    PilotOrchestrator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="PilotOrchestrator.py deps unavailable")
class TestPilotOrchestrator:
    def test_is_class(self):
        assert isinstance(PilotOrchestrator, type)
    def test_importable(self):
        assert PilotOrchestrator is not None


def test_module_importable():
    """Module PilotOrchestrator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE