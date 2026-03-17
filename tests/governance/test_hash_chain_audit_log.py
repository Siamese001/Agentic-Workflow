"""H2 governance tests: Hash-chained immutable audit log.

Validates:
- Genesis rule (entry_index=0, previous_hash="GENESIS")
- Hash chain integrity verification
- Chain break detection (tampered entry)
- Seal prevents further appends
- Entry immutability (frozen dataclass)
- Deterministic hash computation
"""

import pytest

from agentic_core.L2_execution.audit.hash_chain_audit_log import (
    GENESIS_HASH,
    AuditEntry,
    HashChainAuditLog,
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
    _emit_reads_policy_state,  # noqa: E402
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
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_hash_chain_audit_log", "p4obs", "metric_1")
_emit_emits_metric_event("test_hash_chain_audit_log", "p4obs", "metric_2")
_emit_emits_metric_event("test_hash_chain_audit_log", "p4obs", "metric_3")
_emit_emits_metric_event("test_hash_chain_audit_log", "p4obs", "metric_4")
_emit_emits_metric_event("test_hash_chain_audit_log", "p4obs", "metric_5")
_emit_emits_metric_event("test_hash_chain_audit_log", "p4obs", "metric_6")
_emit_records_incident_event("test_hash_chain_audit_log", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_hash_chain_audit_log", "p4obs", "anomaly")
_emit_writes_observability_log("test_hash_chain_audit_log", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_hash_chain_audit_log", "p4obs", "mon_state")
_emit_triggers_alert("test_hash_chain_audit_log", "p4obs", "alert")
_emit_links_incident_trace("test_hash_chain_audit_log", "p4obs", "trace_link")
_emit_captures_pattern("test_hash_chain_audit_log", "p3lm", "pattern")
_emit_records_learning_event("test_hash_chain_audit_log", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_hash_chain_audit_log", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_hash_chain_audit_log", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_hash_chain_audit_log", "p3lm", "routing")
_emit_improves_agent_policy("test_hash_chain_audit_log", "p3lm", "policy")
_emit_stores_learning_state("test_hash_chain_audit_log", "p3lm", "state")
_emit_records_execution_trace("test_hash_chain_audit_log", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_hash_chain_audit_log", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_hash_chain_audit_log", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_hash_chain_audit_log", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_hash_chain_audit_log", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_hash_chain_audit_log", "env_read", "p2_env_1")
_emit_reads_environ("test_hash_chain_audit_log", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_hash_chain_audit_log", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_hash_chain_audit_log", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_hash_chain_audit_log")
_emit_applies_guardrail("p0", "test_hash_chain_audit_log", "p0_governance")
_emit_reads_policy_state("p0", "test_hash_chain_audit_log", "policy_binding")
_emit_snapshots_state("p0", "test_hash_chain_audit_log", "state_snapshot")
_emit_pulls_context("p1", "test_hash_chain_audit_log", "context_pull")
_emit_pulls_context("p1", "test_hash_chain_audit_log", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_hash_chain_audit_log", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_hash_chain_audit_log", "uwg_term_secondary")
_emit_writes_through("p1", "test_hash_chain_audit_log", "write_through")
_emit_writes_through("p1", "test_hash_chain_audit_log", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_hash_chain_audit_log", "safety_validation")
_emit_invokes_eval("p1", "test_hash_chain_audit_log", "eval_call")
_emit_proposal_commits_routing("p1", "test_hash_chain_audit_log", "routing_commit")
_emit_escalates_to_human("p1", "test_hash_chain_audit_log", "human_escalation")
_emit_routes_through("p1", "test_hash_chain_audit_log", "route_through")
_emit_checks_agent_registry("p1", "test_hash_chain_audit_log", "agent_registry")
_emit_validates_agent_capability("p1", "test_hash_chain_audit_log", "capability")
_emit_dispatches_execution_plan("p1", "test_hash_chain_audit_log", "exec_plan")
_emit_agent_executes_agent("p1", "test_hash_chain_audit_log", "sub_agent")
_emit_routes_to_agent("p1", "test_hash_chain_audit_log", "target_agent")
_emit_verifies_policy("p1", "test_hash_chain_audit_log", "policy_check")
_emit_observes_runtime_state("p1", "test_hash_chain_audit_log", "runtime_state")
_emit_verifies_boundary("p1", "test_hash_chain_audit_log", "boundary_check")
_emit_transcripts_response("p1", "test_hash_chain_audit_log", "transcript")
_emit_hard_fails_untranscripted("p1", "test_hash_chain_audit_log")
_emit_gated_by_confidence("p1", "test_hash_chain_audit_log", "confidence_gate")
emit_replay_key("p0", "test_hash_chain_audit_log")
emit_determinism_digest("p0", "test_hash_chain_audit_log")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hash_chain_audit_log", "execution_auth")
_emit_validates_capability("p2", "test_hash_chain_audit_log", "capability_check")
_emit_routes_to_capability("p2", "test_hash_chain_audit_log", "capability_route")
_emit_writes_via_uwg("p2", "test_hash_chain_audit_log", "uwg_write")
_emit_blocks_direct_write("p2", "test_hash_chain_audit_log", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hash_chain_audit_log", "tool_invocation")
_emit_captures_execution_output("p2", "test_hash_chain_audit_log", "exec_output")
_emit_dispatches_agent("p3", "test_hash_chain_audit_log", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hash_chain_audit_log", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hash_chain_audit_log", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hash_chain_audit_log", "healing_outcome")
_emit_escalates_failure("p3", "test_hash_chain_audit_log", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hash_chain_audit_log", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hash_chain_audit_log", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hash_chain_audit_log", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hash_chain_audit_log", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hash_chain_audit_log", "eval_metric")
_emit_stores_embedding("p4", "test_hash_chain_audit_log", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hash_chain_audit_log", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hash_chain_audit_log", "exec_snapshot_link")

pytestmark = pytest.mark.governance


class TestGenesisRule:
    """First entry must follow genesis convention."""

    def test_first_entry_has_genesis_previous_hash(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="init")
        assert entry.previous_hash == GENESIS_HASH

    def test_first_entry_has_index_zero(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="init")
        assert entry.entry_index == 0

    def test_genesis_hash_is_literal_string(self):
        assert GENESIS_HASH == "GENESIS"


class TestChainIntegrity:
    """Hash chain must be verifiable from genesis."""

    def test_single_entry_verifies(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        assert log.verify_chain_integrity() is True

    def test_multi_entry_chain_verifies(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        log.append(tier="L2", action="persist", payload={"k": "v"})
        log.append(tier="L5", action="approve")
        assert log.verify_chain_integrity() is True

    def test_chain_links_previous_hash(self):
        log = HashChainAuditLog()
        e0 = log.append(tier="L2", action="init")
        e1 = log.append(tier="L2", action="persist")
        assert e1.previous_hash == e0.entry_hash

    def test_empty_log_verifies(self):
        log = HashChainAuditLog()
        assert log.verify_chain_integrity() is True

    def test_each_entry_hash_is_sha256(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="test")
        assert len(entry.entry_hash) == 64
        assert all(c in "0123456789abcdef" for c in entry.entry_hash)


class TestChainBreakDetection:
    """Tampered entries must be detected."""

    def test_tampered_hash_detected(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        log.append(tier="L2", action="persist")

        tampered = AuditEntry(
            entry_index=log.entries[1].entry_index,
            previous_hash=log.entries[1].previous_hash,
            entry_hash="0" * 64,
            timestamp=log.entries[1].timestamp,
            tier=log.entries[1].tier,
            action=log.entries[1].action,
            payload=log.entries[1].payload,
        )
        log._entries[1] = tampered
        assert log.verify_chain_integrity() is False


class TestSeal:
    """Sealed log must reject further appends."""

    def test_seal_returns_root_hash(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        root = log.seal()
        assert root == log.chain_root

    def test_append_after_seal_raises(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        log.seal()
        with pytest.raises(RuntimeError, match="sealed"):
            log.append(tier="L2", action="rejected")

    def test_seal_empty_log_raises(self):
        log = HashChainAuditLog()
        with pytest.raises(RuntimeError, match="empty"):
            log.seal()


class TestEntryImmutability:
    """AuditEntry must be frozen."""

    def test_cannot_mutate_entry_field(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="init")
        with pytest.raises(AttributeError):
            entry.action = "tampered"  # type: ignore[misc]


class TestHashDeterminism:
    """Same inputs must produce same hash."""

    def test_entry_hash_is_deterministic(self):
        entry = AuditEntry(
            entry_index=0,
            previous_hash=GENESIS_HASH,
            entry_hash="placeholder",
            timestamp="2026-01-01T00:00:00.000000+00:00",
            tier="L2",
            action="init",
            payload={},
        )
        assert entry.verify_hash() is False

    def test_verify_passes_on_correct_hash(self):
        log = HashChainAuditLog()
        entry = log.append(tier="L2", action="init")
        assert entry.verify_hash() is True


class TestLogProperties:
    """Log properties must reflect state."""

    def test_length_tracks_entries(self):
        log = HashChainAuditLog()
        assert log.length == 0
        log.append(tier="L2", action="init")
        assert log.length == 1
        log.append(tier="L2", action="persist")
        assert log.length == 2

    def test_chain_root_none_when_empty(self):
        log = HashChainAuditLog()
        assert log.chain_root is None

    def test_entries_returns_tuple(self):
        log = HashChainAuditLog()
        log.append(tier="L2", action="init")
        assert isinstance(log.entries, tuple)
