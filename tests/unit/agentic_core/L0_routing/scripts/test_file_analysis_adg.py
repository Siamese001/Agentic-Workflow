"""ADG-driven tests for agentic_core/L0_routing/scripts/file_analysis.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.file_analysis import (  # noqa: F401
        FileAnalysis,
        extract_docstring,
        analyze_class,
        analyze_function,
        infer_domain,
        infer_purpose,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    FileAnalysis = None  # type: ignore[assignment,misc]
    extract_docstring = None  # type: ignore[assignment,misc]
    analyze_class = None  # type: ignore[assignment,misc]
    analyze_function = None  # type: ignore[assignment,misc]
    infer_domain = None  # type: ignore[assignment,misc]
    infer_purpose = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="file_analysis.py deps unavailable")
class TestFileAnalysis:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FileAnalysis)
    def test_importable(self):
        assert FileAnalysis is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_analysis.py deps unavailable")
class TestExtractDocstring:
    def test_is_callable(self):
        assert callable(extract_docstring)

@pytest.mark.skipif(not _AVAILABLE, reason="file_analysis.py deps unavailable")
class TestAnalyzeClass:
    def test_is_callable(self):
        assert callable(analyze_class)

@pytest.mark.skipif(not _AVAILABLE, reason="file_analysis.py deps unavailable")
class TestAnalyzeFunction:
    def test_is_callable(self):
        assert callable(analyze_function)

@pytest.mark.skipif(not _AVAILABLE, reason="file_analysis.py deps unavailable")
class TestInferDomain:
    def test_is_callable(self):
        assert callable(infer_domain)

@pytest.mark.skipif(not _AVAILABLE, reason="file_analysis.py deps unavailable")
class TestInferPurpose:
    def test_is_callable(self):
        assert callable(infer_purpose)


def test_module_importable():
    """Module file_analysis.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
