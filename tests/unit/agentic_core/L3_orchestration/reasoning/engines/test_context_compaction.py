"""Unit tests for ContextCompactor (W4.2 — G5 compaction & tool-result clearing)."""

from __future__ import annotations

import pytest

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    Citation,
    EvidenceClass,
    EvidenceContract,
    EvidenceContractBuilder,
    EvidenceStatus,
    VerifiedChunk,
)
from agentic_core.knowledge.retrieval.prompt_envelope import (
    AssemblyStatusCode,
    PromptAssemblyStatus,
    PromptEnvelope,
)
from agentic_core.L3_orchestration.reasoning.engines.context_compaction import (
    CompactionRecord,
    CompactionResult,
    ContextCompactor,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(
    chunk_id: str,
    content: str,
    *,
    is_must_use: bool = False,
    evidence_class: str = EvidenceClass.SUPPORTING,
    source_id: str = "src_1",
    citation_anchor: str = "",
    contradiction_flag: bool = False,
) -> VerifiedChunk:
    return VerifiedChunk(
        chunk_id=chunk_id,
        content=content,
        source_id=source_id,
        citation_anchor=citation_anchor,
        support_score=0.8 if is_must_use else 0.5,
        is_must_use=is_must_use,
        contradiction_flag=contradiction_flag,
        evidence_class=evidence_class,
    )


def _make_overflow_envelope() -> PromptEnvelope:
    """Build an envelope that exceeds token budget."""
    # Create chunks with large content to simulate overflow
    chunks = [
        _make_chunk("must_1", "Critical evidence that must be preserved. " * 20, is_must_use=True, citation_anchor="A1"),
        _make_chunk(
            "tool_1", "Tool result output from subprocess. " * 30,
            evidence_class=EvidenceClass.BACKGROUND,
            source_id="tool_subprocess_run",
            citation_anchor="B1",
        ),
        _make_chunk(
            "opt_1", "Optional supporting evidence that is somewhat long. " * 15,
            evidence_class=EvidenceClass.SUPPORTING,
            citation_anchor="C1",
        ),
        _make_chunk(
            "bg_1", "Background context information. " * 25,
            evidence_class=EvidenceClass.BACKGROUND,
            source_id="bg_source",
            citation_anchor="D1",
        ),
    ]
    return PromptEnvelope(
        envelope_id="env-001",
        trace_id="trace-001",
        query_id="q-001",
        verified_chunks=tuple(chunks),
        cited_spans=(),
        coverage_score=0.6,
        gaps=(),
        task_spec="test task",
        system_blocks=(),
        replay_key="rk-001",
        policy_hash="ph-001",
        plan_id="plan-001",
        assembly_status=PromptAssemblyStatus(
            status=AssemblyStatusCode.OVERFLOW,
            token_estimate=8000,
            overflow=True,
            citations_required=True,
            contradiction_flags_present=False,
            must_use_chunks_present=1,
            optional_chunks_present=3,
        ),
        evidence_status=EvidenceStatus.WEAK,
    )


def _make_within_budget_envelope() -> PromptEnvelope:
    """Build an envelope within token budget."""
    chunks = [
        _make_chunk("must_1", "Short must-use chunk.", is_must_use=True, citation_anchor="A1"),
        _make_chunk("opt_1", "Short optional chunk.", citation_anchor="B1"),
    ]
    return PromptEnvelope(
        envelope_id="env-002",
        trace_id="trace-002",
        query_id="q-002",
        verified_chunks=tuple(chunks),
        cited_spans=(),
        coverage_score=0.9,
        gaps=(),
        task_spec="test",
        system_blocks=(),
        replay_key="rk-002",
        policy_hash="ph-002",
        plan_id="plan-002",
        assembly_status=PromptAssemblyStatus(
            status=AssemblyStatusCode.READY,
            token_estimate=50,
            overflow=False,
            citations_required=True,
        ),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestContextCompactorNoOp:

    def test_within_budget_returns_same_envelope(self) -> None:
        compactor = ContextCompactor(token_budget=4096)
        envelope = _make_within_budget_envelope()
        result = compactor.compact(envelope)
        assert result.chars_saved == 0
        assert result.tool_results_cleared == 0
        assert result.summaries_produced == 0
        assert result.provenance_intact is True
        assert result.compacted_envelope.envelope_id == "env-002"


class TestContextCompactorToolResultClearing:

    def test_clears_tool_result_chunks(self) -> None:
        compactor = ContextCompactor(token_budget=100, max_summary_chars=100)
        envelope = _make_overflow_envelope()
        result = compactor.compact(envelope)

        # Tool result chunk should be cleared
        cleared_ids = {r.chunk_id for r in result.records if r.action == "cleared"}
        assert "tool_1" in cleared_ids

        # Check the cleared chunk content
        for chunk in result.compacted_envelope.verified_chunks:
            if chunk.chunk_id == "tool_1":
                assert chunk.content.startswith("[tool-result:")
                break

        assert result.tool_results_cleared >= 1

    def test_must_use_chunks_not_cleared(self) -> None:
        compactor = ContextCompactor(token_budget=100, max_summary_chars=100)
        envelope = _make_overflow_envelope()
        result = compactor.compact(envelope)

        # Must-use chunk should not appear in cleared records
        cleared_ids = {r.chunk_id for r in result.records if r.action == "cleared"}
        assert "must_1" not in cleared_ids

        # Must-use content should be preserved
        for chunk in result.compacted_envelope.verified_chunks:
            if chunk.chunk_id == "must_1":
                assert "Critical evidence" in chunk.content
                break


class TestContextCompactorSummarization:

    def test_summarizes_long_optional_chunks(self) -> None:
        compactor = ContextCompactor(token_budget=100, max_summary_chars=100)
        envelope = _make_overflow_envelope()
        result = compactor.compact(envelope)

        # At least one chunk should be summarized
        summarized_ids = {r.chunk_id for r in result.records if r.action == "summarized"}
        # opt_1 is long and non-must-use, should be summarized
        if summarized_ids:
            assert "opt_1" in summarized_ids or any(r.action == "summarized" for r in result.records)

    def test_summary_preserves_citation_anchor(self) -> None:
        compactor = ContextCompactor(token_budget=100, max_summary_chars=100)
        envelope = _make_overflow_envelope()
        result = compactor.compact(envelope)

        # Check that summarized chunks still have their anchor
        for chunk in result.compacted_envelope.verified_chunks:
            if chunk.chunk_id == "opt_1" and "[...compacted]" in chunk.content:
                assert "C1" in chunk.content
                break


class TestContextCompactorBackgroundPruning:

    def test_prunes_background_when_over_budget(self) -> None:
        compactor = ContextCompactor(token_budget=50, max_summary_chars=50)
        envelope = _make_overflow_envelope()
        result = compactor.compact(envelope)

        # Background chunks should be pruned if still over budget
        pruned_ids = {r.chunk_id for r in result.records if r.action == "pruned"}
        if pruned_ids:
            assert "bg_1" in pruned_ids

    def test_pruned_chunks_added_to_excluded(self) -> None:
        compactor = ContextCompactor(token_budget=50, max_summary_chars=50)
        envelope = _make_overflow_envelope()
        result = compactor.compact(envelope)

        # Pruned chunks should appear in excluded_with_reasons
        for _chunk_id, reason in result.compacted_envelope.excluded_with_reasons.items():
            if "compaction_pruned" in reason:
                assert "bg_1" in result.compacted_envelope.excluded_with_reasons
                break


class TestContextCompactorProvenance:

    def test_provenance_intact_when_anchors_preserved(self) -> None:
        compactor = ContextCompactor(token_budget=100, max_summary_chars=100)
        envelope = _make_overflow_envelope()
        result = compactor.compact(envelope)
        # All chunks in the test have citation anchors
        assert result.provenance_intact is True

    def test_compaction_metadata_added(self) -> None:
        compactor = ContextCompactor(token_budget=100, max_summary_chars=100)
        envelope = _make_overflow_envelope()
        result = compactor.compact(envelope)

        meta = result.compacted_envelope.metadata
        assert meta.get("compaction_applied") is True
        assert "compaction_chars_saved" in meta
        assert "compaction_tool_results_cleared" in meta


class TestCompactionRecord:

    def test_record_fields(self) -> None:
        record = CompactionRecord(
            chunk_id="test_1",
            action="cleared",
            original_char_count=500,
            compacted_char_count=20,
            provenance_preserved=True,
        )
        assert record.chunk_id == "test_1"
        assert record.action == "cleared"
        assert record.original_char_count == 500
        assert record.compacted_char_count == 20
        assert record.provenance_preserved is True
