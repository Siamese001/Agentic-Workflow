"""
Tests: Phase 3 — Chunking Governance

Branch coverage:
- FixedTokenChunkPolicy: invalid size, empty doc, exact boundary, multi-chunk
- OverlapWindowChunkPolicy: invalid args, overlap >= chunk_size, step calculation
- SectionAwareChunkPolicy: no sections, single section, multi-section
- SemanticChunkPolicy: empty, single sentence, multi-sentence grouping
- MaxChunkSizeValidator: all under, boundary exact, some over
- MinChunkSizeValidator: all over, boundary, some under
- OverlapSanityValidator: no violations, consecutive duplicate
- DuplicateChunkDetector: no dups, single dup, all same
- OrphanChunkDetector: no orphans, empty content, whitespace only
- ChunkManifestValidator: clean manifest, manifest with all violation types
- ChunkQualityReport.is_valid: valid/invalid paths
"""

import pytest

from agentic_core.evaluation.chunking.policies import (
    Chunk,
    ChunkManifest,
    FixedTokenChunkPolicy,
    OverlapWindowChunkPolicy,
    SectionAwareChunkPolicy,
    SemanticChunkPolicy,
    _approx_token_count,
)
from agentic_core.evaluation.chunking.validators import (
    ChunkManifestValidator,
    ChunkQualityReport,
    DuplicateChunkDetector,
    MaxChunkSizeValidator,
    MinChunkSizeValidator,
    OrphanChunkDetector,
    OverlapSanityValidator,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_eval_chunking", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_eval_chunking", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_eval_chunking", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_eval_chunking", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_eval_chunking", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_eval_chunking", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_eval_chunking", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_eval_chunking", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_eval_chunking", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_eval_chunking", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_eval_chunking", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_eval_chunking", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_eval_chunking", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_eval_chunking", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_eval_chunking", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_eval_chunking", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_eval_chunking", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_eval_chunking", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_eval_chunking", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_eval_chunking", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_eval_chunking", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_eval_chunking", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_eval_chunking", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_eval_chunking", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_eval_chunking", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_eval_chunking", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_eval_chunking", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_eval_chunking", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_eval_chunking")
# REMOVED: _emit_applies_guardrail("p0", "test_eval_chunking", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_eval_chunking", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_eval_chunking", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_eval_chunking", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_eval_chunking", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_eval_chunking", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_eval_chunking", "write_through")
# REMOVED: _emit_writes_through("p1", "test_eval_chunking", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_eval_chunking", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_eval_chunking", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_eval_chunking", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_eval_chunking", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_eval_chunking", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_eval_chunking", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_eval_chunking", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_eval_chunking", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_eval_chunking", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_eval_chunking", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_eval_chunking", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_eval_chunking", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_eval_chunking", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_eval_chunking", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_eval_chunking")
# REMOVED: _emit_gated_by_confidence("p1", "test_eval_chunking", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_eval_chunking")
# REMOVED: emit_determinism_digest("p0", "test_eval_chunking")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_eval_chunking", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_eval_chunking", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_eval_chunking", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_eval_chunking", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_eval_chunking", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_eval_chunking", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_eval_chunking", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_eval_chunking", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_eval_chunking", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_eval_chunking", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_eval_chunking", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_eval_chunking", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_eval_chunking", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_eval_chunking", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_eval_chunking", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_eval_chunking", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_eval_chunking", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_eval_chunking", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_eval_chunking", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_eval_chunking", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_chunk(chunk_id, content, token_count=None, doc_id="doc_0"):
    return Chunk(
        chunk_id=chunk_id,
        doc_id=doc_id,
        content=content,
        token_count=token_count or _approx_token_count(content),
        start_char=0,
        end_char=len(content),
    )


def _make_manifest(chunks, policy="fixed_token"):
    return ChunkManifest(doc_id="doc_0", policy_name=policy, chunks=chunks)


# ---------------------------------------------------------------------------
# _approx_token_count
# ---------------------------------------------------------------------------


class TestApproxTokenCount:
    def test_empty_string(self):
        assert _approx_token_count("") == 0

    def test_single_word(self):
        assert _approx_token_count("hello") == 1

    def test_multiple_words(self):
        assert _approx_token_count("hello world foo bar") == 4


# ---------------------------------------------------------------------------
# FixedTokenChunkPolicy
# ---------------------------------------------------------------------------


class TestFixedTokenChunkPolicy:
    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            FixedTokenChunkPolicy(chunk_size=0)
        with pytest.raises(ValueError):
            FixedTokenChunkPolicy(chunk_size=-1)

    def test_name(self):
        assert FixedTokenChunkPolicy().name == "fixed_token"

    def test_empty_document_returns_empty(self):
        chunks = FixedTokenChunkPolicy().chunk("", doc_id="d")
        assert chunks == []

    def test_single_chunk_when_doc_fits(self):
        doc = "word " * 10
        chunks = FixedTokenChunkPolicy(chunk_size=20).chunk(doc, doc_id="d")
        assert len(chunks) == 1

    def test_multiple_chunks_for_long_doc(self):
        words = " ".join(f"word{i}" for i in range(100))
        chunks = FixedTokenChunkPolicy(chunk_size=10).chunk(words, doc_id="d")
        assert len(chunks) == 10

    def test_chunk_ids_are_unique(self):
        doc = " ".join(f"w{i}" for i in range(30))
        chunks = FixedTokenChunkPolicy(chunk_size=10).chunk(doc, doc_id="doc_x")
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_token_counts_sum_to_total(self):
        doc = " ".join(f"w{i}" for i in range(25))
        chunks = FixedTokenChunkPolicy(chunk_size=10).chunk(doc, doc_id="d")
        total = sum(c.token_count for c in chunks)
        assert total == 25

    def test_last_chunk_may_be_shorter(self):
        doc = " ".join(f"w{i}" for i in range(15))
        chunks = FixedTokenChunkPolicy(chunk_size=10).chunk(doc, doc_id="d")
        assert chunks[-1].token_count == 5

    def test_policy_metadata_in_chunk(self):
        doc = "hello world foo"
        chunks = FixedTokenChunkPolicy(chunk_size=5).chunk(doc, doc_id="d")
        assert chunks[0].metadata["policy"] == "fixed_token"

    def test_deterministic(self):
        doc = " ".join(f"token{i}" for i in range(50))
        c1 = [c.content for c in FixedTokenChunkPolicy(chunk_size=10).chunk(doc, doc_id="d")]
        c2 = [c.content for c in FixedTokenChunkPolicy(chunk_size=10).chunk(doc, doc_id="d")]
        assert c1 == c2


# ---------------------------------------------------------------------------
# OverlapWindowChunkPolicy
# ---------------------------------------------------------------------------


class TestOverlapWindowChunkPolicy:
    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            OverlapWindowChunkPolicy(chunk_size=0)

    def test_negative_overlap_raises(self):
        with pytest.raises(ValueError):
            OverlapWindowChunkPolicy(chunk_size=10, overlap=-1)

    def test_overlap_ge_chunk_size_raises(self):
        with pytest.raises(ValueError):
            OverlapWindowChunkPolicy(chunk_size=10, overlap=10)
        with pytest.raises(ValueError):
            OverlapWindowChunkPolicy(chunk_size=10, overlap=15)

    def test_name(self):
        assert OverlapWindowChunkPolicy().name == "overlap_window"

    def test_zero_overlap_behaves_like_fixed(self):
        doc = " ".join(f"w{i}" for i in range(20))
        chunks_overlap = OverlapWindowChunkPolicy(chunk_size=10, overlap=0).chunk(doc, "d")
        chunks_fixed = FixedTokenChunkPolicy(chunk_size=10).chunk(doc, "d")
        assert len(chunks_overlap) == len(chunks_fixed)

    def test_overlap_produces_more_chunks(self):
        doc = " ".join(f"w{i}" for i in range(20))
        chunks_no_overlap = OverlapWindowChunkPolicy(chunk_size=10, overlap=0).chunk(doc, "d")
        chunks_with_overlap = OverlapWindowChunkPolicy(chunk_size=10, overlap=5).chunk(doc, "d")
        assert len(chunks_with_overlap) > len(chunks_no_overlap)

    def test_consecutive_chunks_share_tokens(self):
        doc = " ".join(f"word{i}" for i in range(20))
        chunks = OverlapWindowChunkPolicy(chunk_size=10, overlap=3).chunk(doc, "d")
        if len(chunks) >= 2:
            # Last 3 tokens of chunk[0] should appear in chunk[1]
            tokens0 = chunks[0].content.split()[-3:]
            tokens1 = chunks[1].content.split()[:3]
            assert tokens0 == tokens1

    def test_empty_document_returns_empty(self):
        assert OverlapWindowChunkPolicy().chunk("", "d") == []


# ---------------------------------------------------------------------------
# SectionAwareChunkPolicy
# ---------------------------------------------------------------------------


class TestSectionAwareChunkPolicy:
    def test_name(self):
        assert SectionAwareChunkPolicy().name == "section_aware"

    def test_no_headers_single_chunk(self):
        doc = "This is a plain document with no headers at all."
        chunks = SectionAwareChunkPolicy().chunk(doc, "d")
        assert len(chunks) == 1
        assert chunks[0].content.strip() == doc.strip()

    def test_two_sections(self):
        doc = "## Section One\nContent of section one.\n## Section Two\nContent of section two."
        chunks = SectionAwareChunkPolicy().chunk(doc, "d")
        assert len(chunks) >= 2

    def test_empty_sections_skipped(self):
        doc = "## \n## Real Section\nActual content here."
        chunks = SectionAwareChunkPolicy().chunk(doc, "d")
        contents = [c.content for c in chunks]
        assert any("Actual content" in c for c in contents)

    def test_chunk_ids_unique(self):
        doc = "## A\nContent A.\n## B\nContent B.\n## C\nContent C."
        chunks = SectionAwareChunkPolicy().chunk(doc, "d")
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_parent_section_populated(self):
        doc = "## Introduction\nThis is the intro."
        chunks = SectionAwareChunkPolicy().chunk(doc, "d")
        assert any(c.parent_section for c in chunks)


# ---------------------------------------------------------------------------
# SemanticChunkPolicy
# ---------------------------------------------------------------------------


class TestSemanticChunkPolicy:
    def test_name(self):
        assert SemanticChunkPolicy().name == "semantic"

    def test_invalid_target_size_raises(self):
        with pytest.raises(ValueError):
            SemanticChunkPolicy(target_size=0)

    def test_empty_document_returns_empty(self):
        assert SemanticChunkPolicy().chunk("", "d") == []

    def test_single_sentence(self):
        chunks = SemanticChunkPolicy(target_size=50).chunk("This is a single sentence.", "d")
        assert len(chunks) == 1

    def test_multiple_sentences_grouped(self):
        sentences = " ".join([f"Sentence number {i} ends here." for i in range(20)])
        chunks = SemanticChunkPolicy(target_size=5).chunk(sentences, "d")
        assert len(chunks) > 1

    def test_chunk_ids_unique(self):
        doc = " ".join([f"Sentence {i} is here." for i in range(10)])
        chunks = SemanticChunkPolicy(target_size=3).chunk(doc, "d")
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_deterministic(self):
        doc = " ".join([f"Word{i} sentence ends." for i in range(15)])
        c1 = [c.content for c in SemanticChunkPolicy(target_size=5).chunk(doc, "d")]
        c2 = [c.content for c in SemanticChunkPolicy(target_size=5).chunk(doc, "d")]
        assert c1 == c2


# ---------------------------------------------------------------------------
# MaxChunkSizeValidator
# ---------------------------------------------------------------------------


class TestMaxChunkSizeValidator:
    def test_invalid_max_raises(self):
        with pytest.raises(ValueError):
            MaxChunkSizeValidator(max_tokens=0)

    def test_all_under_limit_returns_empty(self):
        chunks = [_make_chunk(f"c_{i}", "word " * 10) for i in range(3)]
        v = MaxChunkSizeValidator(max_tokens=20)
        assert v.validate(chunks) == []

    def test_exact_boundary_not_flagged(self):
        chunk = _make_chunk("c_0", "word " * 10)
        assert chunk.token_count == 10
        v = MaxChunkSizeValidator(max_tokens=10)
        assert v.validate([chunk]) == []

    def test_boundary_plus_one_flagged(self):
        chunk = _make_chunk("c_0", "word " * 11)
        v = MaxChunkSizeValidator(max_tokens=10)
        assert "c_0" in v.validate([chunk])

    def test_multiple_violations(self):
        chunks = [_make_chunk(f"c_{i}", "word " * (i + 1)) for i in range(5)]
        v = MaxChunkSizeValidator(max_tokens=3)
        violating = v.validate(chunks)
        assert len(violating) == 2  # c_3 (4 tokens) and c_4 (5 tokens)


# ---------------------------------------------------------------------------
# MinChunkSizeValidator
# ---------------------------------------------------------------------------


class TestMinChunkSizeValidator:
    def test_invalid_min_raises(self):
        with pytest.raises(ValueError):
            MinChunkSizeValidator(min_tokens=-1)

    def test_all_over_limit_returns_empty(self):
        chunks = [_make_chunk(f"c_{i}", "word " * 20) for i in range(3)]
        assert MinChunkSizeValidator(min_tokens=5).validate(chunks) == []

    def test_exact_boundary_not_flagged(self):
        chunk = _make_chunk("c_0", "word " * 5)
        assert MinChunkSizeValidator(min_tokens=5).validate([chunk]) == []

    def test_boundary_minus_one_flagged(self):
        chunk = _make_chunk("c_0", "word " * 4)
        assert "c_0" in MinChunkSizeValidator(min_tokens=5).validate([chunk])

    def test_zero_min_never_flags(self):
        chunk = _make_chunk("c_0", "")
        assert MinChunkSizeValidator(min_tokens=0).validate([chunk]) == []


# ---------------------------------------------------------------------------
# OverlapSanityValidator
# ---------------------------------------------------------------------------


class TestOverlapSanityValidator:
    def test_no_violations_empty(self):
        assert OverlapSanityValidator().validate([]) == 0

    def test_no_violations_distinct_chunks(self):
        chunks = [_make_chunk(f"c_{i}", f"unique content for chunk {i}") for i in range(3)]
        assert OverlapSanityValidator().validate(chunks) == 0

    def test_consecutive_identical_detected(self):
        chunks = [
            _make_chunk("c_0", "same content here"),
            _make_chunk("c_1", "same content here"),
            _make_chunk("c_2", "different content"),
        ]
        assert OverlapSanityValidator().validate(chunks) == 1

    def test_all_identical_counts_n_minus_1(self):
        chunks = [_make_chunk(f"c_{i}", "identical") for i in range(4)]
        assert OverlapSanityValidator().validate(chunks) == 3


# ---------------------------------------------------------------------------
# DuplicateChunkDetector
# ---------------------------------------------------------------------------


class TestDuplicateChunkDetector:
    def test_no_duplicates(self):
        chunks = [_make_chunk(f"c_{i}", f"unique content {i}") for i in range(3)]
        assert DuplicateChunkDetector().detect(chunks) == []

    def test_exact_duplicate_detected(self):
        chunks = [
            _make_chunk("c_0", "some content here"),
            _make_chunk("c_1", "other content"),
            _make_chunk("c_2", "some content here"),
        ]
        dups = DuplicateChunkDetector().detect(chunks)
        assert "c_2" in dups
        assert "c_0" not in dups  # first occurrence not flagged

    def test_case_insensitive(self):
        chunks = [
            _make_chunk("c_0", "Hello World"),
            _make_chunk("c_1", "hello world"),
        ]
        dups = DuplicateChunkDetector().detect(chunks)
        assert "c_1" in dups

    def test_whitespace_normalised(self):
        chunks = [
            _make_chunk("c_0", "  hello world  "),
            _make_chunk("c_1", "hello world"),
        ]
        dups = DuplicateChunkDetector().detect(chunks)
        assert "c_1" in dups

    def test_all_same_flags_all_but_first(self):
        chunks = [_make_chunk(f"c_{i}", "same") for i in range(4)]
        dups = DuplicateChunkDetector().detect(chunks)
        assert len(dups) == 3
        assert "c_0" not in dups


# ---------------------------------------------------------------------------
# OrphanChunkDetector
# ---------------------------------------------------------------------------


class TestOrphanChunkDetector:
    def test_no_orphans(self):
        chunks = [_make_chunk(f"c_{i}", f"content {i}") for i in range(3)]
        assert OrphanChunkDetector().detect(chunks) == []

    def test_empty_content_is_orphan(self):
        chunks = [_make_chunk("c_0", ""), _make_chunk("c_1", "real content")]
        orphans = OrphanChunkDetector().detect(chunks)
        assert "c_0" in orphans
        assert "c_1" not in orphans

    def test_whitespace_only_is_orphan(self):
        chunks = [_make_chunk("c_0", "   \n\t  ")]
        assert "c_0" in OrphanChunkDetector().detect(chunks)

    def test_all_orphans(self):
        chunks = [_make_chunk(f"c_{i}", "") for i in range(3)]
        assert len(OrphanChunkDetector().detect(chunks)) == 3


# ---------------------------------------------------------------------------
# ChunkManifestValidator
# ---------------------------------------------------------------------------


class TestChunkManifestValidator:
    def test_valid_manifest_is_valid(self):
        chunks = [_make_chunk(f"c_{i}", f"unique content token_{i} word") for i in range(3)]
        manifest = _make_manifest(chunks)
        report = ChunkManifestValidator(max_chunk_tokens=50, min_chunk_tokens=1).validate(manifest)
        assert report.is_valid

    def test_oversized_chunk_detected(self):
        chunks = [_make_chunk("c_0", " ".join(f"w{i}" for i in range(20)))]
        manifest = _make_manifest(chunks)
        report = ChunkManifestValidator(max_chunk_tokens=10).validate(manifest)
        assert report.oversized_chunks == 1
        assert not report.is_valid

    def test_orphan_chunk_detected(self):
        chunks = [_make_chunk("c_0", ""), _make_chunk("c_1", "real content here")]
        manifest = _make_manifest(chunks)
        report = ChunkManifestValidator().validate(manifest)
        assert report.orphan_chunks == 1
        assert not report.is_valid

    def test_duplicate_detected(self):
        chunks = [
            _make_chunk("c_0", "duplicate content here"),
            _make_chunk("c_1", "duplicate content here"),
        ]
        manifest = _make_manifest(chunks)
        report = ChunkManifestValidator().validate(manifest)
        assert report.duplicates == 1
        assert not report.is_valid

    def test_overlap_violation_detected(self):
        chunks = [
            _make_chunk("c_0", "identical chunk text"),
            _make_chunk("c_1", "identical chunk text"),
        ]
        manifest = _make_manifest(chunks)
        report = ChunkManifestValidator().validate(manifest)
        assert report.overlap_violations >= 1

    def test_total_chunks_count(self):
        chunks = [_make_chunk(f"c_{i}", f"content {i}") for i in range(5)]
        manifest = _make_manifest(chunks)
        report = ChunkManifestValidator().validate(manifest)
        assert report.total_chunks == 5

    def test_messages_populated_on_violations(self):
        chunks = [_make_chunk("c_0", "")]
        manifest = _make_manifest(chunks)
        report = ChunkManifestValidator().validate(manifest)
        assert len(report.messages) > 0

    def test_to_dict_contains_is_valid(self):
        chunks = [_make_chunk("c_0", "clean content here")]
        manifest = _make_manifest(chunks)
        report = ChunkManifestValidator().validate(manifest)
        d = report.to_dict()
        assert "is_valid" in d
        assert "total_chunks" in d


# ---------------------------------------------------------------------------
# ChunkQualityReport.is_valid boundary
# ---------------------------------------------------------------------------


class TestChunkQualityReportIsValid:
    def _make_report(self, **kwargs):
        defaults = {
            "doc_id": "d",
            "policy_name": "fixed_token",
            "total_chunks": 5,
            "duplicates": 0,
            "orphan_chunks": 0,
            "oversized_chunks": 0,
            "undersized_chunks": 0,
            "overlap_violations": 0,
        }
        defaults.update(kwargs)
        return ChunkQualityReport(**defaults)

    def test_all_zero_is_valid(self):
        assert self._make_report().is_valid

    def test_one_duplicate_invalid(self):
        assert not self._make_report(duplicates=1).is_valid

    def test_one_orphan_invalid(self):
        assert not self._make_report(orphan_chunks=1).is_valid

    def test_one_oversized_invalid(self):
        assert not self._make_report(oversized_chunks=1).is_valid

    def test_one_overlap_invalid(self):
        assert not self._make_report(overlap_violations=1).is_valid

    def test_undersized_alone_does_not_invalidate(self):
        # undersized is informational only
        assert self._make_report(undersized_chunks=3).is_valid
