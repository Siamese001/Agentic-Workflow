"""W2 / G8: per-lane C0.2 evidence trace carries retrieval observability fields.

Plan: apps-rg-e2e-gap-remediation-7e2d9c (W2 PR 2 — instrumentation, no behavior change).

The trace now records raw dense hit count, applied `where` filter, post-filter survivor count,
similarity threshold, and embedding model id + dimension so the before/after C0.2 traces required
by the W2 merge gate are observable. Additive + defaulted = backward compatible.

Pure product-mode unit test: no APPS_RG_TEST_HARNESS, no Chroma, no provider.
"""

from __future__ import annotations

from apps_rg.runtime.bindings.c0_binding import _build_section_evidence_trace
from apps_rg.runtime.bindings.c0_evidence_trace_map import SectionEvidenceTrace

_G8_FIELDS = (
    "raw_dense_hit_count",
    "post_filter_survivor_count",
    "applied_where_filter",
    "similarity_threshold",
    "embedding_model_id",
    "embedding_dimension",
)


def test_trace_dataclass_g8_defaults_backward_compatible() -> None:
    """Old callers that omit the G8 fields still construct a valid trace."""
    trace = SectionEvidenceTrace(section_id="competencies")
    assert trace.raw_dense_hit_count == 0
    assert trace.post_filter_survivor_count == 0
    assert trace.applied_where_filter == ""
    assert trace.similarity_threshold == 0.0
    assert trace.embedding_model_id == ""
    assert trace.embedding_dimension == 0


def test_build_section_evidence_trace_plumbs_g8_fields() -> None:
    trace = _build_section_evidence_trace(
        {"section_id": "competencies", "section_type": "skills"},
        "query text",
        [],
        {"resume_payload": {}, "jd_payload": {}},
        timestamp_iso="2026-06-08T00:00:00Z",
        raw_dense_hit_count=7,
        post_filter_survivor_count=3,
        applied_where_filter='{"app": "apps_rg"}',
        similarity_threshold=0.42,
        embedding_model_id="BAAI/bge-m3",
        embedding_dimension=1024,
    )
    assert trace.section_id == "competencies"
    assert trace.raw_dense_hit_count == 7
    assert trace.post_filter_survivor_count == 3
    assert trace.applied_where_filter == '{"app": "apps_rg"}'
    assert trace.similarity_threshold == 0.42
    assert trace.embedding_model_id == "BAAI/bge-m3"
    assert trace.embedding_dimension == 1024


def test_post_filter_survivor_count_defaults_to_item_count() -> None:
    """When the caller omits post_filter_survivor_count, it falls back to len(items)."""
    trace = _build_section_evidence_trace(
        {"section_id": "headline"},
        "q",
        [],  # zero items -> zero survivors
        {},
        timestamp_iso="2026-06-08T00:00:00Z",
        raw_dense_hit_count=4,
    )
    assert trace.raw_dense_hit_count == 4
    assert trace.post_filter_survivor_count == 0


def test_trace_omitting_g8_fields_uses_neutral_values() -> None:
    """A caller that passes none of the G8 kwargs gets neutral, non-misleading values."""
    trace = _build_section_evidence_trace(
        {"section_id": "headline"},
        "q",
        [],
        {},
        timestamp_iso="2026-06-08T00:00:00Z",
    )
    for field in _G8_FIELDS:
        assert hasattr(trace, field)
    assert trace.applied_where_filter == ""
    assert trace.embedding_dimension == 0
