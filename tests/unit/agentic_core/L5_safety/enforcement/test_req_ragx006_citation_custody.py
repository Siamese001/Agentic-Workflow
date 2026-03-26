"""REQ-RAGX-006: ExternalKnowledgeAccessViolation enforcement.

Production enforcement: validate_citation_custody() in rag_guardrail.py.
CitationBundle dataclass for immutable citation binding.

Positive tests: properly cited context passes.
Negative tests: missing/incomplete citations raise ExternalKnowledgeAccessViolation.
"""

from __future__ import annotations

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_req_ragx006_citation_custody")
# REMOVED: _emit_applies_guardrail("p0", "test_req_ragx006_citation_custody", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_req_ragx006_citation_custody", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_req_ragx006_citation_custody", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_req_ragx006_citation_custody", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_req_ragx006_citation_custody", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_req_ragx006_citation_custody", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_req_ragx006_citation_custody", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_req_ragx006_citation_custody", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_req_ragx006_citation_custody", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_req_ragx006_citation_custody", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_req_ragx006_citation_custody", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_req_ragx006_citation_custody", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_req_ragx006_citation_custody", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_req_ragx006_citation_custody", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_req_ragx006_citation_custody", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_req_ragx006_citation_custody", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_req_ragx006_citation_custody", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_req_ragx006_citation_custody", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_req_ragx006_citation_custody", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_req_ragx006_citation_custody", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_req_ragx006_citation_custody", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_req_ragx006_citation_custody", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_req_ragx006_citation_custody", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_req_ragx006_citation_custody", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_req_ragx006_citation_custody", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_req_ragx006_citation_custody", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_req_ragx006_citation_custody", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_req_ragx006_citation_custody", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_req_ragx006_citation_custody", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_req_ragx006_citation_custody", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_req_ragx006_citation_custody", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_req_ragx006_citation_custody", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_req_ragx006_citation_custody", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_req_ragx006_citation_custody", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_req_ragx006_citation_custody", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_req_ragx006_citation_custody", "write_through")
# REMOVED: _emit_writes_through("p1", "test_req_ragx006_citation_custody", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_req_ragx006_citation_custody", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_req_ragx006_citation_custody", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_req_ragx006_citation_custody", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_req_ragx006_citation_custody", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_req_ragx006_citation_custody", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_req_ragx006_citation_custody", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_req_ragx006_citation_custody", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_req_ragx006_citation_custody", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_req_ragx006_citation_custody", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_req_ragx006_citation_custody", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_req_ragx006_citation_custody", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_req_ragx006_citation_custody", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_req_ragx006_citation_custody", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_req_ragx006_citation_custody", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_req_ragx006_citation_custody")
# REMOVED: _emit_gated_by_confidence("p1", "test_req_ragx006_citation_custody", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_req_ragx006_citation_custody")
# REMOVED: emit_determinism_digest("p0", "test_req_ragx006_citation_custody")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_req_ragx006_citation_custody", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_req_ragx006_citation_custody", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_req_ragx006_citation_custody", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_req_ragx006_citation_custody", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_req_ragx006_citation_custody", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_req_ragx006_citation_custody", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_req_ragx006_citation_custody", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_req_ragx006_citation_custody", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_req_ragx006_citation_custody", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_req_ragx006_citation_custody", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_req_ragx006_citation_custody", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_req_ragx006_citation_custody", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_req_ragx006_citation_custody", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_req_ragx006_citation_custody", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_req_ragx006_citation_custody", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_req_ragx006_citation_custody", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_req_ragx006_citation_custody", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_req_ragx006_citation_custody", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_req_ragx006_citation_custody", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_req_ragx006_citation_custody", "exec_snapshot_link")

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
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import CitationBundle
    from agentic_core.L5_safety.enforcement.rag_guardrail import CitationBundle
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
    from agentic_core.L5_safety.enforcement.rag_guardrail import (
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
        validate_citation_custody,
    )

    validate_citation_custody([], None)  # no context -> no enforcement needed


def test_empty_context_passes_without_citations():
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
        validate_citation_custody,
    )

    validate_citation_custody([], [])  # empty -> no enforcement needed


def test_single_chunk_with_matching_citation_passes():
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
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
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
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
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
        ExternalKnowledgeAccessViolation,
        validate_citation_custody,
    )

    chunks = [{"chunk_id": "c1", "text": "retrieved content"}]
    with pytest.raises(ExternalKnowledgeAccessViolation, match="CITATION_MISSING"):
        validate_citation_custody(chunks, None)


def test_context_with_empty_citations_raises():
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
        ExternalKnowledgeAccessViolation,
        validate_citation_custody,
    )

    chunks = [{"chunk_id": "c1", "text": "retrieved content"}]
    with pytest.raises(ExternalKnowledgeAccessViolation, match="CITATION_MISSING"):
        validate_citation_custody(chunks, [])


def test_partial_citations_raises_gap():
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
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
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
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
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import CitationBundle

    cb = CitationBundle(chunk_id="c1", source_ref="a.md", byte_sha256="a" * 64, byte_range=(0, 10), score=0.9)
    with pytest.raises((AttributeError, TypeError)):
        cb.chunk_id = "mutated"  # type: ignore[misc]


def test_citation_bundle_fields():
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import CitationBundle

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
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
        ExternalKnowledgeAccessViolation,
    )

    assert issubclass(ExternalKnowledgeAccessViolation, Exception)


def test_external_knowledge_access_violation_carries_message():
#  # MOVED: from agentic_core.L5_safety.enforcement.rag_guardrail import (
        ExternalKnowledgeAccessViolation,
    )

    err = ExternalKnowledgeAccessViolation("wave aborted")
    assert "wave aborted" in str(err)
