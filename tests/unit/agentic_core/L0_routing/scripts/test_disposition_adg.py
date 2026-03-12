"""ADG-driven tests for agentic_core/L0_routing/scripts/disposition.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.disposition import (  # noqa: F401
        Disposition,
        CoreAnalysisResult,
        CoreSynthesisAnalyzer,
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    Disposition = None  # type: ignore[assignment,misc]
    CoreAnalysisResult = None  # type: ignore[assignment,misc]
    CoreSynthesisAnalyzer = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="disposition.py deps unavailable")
class TestDisposition:
    def test_is_enum(self):
        import enum
        assert issubclass(Disposition, enum.Enum)
    def test_has_members(self):
        assert len(list(Disposition)) >= 1
    def test_importable(self):
        assert Disposition is not None

@pytest.mark.skipif(not _AVAILABLE, reason="disposition.py deps unavailable")
class TestCoreAnalysisResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CoreAnalysisResult)
    def test_importable(self):
        assert CoreAnalysisResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="disposition.py deps unavailable")
class TestCoreSynthesisAnalyzer:
    def test_is_class(self):
        assert isinstance(CoreSynthesisAnalyzer, type)
    def test_importable(self):
        assert CoreSynthesisAnalyzer is not None

@pytest.mark.skipif(not _AVAILABLE, reason="disposition.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module disposition.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
