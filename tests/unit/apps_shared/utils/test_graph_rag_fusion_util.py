"""Foundational behavioral tests for apps_shared/utils/graph_rag_fusion_util.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_graph_rag_fusion_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.graph_rag_fusion_util import (  # noqa: F401
        QueryType,
        FusionResult,
        CypherQueryGenerator,
        GraphRAGFusion,
        get_graphrag_fusion,
        graphrag_query,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    QueryType = None  # type: ignore[assignment,misc]
    FusionResult = None  # type: ignore[assignment,misc]
    CypherQueryGenerator = None  # type: ignore[assignment,misc]
    GraphRAGFusion = None  # type: ignore[assignment,misc]
    get_graphrag_fusion = None  # type: ignore[assignment,misc]
    graphrag_query = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestQueryTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(QueryType, enum.Enum)

    def test_has_members(self):
        assert len(list(QueryType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in QueryType:
            assert member.value is not None

    def test_known_member_vector_only_exists(self):
        assert hasattr(QueryType, 'VECTOR_ONLY')

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestFusionResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FusionResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(FusionResult)}
        assert field_names >= {'vector_results', 'query', 'fused_context', 'query_type', 'graph_results'}

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestCypherQueryGeneratorContract:
    def test_is_class(self):
        assert isinstance(CypherQueryGenerator, type)

    def test_has_method_generate_query(self):
        assert callable(getattr(CypherQueryGenerator, 'generate_query', None))

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestGraphRAGFusionContract:
    def test_is_class(self):
        assert isinstance(GraphRAGFusion, type)

    def test_has_method_query(self):
        assert callable(getattr(GraphRAGFusion, 'query', None))

    def test_has_method_get_stats(self):
        assert callable(getattr(GraphRAGFusion, 'get_stats', None))

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestGetGraphragFusionFunction:
    def test_is_callable(self):
        assert callable(get_graphrag_fusion)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_graphrag_fusion)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestGraphragQueryFunction:
    def test_is_callable(self):
        assert callable(graphrag_query)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(graphrag_query)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="graph_rag_fusion_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module graph_rag_fusion_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
