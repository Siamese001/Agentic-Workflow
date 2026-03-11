"""REQ-RAGX-006: ExternalKnowledgeAccessViolation enforcement.

Production enforcement: validate_citation_custody() in rag_guardrail.py.
CitationBundle dataclass for immutable citation binding.

Positive tests: properly cited context passes.
Negative tests: missing/incomplete citations raise ExternalKnowledgeAccessViolation.
"""

from __future__ import annotations

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Positive: properly cited context passes validation
# ---------------------------------------------------------------------------


def test_no_context_passes_without_citations():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        validate_citation_custody,
    )

    validate_citation_custody([], None)  # no context -> no enforcement needed


def test_empty_context_passes_without_citations():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        validate_citation_custody,
    )

    validate_citation_custody([], [])  # empty -> no enforcement needed


def test_single_chunk_with_matching_citation_passes():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        CitationBundle,
        validate_citation_custody,
    )

    chunks = [{"chunk_id": "c1", "text": "some retrieved content"}]
    citations = [
        CitationBundle(
            chunk_id="c1",
            source_ref="docs/arch.md",
            byte_sha256="abcd1234" * 8,
            byte_range=(0, 100),
            score=0.95,
        )
    ]
    validate_citation_custody(chunks, citations)  # should not raise


def test_multiple_chunks_all_cited_passes():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        CitationBundle,
        validate_citation_custody,
    )

    chunks = [
        {"chunk_id": "c1", "text": "chunk 1"},
        {"chunk_id": "c2", "text": "chunk 2"},
        {"chunk_id": "c3", "text": "chunk 3"},
    ]
    citations = [
        CitationBundle(chunk_id="c1", source_ref="a.md", byte_sha256="a" * 64, byte_range=(0, 10), score=0.9),
        CitationBundle(chunk_id="c2", source_ref="b.md", byte_sha256="b" * 64, byte_range=(0, 20), score=0.8),
        CitationBundle(chunk_id="c3", source_ref="c.md", byte_sha256="c" * 64, byte_range=(0, 30), score=0.7),
    ]
    validate_citation_custody(chunks, citations)  # should not raise


# ---------------------------------------------------------------------------
# Negative: missing or incomplete citations raise violation
# ---------------------------------------------------------------------------


def test_context_without_citations_raises():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        ExternalKnowledgeAccessViolation,
        validate_citation_custody,
    )

    chunks = [{"chunk_id": "c1", "text": "retrieved content"}]
    with pytest.raises(ExternalKnowledgeAccessViolation, match="CITATION_MISSING"):
        validate_citation_custody(chunks, None)


def test_context_with_empty_citations_raises():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        ExternalKnowledgeAccessViolation,
        validate_citation_custody,
    )

    chunks = [{"chunk_id": "c1", "text": "retrieved content"}]
    with pytest.raises(ExternalKnowledgeAccessViolation, match="CITATION_MISSING"):
        validate_citation_custody(chunks, [])


def test_partial_citations_raises_gap():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        CitationBundle,
        ExternalKnowledgeAccessViolation,
        validate_citation_custody,
    )

    chunks = [
        {"chunk_id": "c1", "text": "chunk 1"},
        {"chunk_id": "c2", "text": "chunk 2"},
    ]
    citations = [
        CitationBundle(chunk_id="c1", source_ref="a.md", byte_sha256="a" * 64, byte_range=(0, 10), score=0.9),
    ]
    with pytest.raises(ExternalKnowledgeAccessViolation, match="CITATION_GAP.*c2"):
        validate_citation_custody(chunks, citations)


def test_chunk_missing_chunk_id_field_raises():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        CitationBundle,
        ExternalKnowledgeAccessViolation,
        validate_citation_custody,
    )

    chunks = [{"text": "no chunk_id key"}]
    citations = [
        CitationBundle(chunk_id="c1", source_ref="a.md", byte_sha256="a" * 64, byte_range=(0, 10), score=0.9),
    ]
    with pytest.raises(ExternalKnowledgeAccessViolation, match="CHUNK_ID_MISSING"):
        validate_citation_custody(chunks, citations)


# ---------------------------------------------------------------------------
# CitationBundle is frozen dataclass
# ---------------------------------------------------------------------------


def test_citation_bundle_is_frozen():
    from agentic_core.L5_safety.enforcement.rag_guardrail import CitationBundle

    cb = CitationBundle(chunk_id="c1", source_ref="a.md", byte_sha256="a" * 64, byte_range=(0, 10), score=0.9)
    with pytest.raises((AttributeError, TypeError)):
        cb.chunk_id = "mutated"  # type: ignore[misc]


def test_citation_bundle_fields():
    from agentic_core.L5_safety.enforcement.rag_guardrail import CitationBundle

    cb = CitationBundle(
        chunk_id="c1", source_ref="a.md", byte_sha256="abc123", byte_range=(0, 50), score=0.88
    )
    assert cb.chunk_id == "c1"
    assert cb.source_ref == "a.md"
    assert cb.byte_sha256 == "abc123"
    assert cb.byte_range == (0, 50)
    assert cb.score == 0.88


# ---------------------------------------------------------------------------
# ExternalKnowledgeAccessViolation is a proper exception type
# ---------------------------------------------------------------------------


def test_external_knowledge_access_violation_is_exception():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        ExternalKnowledgeAccessViolation,
    )

    assert issubclass(ExternalKnowledgeAccessViolation, Exception)


def test_external_knowledge_access_violation_carries_message():
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
        ExternalKnowledgeAccessViolation,
    )

    err = ExternalKnowledgeAccessViolation("wave aborted")
    assert "wave aborted" in str(err)
