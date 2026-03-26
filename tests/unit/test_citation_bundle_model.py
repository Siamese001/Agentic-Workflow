"""
Phase 8 — Wave 1 Tests: CitationBundle model + deterministic validation.
"""

from __future__ import annotations

import pytest

    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_citation_bundle_model", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_citation_bundle_model", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_citation_bundle_model", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_citation_bundle_model", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_citation_bundle_model", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_citation_bundle_model", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_citation_bundle_model", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_citation_bundle_model", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_citation_bundle_model", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_citation_bundle_model", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_citation_bundle_model", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_citation_bundle_model", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_citation_bundle_model", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_citation_bundle_model", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_citation_bundle_model", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_citation_bundle_model", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_citation_bundle_model", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_citation_bundle_model", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_citation_bundle_model", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_citation_bundle_model", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_citation_bundle_model", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_citation_bundle_model", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_citation_bundle_model", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_citation_bundle_model", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_citation_bundle_model", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_citation_bundle_model", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_citation_bundle_model", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_citation_bundle_model", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_citation_bundle_model")
# REMOVED: _emit_applies_guardrail("p0", "test_citation_bundle_model", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_citation_bundle_model", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_citation_bundle_model", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_citation_bundle_model", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_citation_bundle_model", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_citation_bundle_model", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_citation_bundle_model", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_citation_bundle_model", "write_through")
# REMOVED: _emit_writes_through("p1", "test_citation_bundle_model", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_citation_bundle_model", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_citation_bundle_model", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_citation_bundle_model", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_citation_bundle_model", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_citation_bundle_model", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_citation_bundle_model", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_citation_bundle_model", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_citation_bundle_model", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_citation_bundle_model", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_citation_bundle_model", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_citation_bundle_model", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_citation_bundle_model", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_citation_bundle_model", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_citation_bundle_model", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_citation_bundle_model")
# REMOVED: _emit_gated_by_confidence("p1", "test_citation_bundle_model", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_citation_bundle_model")
# REMOVED: emit_determinism_digest("p0", "test_citation_bundle_model")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_citation_bundle_model", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_citation_bundle_model", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_citation_bundle_model", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_citation_bundle_model", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_citation_bundle_model", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_citation_bundle_model", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_citation_bundle_model", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_citation_bundle_model", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_citation_bundle_model", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_citation_bundle_model", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_citation_bundle_model", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_citation_bundle_model", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_citation_bundle_model", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_citation_bundle_model", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_citation_bundle_model", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_citation_bundle_model", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_citation_bundle_model", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_citation_bundle_model", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_citation_bundle_model", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_citation_bundle_model", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"
_RH = "a" * 64


def _make_anchor(
    source_doc_id: str = "doc-A",
    chunk_id: str = "chunk-1",
    char_start: int = 0,
    char_end: int = 10,
    version_hash: str = "vh-1",
) -> RetrievalAnchor:
    return RetrievalAnchor(
        source_doc_id=source_doc_id,
        chunk_id=chunk_id,
        char_start=char_start,
        char_end=char_end,
        retrieved_at_utc=_TS,
        version_hash=version_hash,
    )


def _make_bundle(anchors: list[RetrievalAnchor] | None = None, **overrides) -> CitationBundle:
    defaults: dict = {
        "schema_version": 1,
        "request_hash": _RH,
        "anchors": anchors if anchors is not None else [_make_anchor()],
    }
    defaults.update(overrides)
    return CitationBundle(**defaults)


class TestCitationBundleHashStable:
    def test_citation_bundle_hash_stable(self):
        """Same inputs produce the same citation_hash on repeated construction."""
        from agentic_core.L4_state.types.citation_bundle_types import (
            CitationBundle,
            build_citation_bundle,
        )
        from agentic_core.L4_state.types.retrieval_anchor_types import RetrievalAnchor
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
            _emit_reads_policy_state,  # noqa: E402
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

        b1 = _make_bundle()
        b2 = _make_bundle()
        assert b1.citation_hash == b2.citation_hash
        assert len(b1.citation_hash) == 64

    def test_hash_changes_with_request_hash(self):
        b1 = _make_bundle(request_hash="a" * 64)
        b2 = _make_bundle(request_hash="b" * 64)
        assert b1.citation_hash != b2.citation_hash

    def test_hash_changes_with_anchors(self):
        b1 = _make_bundle(anchors=[_make_anchor(chunk_id="chunk-X")])
        b2 = _make_bundle(anchors=[_make_anchor(chunk_id="chunk-Y")])
        assert b1.citation_hash != b2.citation_hash

    def test_hash_changes_with_version_hash(self):
        b1 = _make_bundle(anchors=[_make_anchor(version_hash="vh-1")])
        b2 = _make_bundle(anchors=[_make_anchor(version_hash="vh-2")])
        assert b1.citation_hash != b2.citation_hash

    def test_citation_hash_excluded_from_canonical_bytes(self):
        b = _make_bundle()
        assert b"citation_hash" not in b.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        b1 = _make_bundle()
        b2 = _make_bundle()
        assert b1.canonical_bytes() == b2.canonical_bytes()

    def test_volatile_field_excluded_from_canonical_bytes(self):
        """retrieved_at_utc is volatile — must not appear in canonical_bytes."""
        b = _make_bundle()
        assert b"retrieved_at_utc" not in b.canonical_bytes()

    def test_hash_stable_across_different_retrieved_at(self):
        """Two anchors differing only in retrieved_at_utc must produce the same hash."""
        a1 = RetrievalAnchor(
            source_doc_id="doc-A",
            chunk_id="chunk-1",
            char_start=0,
            char_end=10,
            retrieved_at_utc="2026-01-01T00:00:00Z",
            version_hash="vh-1",
        )
        a2 = RetrievalAnchor(
            source_doc_id="doc-A",
            chunk_id="chunk-1",
            char_start=0,
            char_end=10,
            retrieved_at_utc="2026-02-01T00:00:00Z",
            version_hash="vh-1",
        )
        b1 = _make_bundle(anchors=[a1])
        b2 = _make_bundle(anchors=[a2])
        assert b1.citation_hash == b2.citation_hash


class TestCitationBundleRequiresAnchorsWhenRetrievalUsed:
    def test_citation_bundle_requires_anchors_when_retrieval_used(self):
        """
        CitationBundle with empty anchors list is structurally valid
        (the enforcement of non-empty is done by enforce_citations_for_retrieval).
        But build_citation_bundle with non-empty anchors must succeed.
        """
        b = build_citation_bundle(request_hash=_RH, anchors=[_make_anchor()])
        assert len(b.anchors) == 1

    def test_empty_anchors_list_is_allowed_in_bundle(self):
        """CitationBundle itself allows empty anchors — enforcement is at the seam."""
        b = _make_bundle(anchors=[])
        assert b.anchors == []
        assert len(b.citation_hash) == 64

    def test_multiple_anchors_stored(self):
        anchors = [
            _make_anchor(chunk_id="chunk-1"),
            _make_anchor(chunk_id="chunk-2"),
        ]
        b = _make_bundle(anchors=anchors)
        assert len(b.anchors) == 2

    def test_invalid_schema_version_raises(self):
    """Test invalid_schema_version_raises contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"


class TestAnchorOrderingDeterministic:
    def test_anchor_ordering_deterministic(self):
        """
        Anchors in canonical_bytes must be sorted by (source_doc_id, chunk_id, char_start)
        regardless of construction order.
        """
        anchors_unsorted = [
            _make_anchor(source_doc_id="doc-Z", chunk_id="chunk-1", char_start=0, char_end=5),
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-1", char_start=0, char_end=5),
            _make_anchor(source_doc_id="doc-M", chunk_id="chunk-1", char_start=0, char_end=5),
        ]
        anchors_sorted = [
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-1", char_start=0, char_end=5),
            _make_anchor(source_doc_id="doc-M", chunk_id="chunk-1", char_start=0, char_end=5),
            _make_anchor(source_doc_id="doc-Z", chunk_id="chunk-1", char_start=0, char_end=5),
        ]
        b1 = _make_bundle(anchors=anchors_unsorted)
        b2 = _make_bundle(anchors=anchors_sorted)
        assert b1.citation_hash == b2.citation_hash

    def test_anchors_stored_sorted_by_source_doc_id(self):
        anchors = [
            _make_anchor(source_doc_id="doc-Z"),
            _make_anchor(source_doc_id="doc-A"),
        ]
        b = _make_bundle(anchors=anchors)
        doc_ids = [a.source_doc_id for a in b.anchors]
        assert doc_ids == sorted(doc_ids)

    def test_anchors_sorted_by_chunk_id_within_doc(self):
        anchors = [
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-Z"),
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-A"),
        ]
        b = _make_bundle(anchors=anchors)
        chunk_ids = [a.chunk_id for a in b.anchors]
        assert chunk_ids == sorted(chunk_ids)

    def test_anchors_sorted_by_char_start_within_chunk(self):
        anchors = [
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-1", char_start=50, char_end=60),
            _make_anchor(source_doc_id="doc-A", chunk_id="chunk-1", char_start=10, char_end=20),
        ]
        b = _make_bundle(anchors=anchors)
        starts = [a.char_start for a in b.anchors]
        assert starts == sorted(starts)

    def test_to_dict_contains_all_fields(self):
        b = _make_bundle()
        d = b.to_dict()
        assert "schema_version" in d
        assert "request_hash" in d
        assert "anchors" in d
        assert "citation_hash" in d

    def test_factory_produces_valid_bundle(self):
        b = build_citation_bundle(request_hash=_RH, anchors=[_make_anchor()])
        assert isinstance(b, CitationBundle)
        assert len(b.citation_hash) == 64
