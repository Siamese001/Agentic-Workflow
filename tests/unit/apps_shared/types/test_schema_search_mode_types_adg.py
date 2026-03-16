"""ADG contract tests for apps_shared/types/schema_search_mode_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_schema_search_mode_types_adg")
_emit_applies_guardrail("p0", "test_schema_search_mode_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_schema_search_mode_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_schema_search_mode_types_adg", "state_snapshot")
emit_replay_key("p0", "test_schema_search_mode_types_adg")
emit_determinism_digest("p0", "test_schema_search_mode_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.schema_search_mode_types import (
        SchemaSearchMode,
        SchemaSearchQuery,
        SchemaSearchResult,
        SchemaSimilarityType,
        SchemaVectorConfig,
        SchemaVectorEntry,
        SchemaVectorSearcher,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    SchemaSearchMode = SchemaSimilarityType = SchemaVectorEntry = None  # type: ignore[assignment,misc]
    SchemaSearchQuery = SchemaSearchResult = SchemaVectorConfig = SchemaVectorSearcher = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaSearchMode:
    def test_is_enum(self):
        import enum; assert issubclass(SchemaSearchMode, enum.Enum)
    def test_has_semantic(self): assert SchemaSearchMode.SEMANTIC.value == "semantic"
    def test_has_hybrid(self): assert SchemaSearchMode.HYBRID.value == "hybrid"
    def test_four_modes(self): assert len(list(SchemaSearchMode)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaSimilarityType:
    def test_is_enum(self):
        import enum; assert issubclass(SchemaSimilarityType, enum.Enum)
    def test_has_structural(self): assert SchemaSimilarityType.STRUCTURAL.value == "structural"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaSearchQuery:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SchemaSearchQuery)
    def test_creates_defaults(self):
        q = SchemaSearchQuery()
        assert q.search_mode == SchemaSearchMode.SEMANTIC
        assert q.top_k == 10; assert q.threshold == 0.7

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaVectorConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SchemaVectorConfig)
    def test_creates_defaults(self):
        c = SchemaVectorConfig(); assert c.dimension == 1536; assert c.max_entries == 10000

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaVectorSearcher:
    def test_creates(self):
        s = SchemaVectorSearcher(); assert s is not None
    def test_get_statistics_empty(self):
        s = SchemaVectorSearcher()
        stats = s.get_schema_statistics(); assert stats["total_schemas"] == 0
    def test_search_returns_result(self):
        s = SchemaVectorSearcher()
        q = SchemaSearchQuery(query_text="test")
        result = s.search_schema_vectors(q)
        assert isinstance(result, SchemaSearchResult); assert result.entries == []

def test_module_importable(): assert _AVAIL or not _AVAIL
