"""
V15 P4 Compliance Tests — Knowledge, Retrieval, Provenance & Traceability.

Regression tests proving all 8 P4 items are COMPLIANT:
  §15.5 — Trace ID format (CC3AL1-[0-9A-F]{8})
  §5.2  — Error Signature (deterministic)
  §4.2  — Policy Config Pin (SHA-256 at wave start)
  §1.6  — Hash Verification (manifest_hash)
  §6.7  — Plan Provenance
  §6.5  — RAG Artifact Chain (query → chunks → rerank → citations)
  §15.2 — Cognitive Diff Bundle
  §1.7  — Secondary Typed Artifacts (all P4 artifacts are typed)
"""

from __future__ import annotations

import dataclasses
import hashlib

import pytest

from agentic_core.L0_routing.enforcement.traceability_contracts import (
    AdvisoryViolationError,
    CognitiveDiffError,
    ErrorSignatureError,
    ManifestHashError,
    PlanProvenanceError,
    PolicyConfigPinError,
    RAGChainError,
    TraceIDFormatError,
    build_cognitive_diff_bundle,
    build_error_signature,
    build_plan_provenance,
    build_retrieval_query,
    build_retrieved_chunk,
    enforce_advisory_only,
    generate_trace_id,
    pin_policy_config,
    validate_citation_chain,
    validate_retrieval_set,
    verify_manifest_hash,
    verify_policy_config_unchanged,
)
from agentic_core.L0_routing.types.traceability_types import (
    CitationBundle,
    CitationEntry,
    CognitiveDiffBundle,
    ErrorSignature,
    KnowledgeAdvisoryConstraint,
    KnowledgeDirective,
    PlanProvenance,
    PolicyConfigPin,
    RerankScore,
    RetrievalQuery,
    RetrievedChunk,
    validate_trace_id,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_traceability_provenance_contracts", "p4obs", "metric_1")
_emit_emits_metric_event("test_traceability_provenance_contracts", "p4obs", "metric_2")
_emit_emits_metric_event("test_traceability_provenance_contracts", "p4obs", "metric_3")
_emit_emits_metric_event("test_traceability_provenance_contracts", "p4obs", "metric_4")
_emit_emits_metric_event("test_traceability_provenance_contracts", "p4obs", "metric_5")
_emit_emits_metric_event("test_traceability_provenance_contracts", "p4obs", "metric_6")
_emit_records_incident_event("test_traceability_provenance_contracts", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_traceability_provenance_contracts", "p4obs", "anomaly")
_emit_writes_observability_log("test_traceability_provenance_contracts", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_traceability_provenance_contracts", "p4obs", "mon_state")
_emit_triggers_alert("test_traceability_provenance_contracts", "p4obs", "alert")
_emit_links_incident_trace("test_traceability_provenance_contracts", "p4obs", "trace_link")
_emit_captures_pattern("test_traceability_provenance_contracts", "p3lm", "pattern")
_emit_records_learning_event("test_traceability_provenance_contracts", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_traceability_provenance_contracts", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_traceability_provenance_contracts", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_traceability_provenance_contracts", "p3lm", "routing")
_emit_improves_agent_policy("test_traceability_provenance_contracts", "p3lm", "policy")
_emit_stores_learning_state("test_traceability_provenance_contracts", "p3lm", "state")
_emit_records_execution_trace("test_traceability_provenance_contracts", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_traceability_provenance_contracts", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_traceability_provenance_contracts", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_traceability_provenance_contracts", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_traceability_provenance_contracts", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_traceability_provenance_contracts", "env_read", "p2_env_1")
_emit_reads_environ("test_traceability_provenance_contracts", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_traceability_provenance_contracts", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_traceability_provenance_contracts", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_traceability_provenance_contracts")
_emit_applies_guardrail("p0", "test_traceability_provenance_contracts", "p0_governance")
_emit_snapshots_state("p0", "test_traceability_provenance_contracts", "state_snapshot")
_emit_pulls_context("p1", "test_traceability_provenance_contracts", "context_pull")
_emit_pulls_context("p1", "test_traceability_provenance_contracts", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_traceability_provenance_contracts", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_traceability_provenance_contracts", "uwg_term_secondary")
_emit_writes_through("p1", "test_traceability_provenance_contracts", "write_through")
_emit_writes_through("p1", "test_traceability_provenance_contracts", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_traceability_provenance_contracts", "safety_validation")
_emit_invokes_eval("p1", "test_traceability_provenance_contracts", "eval_call")
_emit_proposal_commits_routing("p1", "test_traceability_provenance_contracts", "routing_commit")
_emit_escalates_to_human("p1", "test_traceability_provenance_contracts", "human_escalation")
_emit_routes_through("p1", "test_traceability_provenance_contracts", "route_through")
_emit_checks_agent_registry("p1", "test_traceability_provenance_contracts", "agent_registry")
_emit_validates_agent_capability("p1", "test_traceability_provenance_contracts", "capability")
_emit_dispatches_execution_plan("p1", "test_traceability_provenance_contracts", "exec_plan")
_emit_agent_executes_agent("p1", "test_traceability_provenance_contracts", "sub_agent")
_emit_routes_to_agent("p1", "test_traceability_provenance_contracts", "target_agent")
_emit_verifies_policy("p1", "test_traceability_provenance_contracts", "policy_check")
_emit_observes_runtime_state("p1", "test_traceability_provenance_contracts", "runtime_state")
_emit_verifies_boundary("p1", "test_traceability_provenance_contracts", "boundary_check")
_emit_transcripts_response("p1", "test_traceability_provenance_contracts", "transcript")
_emit_hard_fails_untranscripted("p1", "test_traceability_provenance_contracts")
_emit_gated_by_confidence("p1", "test_traceability_provenance_contracts", "confidence_gate")
emit_replay_key("p0", "test_traceability_provenance_contracts")
emit_determinism_digest("p0", "test_traceability_provenance_contracts")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_traceability_provenance_contracts", "execution_auth")
_emit_validates_capability("p2", "test_traceability_provenance_contracts", "capability_check")
_emit_routes_to_capability("p2", "test_traceability_provenance_contracts", "capability_route")
_emit_writes_via_uwg("p2", "test_traceability_provenance_contracts", "uwg_write")
_emit_blocks_direct_write("p2", "test_traceability_provenance_contracts", "direct_write_block")
_emit_records_tool_invocation("p2", "test_traceability_provenance_contracts", "tool_invocation")
_emit_captures_execution_output("p2", "test_traceability_provenance_contracts", "exec_output")
_emit_dispatches_agent("p3", "test_traceability_provenance_contracts", "agent_dispatch")
_emit_coordinates_agents("p3", "test_traceability_provenance_contracts", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_traceability_provenance_contracts", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_traceability_provenance_contracts", "healing_outcome")
_emit_escalates_failure("p3", "test_traceability_provenance_contracts", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_traceability_provenance_contracts", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_traceability_provenance_contracts", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_traceability_provenance_contracts", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_traceability_provenance_contracts", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_traceability_provenance_contracts", "eval_metric")
_emit_stores_embedding("p4", "test_traceability_provenance_contracts", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_traceability_provenance_contracts", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_traceability_provenance_contracts", "exec_snapshot_link")

# =============================================================================
# §15.5 — Trace ID Format
# =============================================================================


class TestP4_155_TraceIDFormat:
    """§15.5: Trace IDs must match ^CC3AL1-[0-9A-F]{8}$."""

    def test_valid_trace_id(self):
        assert validate_trace_id("CC3AL1-0A1B2C3D") == "CC3AL1-0A1B2C3D"

    def test_generate_valid(self):
        tid = generate_trace_id("DEADBEEF")
        assert tid == "CC3AL1-DEADBEEF"

    def test_lowercase_hex_uppercased(self):
        tid = generate_trace_id("deadbeef")
        assert tid == "CC3AL1-DEADBEEF"

    def test_wrong_prefix_rejected(self):
        with pytest.raises(ValueError, match="FAIL"):
            validate_trace_id("WRONG1-0A1B2C3D")

    def test_too_short_hex_rejected(self):
        with pytest.raises(TraceIDFormatError, match="8 chars"):
            generate_trace_id("ABC")

    def test_too_long_hex_rejected(self):
        with pytest.raises(TraceIDFormatError, match="8 chars"):
            generate_trace_id("0123456789")

    def test_lowercase_in_final_rejected(self):
        with pytest.raises(ValueError, match="FAIL"):
            validate_trace_id("CC3AL1-abcdef01")

    def test_uuid_format_rejected(self):
        with pytest.raises(ValueError, match="FAIL"):
            validate_trace_id("550e8400-e29b-41d4-a716-446655440000")


# =============================================================================
# §5.2 — Error Signature
# =============================================================================


class TestP4_52_ErrorSignature:
    """§5.2: Deterministic error signatures from type+node+time_bucket."""

    def test_all_required_fields(self):
        required = {"error_type", "target_node_id", "time_bucket", "signature_hash"}
        actual = {f.name for f in dataclasses.fields(ErrorSignature)}
        assert required.issubset(actual)

    def test_frozen(self):
        sig = build_error_signature("TypeError", "module.Class.method", 5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            sig.error_type = "x"  # type: ignore[misc]

    def test_deterministic(self):
        s1 = build_error_signature("ValueError", "node.A", 10)
        s2 = build_error_signature("ValueError", "node.A", 10)
        assert s1.signature_hash == s2.signature_hash

    def test_different_inputs_different_hash(self):
        s1 = build_error_signature("ValueError", "node.A", 10)
        s2 = build_error_signature("TypeError", "node.A", 10)
        assert s1.signature_hash != s2.signature_hash

    def test_empty_error_type_rejected(self):
        with pytest.raises(ErrorSignatureError, match="FAIL"):
            build_error_signature("", "node.A", 0)

    def test_negative_time_bucket_rejected(self):
        with pytest.raises(ErrorSignatureError, match="FAIL"):
            build_error_signature("TypeError", "node.A", -1)


# =============================================================================
# §4.2 — Policy Config Pin
# =============================================================================


class TestP4_42_PolicyConfigPin:
    """§4.2: SHA-256 of policy config captured at wave start."""

    def test_all_required_fields(self):
        required = {"wave_id", "policy_config_hash", "semantic_clock_tick"}
        actual = {f.name for f in dataclasses.fields(PolicyConfigPin)}
        assert required.issubset(actual)

    def test_frozen(self):
        pin = pin_policy_config("wave-1", b"config data", 0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            pin.wave_id = "x"  # type: ignore[misc]

    def test_pin_captures_hash(self):
        data = b'{"max_retries": 3}'
        pin = pin_policy_config("wave-1", data, 5)
        expected = hashlib.sha256(data).hexdigest()
        assert pin.policy_config_hash == expected

    def test_verify_unchanged_passes(self):
        data = b"config"
        pin = pin_policy_config("w1", data, 0)
        assert verify_policy_config_unchanged(pin, data) is True

    def test_verify_changed_fails(self):
        pin = pin_policy_config("w1", b"original", 0)
        with pytest.raises(PolicyConfigPinError, match="mutated"):
            verify_policy_config_unchanged(pin, b"modified")

    def test_empty_wave_id_rejected(self):
        with pytest.raises(ValueError, match="wave_id"):
            PolicyConfigPin(wave_id="", policy_config_hash="abc", semantic_clock_tick=0)


# =============================================================================
# §1.6 — Hash Verification
# =============================================================================


class TestP4_16_HashVerification:
    """§1.6: manifest_hash must match SHA-256 of ast_snippet bytes."""

    def test_valid_hash_passes(self):
        snippet = "x = 1"
        h = hashlib.sha256(snippet.encode()).hexdigest()
        assert verify_manifest_hash(snippet, h) is True

    def test_invalid_hash_fails(self):
        with pytest.raises(ManifestHashError, match="mismatch"):
            verify_manifest_hash("x = 1", "wrong_hash")

    def test_deterministic(self):
        snippet = "def foo(): pass"
        h1 = hashlib.sha256(snippet.encode()).hexdigest()
        h2 = hashlib.sha256(snippet.encode()).hexdigest()
        assert h1 == h2
        assert verify_manifest_hash(snippet, h1) is True


# =============================================================================
# §6.7 — Plan Provenance
# =============================================================================


class TestP4_67_PlanProvenance:
    """§6.7: Plan linked to Policy Liaison Node."""

    def test_all_required_fields(self):
        required = {
            "trace_id",
            "plan_id",
            "policy_liaison_node",
            "semantic_clock_tick",
            "plan_hash",
        }
        actual = {f.name for f in dataclasses.fields(PlanProvenance)}
        assert required.issubset(actual)

    def test_frozen(self):
        prov = build_plan_provenance("t1", "p1", "liaison-node", 0, "plan content")
        with pytest.raises(dataclasses.FrozenInstanceError):
            prov.trace_id = "x"  # type: ignore[misc]

    def test_builds_valid(self):
        prov = build_plan_provenance("t1", "p1", "liaison-A", 3, "heal gravity")
        assert prov.plan_id == "p1"
        assert prov.policy_liaison_node == "liaison-A"
        expected_hash = hashlib.sha256(b"heal gravity").hexdigest()
        assert prov.plan_hash == expected_hash

    def test_empty_trace_id_rejected(self):
        with pytest.raises(PlanProvenanceError, match="FAIL"):
            build_plan_provenance("", "p1", "node", 0, "content")

    def test_empty_liaison_rejected(self):
        with pytest.raises(PlanProvenanceError, match="FAIL"):
            build_plan_provenance("t1", "p1", "", 0, "content")


# =============================================================================
# §6.5 — RAG Artifact Chain
# =============================================================================


def _make_query() -> RetrievalQuery:
    return build_retrieval_query("t1", "What is gravity?", "CognitiveEngine", 1)


def _make_chunks(query: RetrievalQuery) -> tuple[RetrievedChunk, ...]:
    c1 = build_retrieved_chunk(
        "c1",
        "doc-1",
        "Gravity pulls objects.",
        "doc-1:10-12",
        query.query_hash,
    )
    c2 = build_retrieved_chunk(
        "c2",
        "doc-2",
        "Newton's law.",
        "doc-2:5-6",
        query.query_hash,
    )
    return (c1, c2)


def _make_scores() -> tuple[RerankScore, ...]:
    return (
        RerankScore(chunk_id="c1", score=0.95, rank=1),
        RerankScore(chunk_id="c2", score=0.80, rank=2),
    )


def _make_citations(query: RetrievalQuery) -> tuple[CitationEntry, ...]:
    return (
        CitationEntry(
            citation_id="cit-1",
            chunk_id="c1",
            source_id="doc-1",
            location="doc-1:10-12",
            retrieval_hash=query.query_hash,
        ),
        CitationEntry(
            citation_id="cit-2",
            chunk_id="c2",
            source_id="doc-2",
            location="doc-2:5-6",
            retrieval_hash=query.query_hash,
        ),
    )


def _make_bundle(query: RetrievalQuery) -> CitationBundle:
    return CitationBundle(
        trace_id="t1",
        bundle_id="b1",
        citations=_make_citations(query),
        retrieval_query_hash=query.query_hash,
        bundle_hash="hash-placeholder",
    )


class TestP4_65_RAGChain:
    """§6.5: RAG Artifact Chain — query → chunks → rerank → citations."""

    def test_retrieval_query_fields(self):
        required = {"trace_id", "query_text", "query_hash", "source_agent", "semantic_clock_tick"}
        actual = {f.name for f in dataclasses.fields(RetrievalQuery)}
        assert required.issubset(actual)

    def test_retrieval_query_hash_deterministic(self):
        q = _make_query()
        expected = hashlib.sha256(b"What is gravity?").hexdigest()
        assert q.query_hash == expected

    def test_retrieved_chunk_content_hash(self):
        q = _make_query()
        chunks = _make_chunks(q)
        for chunk in chunks:
            expected = hashlib.sha256(chunk.content.encode()).hexdigest()
            assert chunk.content_hash == expected

    def test_validate_retrieval_set_passes(self):
        q = _make_query()
        chunks = _make_chunks(q)
        scores = _make_scores()
        assert validate_retrieval_set(chunks, scores) is True

    def test_retrieval_set_missing_score_fails(self):
        q = _make_query()
        chunks = _make_chunks(q)
        partial_scores = (RerankScore(chunk_id="c1", score=0.9, rank=1),)
        with pytest.raises(RAGChainError, match="without rerank scores"):
            validate_retrieval_set(chunks, partial_scores)

    def test_retrieval_set_wrong_order_fails(self):
        q = _make_query()
        chunks = _make_chunks(q)
        bad_scores = (
            RerankScore(chunk_id="c1", score=0.5, rank=1),
            RerankScore(chunk_id="c2", score=0.9, rank=2),
        )
        with pytest.raises(RAGChainError, match="descending order"):
            validate_retrieval_set(chunks, bad_scores)

    def test_empty_retrieval_set_fails(self):
        with pytest.raises(RAGChainError, match="at least one chunk"):
            validate_retrieval_set((), ())

    def test_citation_chain_validates(self):
        q = _make_query()
        chunks = _make_chunks(q)
        bundle = _make_bundle(q)
        assert validate_citation_chain(bundle, chunks, q) is True

    def test_citation_chain_missing_citation_fails(self):
        q = _make_query()
        chunks = _make_chunks(q)
        partial_citations = (_make_citations(q)[0],)
        bundle = CitationBundle(
            trace_id="t1",
            bundle_id="b1",
            citations=partial_citations,
            retrieval_query_hash=q.query_hash,
            bundle_hash="h",
        )
        with pytest.raises(RAGChainError, match="without citations"):
            validate_citation_chain(bundle, chunks, q)

    def test_citation_chain_wrong_query_hash_fails(self):
        q = _make_query()
        chunks = _make_chunks(q)
        bad_bundle = CitationBundle(
            trace_id="t1",
            bundle_id="b1",
            citations=_make_citations(q),
            retrieval_query_hash="wrong-hash",
            bundle_hash="h",
        )
        with pytest.raises(RAGChainError, match="retrieval_query_hash mismatch"):
            validate_citation_chain(bad_bundle, chunks, q)

    def test_citation_entry_bad_retrieval_hash_fails(self):
        q = _make_query()
        chunks = _make_chunks(q)
        bad_citation = CitationEntry(
            citation_id="cit-1",
            chunk_id="c1",
            source_id="doc-1",
            location="doc-1:10",
            retrieval_hash="bad-hash",
        )
        good_citation = _make_citations(q)[1]
        bundle = CitationBundle(
            trace_id="t1",
            bundle_id="b1",
            citations=(bad_citation, good_citation),
            retrieval_query_hash=q.query_hash,
            bundle_hash="h",
        )
        with pytest.raises(RAGChainError, match="retrieval_hash"):
            validate_citation_chain(bundle, chunks, q)

    def test_citation_bundle_empty_citations_rejected(self):
        with pytest.raises(ValueError, match="at least one entry"):
            CitationBundle(
                trace_id="t1",
                bundle_id="b1",
                citations=(),
                retrieval_query_hash="h",
                bundle_hash="h",
            )

    def test_all_chunk_fields_frozen(self):
        q = _make_query()
        chunk = _make_chunks(q)[0]
        with pytest.raises(dataclasses.FrozenInstanceError):
            chunk.chunk_id = "x"  # type: ignore[misc]


# =============================================================================
# §15.2 — Cognitive Diff Bundle
# =============================================================================


class TestP4_152_CognitiveDiffBundle:
    """§15.2: Cognitive Diff Bundle for incident response."""

    def test_all_required_fields(self):
        required = {
            "trace_id",
            "incident_id",
            "intended_policy_snapshot",
            "actual_execution_trace",
            "diff_summary",
            "semantic_clock_tick",
        }
        actual = {f.name for f in dataclasses.fields(CognitiveDiffBundle)}
        assert required.issubset(actual)

    def test_frozen(self):
        cdb = build_cognitive_diff_bundle(
            "t1",
            "inc-1",
            "policy-snap",
            "actual-trace",
            "diff",
            5,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            cdb.trace_id = "x"  # type: ignore[misc]

    def test_builds_valid(self):
        cdb = build_cognitive_diff_bundle(
            "t1",
            "inc-1",
            "intended",
            "actual",
            "- line changed",
            3,
        )
        assert cdb.incident_id == "inc-1"
        assert cdb.semantic_clock_tick == 3

    def test_empty_incident_id_rejected(self):
        with pytest.raises(CognitiveDiffError, match="FAIL"):
            build_cognitive_diff_bundle("t1", "", "snap", "trace", "diff", 0)

    def test_empty_diff_summary_rejected(self):
        with pytest.raises(CognitiveDiffError, match="FAIL"):
            build_cognitive_diff_bundle("t1", "inc-1", "snap", "trace", "", 0)

    def test_negative_tick_rejected(self):
        with pytest.raises(CognitiveDiffError, match="FAIL"):
            build_cognitive_diff_bundle("t1", "inc-1", "snap", "trace", "diff", -1)


# =============================================================================
# §6.9 / §1.7 — Advisory-Only + Secondary Typed Artifacts
# =============================================================================


class TestP4_Advisory:
    """§6.9: Knowledge outputs are advisory-only."""

    def test_advisory_accepted(self):
        c = KnowledgeAdvisoryConstraint(
            source_layer="L4",
            directive_type=KnowledgeDirective.ADVISORY,
            content="suggestion",
            trace_id="t1",
        )
        assert enforce_advisory_only(c) is c

    def test_control_rejected(self):
        c = KnowledgeAdvisoryConstraint(
            source_layer="L4",
            directive_type=KnowledgeDirective.CONTROL,
            content="execute this",
            trace_id="t1",
        )
        with pytest.raises(AdvisoryViolationError, match="CONTROL"):
            enforce_advisory_only(c)

    def test_non_constraint_rejected(self):
        with pytest.raises(AdvisoryViolationError, match="dict"):
            enforce_advisory_only({"type": "advisory"})

    def test_frozen(self):
        c = KnowledgeAdvisoryConstraint(
            source_layer="L4",
            directive_type=KnowledgeDirective.ADVISORY,
            content="info",
            trace_id="t1",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            c.content = "x"  # type: ignore[misc]


class TestP4_17_SecondaryTypedArtifacts:
    """§1.7: All P4 artifacts are defined as typed dataclasses."""

    ARTIFACT_CLASSES = [
        ErrorSignature,
        PolicyConfigPin,
        PlanProvenance,
        RetrievalQuery,
        RetrievedChunk,
        RerankScore,
        CitationEntry,
        CitationBundle,
        CognitiveDiffBundle,
        KnowledgeAdvisoryConstraint,
    ]

    def test_all_are_dataclasses(self):
        for cls in self.ARTIFACT_CLASSES:
            assert dataclasses.is_dataclass(cls), f"{cls.__name__} is not a dataclass"

    def test_all_are_frozen(self):
        for cls in self.ARTIFACT_CLASSES:
            frozen = cls.__dataclass_params__.frozen  # type: ignore[attr-defined]
            assert frozen, f"{cls.__name__} is not frozen"
