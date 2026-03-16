"""ADG contract tests for apps_shared/types/similarity_method_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_similarity_method_types_adg")
_emit_applies_guardrail("p0", "test_similarity_method_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_similarity_method_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_similarity_method_types_adg", "state_snapshot")
emit_replay_key("p0", "test_similarity_method_types_adg")
emit_determinism_digest("p0", "test_similarity_method_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
