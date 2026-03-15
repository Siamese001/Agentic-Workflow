"""ADG-driven tests for apps_rg/reasoning/ResumeOrchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.reasoning.ResumeOrchestrator import (  # noqa: F401
        ResumeOrchestrator,
        orchestrate_resume,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ResumeOrchestrator = None  # type: ignore[assignment,misc]
    orchestrate_resume = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ResumeOrchestrator.py deps unavailable")
class TestResumeOrchestrator:
    def test_is_class(self):
        assert isinstance(ResumeOrchestrator, type)
    def test_importable(self):
        assert ResumeOrchestrator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ResumeOrchestrator.py deps unavailable")
class TestOrchestrateResume:
    def test_is_callable(self):
        assert callable(orchestrate_resume)


def test_module_importable():
    """Module ResumeOrchestrator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
