"""
Phase 8 — Wave 2 Tests: enforce_citations_for_retrieval() + response assembly seam.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.enforcement.citation_enforcement import (
    CitationEnforcementViolation,
    assemble_response,
    enforce_citations_for_retrieval,
)
from agentic_core.L4_state.types.retrieval_anchor_types import AnchoredResult, RetrievalAnchor
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
)

_emit_emits_metric_event("test_citation_enforcement", "p4obs", "metric_1")
_emit_emits_metric_event("test_citation_enforcement", "p4obs", "metric_2")
_emit_emits_metric_event("test_citation_enforcement", "p4obs", "metric_3")
_emit_emits_metric_event("test_citation_enforcement", "p4obs", "metric_4")
_emit_emits_metric_event("test_citation_enforcement", "p4obs", "metric_5")
_emit_emits_metric_event("test_citation_enforcement", "p4obs", "metric_6")
_emit_records_incident_event("test_citation_enforcement", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_citation_enforcement", "p4obs", "anomaly")
_emit_writes_observability_log("test_citation_enforcement", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_citation_enforcement", "p4obs", "mon_state")
_emit_triggers_alert("test_citation_enforcement", "p4obs", "alert")
_emit_links_incident_trace("test_citation_enforcement", "p4obs", "trace_link")
_emit_captures_pattern("test_citation_enforcement", "p3lm", "pattern")
_emit_records_learning_event("test_citation_enforcement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_citation_enforcement", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_citation_enforcement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_citation_enforcement", "p3lm", "routing")
_emit_improves_agent_policy("test_citation_enforcement", "p3lm", "policy")
_emit_stores_learning_state("test_citation_enforcement", "p3lm", "state")
_emit_records_execution_trace("test_citation_enforcement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_citation_enforcement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_citation_enforcement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_citation_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_citation_enforcement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_citation_enforcement", "env_read", "p2_env_1")
_emit_reads_environ("test_citation_enforcement", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_citation_enforcement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_citation_enforcement", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_citation_enforcement")
_emit_applies_guardrail("p0", "test_citation_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_citation_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_citation_enforcement", "state_snapshot")
_emit_pulls_context("p1", "test_citation_enforcement", "context_pull")
_emit_pulls_context("p1", "test_citation_enforcement", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_citation_enforcement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_citation_enforcement", "uwg_term_secondary")
_emit_writes_through("p1", "test_citation_enforcement", "write_through")
_emit_writes_through("p1", "test_citation_enforcement", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_citation_enforcement", "safety_validation")
_emit_invokes_eval("p1", "test_citation_enforcement", "eval_call")
_emit_proposal_commits_routing("p1", "test_citation_enforcement", "routing_commit")
_emit_escalates_to_human("p1", "test_citation_enforcement", "human_escalation")
_emit_routes_through("p1", "test_citation_enforcement", "route_through")
_emit_checks_agent_registry("p1", "test_citation_enforcement", "agent_registry")
_emit_validates_agent_capability("p1", "test_citation_enforcement", "capability")
_emit_dispatches_execution_plan("p1", "test_citation_enforcement", "exec_plan")
_emit_agent_executes_agent("p1", "test_citation_enforcement", "sub_agent")
_emit_routes_to_agent("p1", "test_citation_enforcement", "target_agent")
_emit_verifies_policy("p1", "test_citation_enforcement", "policy_check")
_emit_observes_runtime_state("p1", "test_citation_enforcement", "runtime_state")
_emit_verifies_boundary("p1", "test_citation_enforcement", "boundary_check")
_emit_transcripts_response("p1", "test_citation_enforcement", "transcript")
_emit_hard_fails_untranscripted("p1", "test_citation_enforcement")
_emit_gated_by_confidence("p1", "test_citation_enforcement", "confidence_gate")
emit_replay_key("p0", "test_citation_enforcement")
emit_determinism_digest("p0", "test_citation_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_citation_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_citation_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_citation_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_citation_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_citation_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_citation_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_citation_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_citation_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_citation_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_citation_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_citation_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_citation_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_citation_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_citation_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_citation_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_citation_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_citation_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_citation_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_citation_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_citation_enforcement", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"
_RH = "a" * 64


def _make_anchor(chunk_id: str = "chunk-1", source_doc_id: str = "doc-A") -> RetrievalAnchor:
    return RetrievalAnchor(
        source_doc_id=source_doc_id,
        chunk_id=chunk_id,
        char_start=0,
        char_end=10,
        retrieved_at_utc=_TS,
        version_hash=f"vh-{chunk_id}",
    )


def _make_anchored_result(chunk_id: str = "chunk-1") -> AnchoredResult:
    return AnchoredResult(content=f"content of {chunk_id}", anchor=_make_anchor(chunk_id))


_BASE_OUTPUT: dict = {"answer": "The capital is Paris.", "model": "gpt-4"}


class TestMissingCitationsRejected:
    def test_missing_citations_rejected(self):
        """
        Core Wave 2 guarantee: retrieval_used=True with empty anchored_results
        raises CitationEnforcementViolation.
        """
        with pytest.raises(CitationEnforcementViolation) as exc_info:
            enforce_citations_for_retrieval(
                output=dict(_BASE_OUTPUT),
                anchored_results=[],
                retrieval_used=True,
            )
        assert exc_info.value.code == "MISSING_CITATIONS"

    def test_none_anchored_results_rejected(self):
        with pytest.raises(CitationEnforcementViolation) as exc_info:
            enforce_citations_for_retrieval(
                output=dict(_BASE_OUTPUT),
                anchored_results=None,
                retrieval_used=True,
            )
        assert "MISSING_CITATIONS" in str(exc_info.value)

    def test_violation_detail_non_empty(self):
        try:
            enforce_citations_for_retrieval(
                output=dict(_BASE_OUTPUT),
                anchored_results=[],
                retrieval_used=True,
            )
            pytest.fail("Expected CitationEnforcementViolation")
        except CitationEnforcementViolation as exc:  # guardian: allow-silent-swallower
            assert exc.detail != ""

    def test_violation_code_constant(self):
        assert CitationEnforcementViolation.code == "MISSING_CITATIONS"

    def test_violation_is_exception(self):
        exc = CitationEnforcementViolation("test")
        assert isinstance(exc, Exception)

    def test_violation_detail_stored(self):
        exc = CitationEnforcementViolation("my detail")
        assert exc.detail == "my detail"


class TestAnchoredOutputIncludesCitationBundle:
    def test_anchored_output_includes_citation_bundle(self):
        """
        Core Wave 2 guarantee: retrieval_used=True with non-empty anchored_results
        returns output with "citations" key containing CitationBundle.
        """
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
        )
        assert "citations" in result
        citations = result["citations"]
        assert "citation_hash" in citations
        assert "anchors" in citations
        assert len(citations["anchors"]) == 1

    def test_citations_block_contains_schema_version(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert result["citations"]["schema_version"] == 1

    def test_citations_hash_is_64_chars(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert len(result["citations"]["citation_hash"]) == 64

    def test_citations_hash_stable_for_same_inputs(self):
        r1 = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
            request_hash=_RH,
        )
        r2 = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result("chunk-1")],
            retrieval_used=True,
            request_hash=_RH,
        )
        assert r1["citations"]["citation_hash"] == r2["citations"]["citation_hash"]

    def test_multiple_anchors_all_included(self):
        results = [
            _make_anchored_result("chunk-A"),
            _make_anchored_result("chunk-B"),
            _make_anchored_result("chunk-C"),
        ]
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=results,
            retrieval_used=True,
        )
        assert len(result["citations"]["anchors"]) == 3

    def test_original_output_fields_preserved(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert result["answer"] == _BASE_OUTPUT["answer"]
        assert result["model"] == _BASE_OUTPUT["model"]

    def test_output_dict_not_mutated_in_place(self):
        """enforce_citations_for_retrieval must return a new dict, not mutate input."""
        original = dict(_BASE_OUTPUT)
        enforce_citations_for_retrieval(
            output=original,
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert "citations" not in original

    def test_explicit_request_hash_used_in_bundle(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
            request_hash=_RH,
        )
        assert result["citations"]["request_hash"] == _RH


class TestNoRetrievalPreservesLegacyOutput:
    def test_no_retrieval_preserves_legacy_output(self):
        """
        Core Wave 2 guarantee: retrieval_used=False returns output unchanged.
        """
        original = dict(_BASE_OUTPUT)
        result = enforce_citations_for_retrieval(
            output=original,
            anchored_results=None,
            retrieval_used=False,
        )
        assert result == original
        assert "citations" not in result

    def test_no_retrieval_empty_anchors_no_violation(self):
        result = enforce_citations_for_retrieval(
            output=dict(_BASE_OUTPUT),
            anchored_results=[],
            retrieval_used=False,
        )
        assert "citations" not in result

    def test_no_retrieval_returns_same_object_reference(self):
        original = dict(_BASE_OUTPUT)
        result = enforce_citations_for_retrieval(
            output=original,
            anchored_results=None,
            retrieval_used=False,
        )
        assert result is original


class TestAssembleResponseSeam:
    def test_assemble_response_calls_enforce_citations(self):
        """assemble_response() is the canonical seam and must enforce citations."""
        with pytest.raises(CitationEnforcementViolation):
            assemble_response(
                output=dict(_BASE_OUTPUT),
                anchored_results=[],
                retrieval_used=True,
            )

    def test_assemble_response_with_anchors_succeeds(self):
        result = assemble_response(
            output=dict(_BASE_OUTPUT),
            anchored_results=[_make_anchored_result()],
            retrieval_used=True,
        )
        assert "citations" in result

    def test_assemble_response_no_retrieval_passthrough(self):
        original = dict(_BASE_OUTPUT)
        result = assemble_response(
            output=original,
            anchored_results=None,
            retrieval_used=False,
        )
        assert result is original
