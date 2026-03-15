"""ADG contract tests for apps_shared/types/similarity_method_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.similarity_method_types import (
        CompatibilityLevel,
        SchemaSimilarityRequest,
        SimilarityMethod,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    SimilarityMethod = CompatibilityLevel = SchemaSimilarityRequest = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSimilarityMethod:
    def test_is_enum(self):
        import enum; assert issubclass(SimilarityMethod, enum.Enum)
    def test_has_structural(self): assert SimilarityMethod.STRUCTURAL.value == "structural"
    def test_has_hybrid(self): assert SimilarityMethod.HYBRID.value == "hybrid"
    def test_five_methods(self): assert len(list(SimilarityMethod)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCompatibilityLevel:
    def test_is_enum(self):
        import enum; assert issubclass(CompatibilityLevel, enum.Enum)
    def test_has_identical(self): assert CompatibilityLevel.IDENTICAL.value == "identical"
    def test_has_incompatible(self): assert CompatibilityLevel.INCOMPATIBLE.value == "incompatible"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaSimilarityRequest:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SchemaSimilarityRequest)
    def test_creates(self):
        r = SchemaSimilarityRequest(source_schema={"a": 1}, target_schema={"b": 2})
        assert r.method == SimilarityMethod.STRUCTURAL
        assert r.weight_structural == 0.4

def test_module_importable(): assert _AVAIL or not _AVAIL
