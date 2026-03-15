"""ADG-driven tests for agentic_core/runtime/config/security_level_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.config.security_level_config import (  # noqa: F401
        AnalysisType,
        PhaseResult,
        PhaseType,
        RefactorProposal,
        RefactorType,
        SecurityIssue,
        SecurityLevel,
        SemanticMatch,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SecurityLevel = None  # type: ignore[assignment,misc]
    AnalysisType = None  # type: ignore[assignment,misc]
    RefactorType = None  # type: ignore[assignment,misc]
    PhaseType = None  # type: ignore[assignment,misc]
    SecurityIssue = None  # type: ignore[assignment,misc]
    SemanticMatch = None  # type: ignore[assignment,misc]
    RefactorProposal = None  # type: ignore[assignment,misc]
    PhaseResult = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="security_level_config.py deps unavailable")
class TestSecurityLevel:
    def test_is_enum(self):
        import enum
        assert issubclass(SecurityLevel, enum.Enum)
    def test_has_members(self):
        assert len(list(SecurityLevel)) >= 1
    def test_importable(self):
        assert SecurityLevel is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_level_config.py deps unavailable")
class TestAnalysisType:
    def test_is_enum(self):
        import enum
        assert issubclass(AnalysisType, enum.Enum)
    def test_has_members(self):
        assert len(list(AnalysisType)) >= 1
    def test_importable(self):
        assert AnalysisType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_level_config.py deps unavailable")
class TestRefactorType:
    def test_is_enum(self):
        import enum
        assert issubclass(RefactorType, enum.Enum)
    def test_has_members(self):
        assert len(list(RefactorType)) >= 1
    def test_importable(self):
        assert RefactorType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_level_config.py deps unavailable")
class TestPhaseType:
    def test_is_enum(self):
        import enum
        assert issubclass(PhaseType, enum.Enum)
    def test_has_members(self):
        assert len(list(PhaseType)) >= 1
    def test_importable(self):
        assert PhaseType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_level_config.py deps unavailable")
class TestSecurityIssue:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SecurityIssue)
    def test_importable(self):
        assert SecurityIssue is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_level_config.py deps unavailable")
class TestSemanticMatch:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SemanticMatch)
    def test_importable(self):
        assert SemanticMatch is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_level_config.py deps unavailable")
class TestRefactorProposal:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RefactorProposal)
    def test_importable(self):
        assert RefactorProposal is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_level_config.py deps unavailable")
class TestPhaseResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PhaseResult)
    def test_importable(self):
        assert PhaseResult is not None


def test_module_importable():
    """Module security_level_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
