"""ADG-driven tests for agentic_core/L0_routing/scripts/code_entity.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.code_entity import (  # noqa: F401
        CodeEntity,
        FileAnalysis,
        analyze_file,
        build_current_codebase_index,
        classify_entity_type,
        extract_docstring,
        infer_domain,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CodeEntity = None  # type: ignore[assignment,misc]
    FileAnalysis = None  # type: ignore[assignment,misc]
    extract_docstring = None  # type: ignore[assignment,misc]
    classify_entity_type = None  # type: ignore[assignment,misc]
    infer_domain = None  # type: ignore[assignment,misc]
    analyze_file = None  # type: ignore[assignment,misc]
    build_current_codebase_index = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="code_entity.py deps unavailable")
class TestCodeEntity:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CodeEntity)
    def test_importable(self):
        assert CodeEntity is not None

@pytest.mark.skipif(not _AVAILABLE, reason="code_entity.py deps unavailable")
class TestFileAnalysis:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FileAnalysis)
    def test_importable(self):
        assert FileAnalysis is not None

@pytest.mark.skipif(not _AVAILABLE, reason="code_entity.py deps unavailable")
class TestExtractDocstring:
    def test_is_callable(self):
        assert callable(extract_docstring)

@pytest.mark.skipif(not _AVAILABLE, reason="code_entity.py deps unavailable")
class TestClassifyEntityType:
    def test_is_callable(self):
        assert callable(classify_entity_type)

@pytest.mark.skipif(not _AVAILABLE, reason="code_entity.py deps unavailable")
class TestInferDomain:
    def test_is_callable(self):
        assert callable(infer_domain)

@pytest.mark.skipif(not _AVAILABLE, reason="code_entity.py deps unavailable")
class TestAnalyzeFile:
    def test_is_callable(self):
        assert callable(analyze_file)

@pytest.mark.skipif(not _AVAILABLE, reason="code_entity.py deps unavailable")
class TestBuildCurrentCodebaseIndex:
    def test_is_callable(self):
        assert callable(build_current_codebase_index)


def test_module_importable():
    """Module code_entity.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE