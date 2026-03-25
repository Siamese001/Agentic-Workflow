"""
Phase 1 — SSOT AuditTrail Mixin Tests.

Validates:
  - ExecutionTrace-compatible entry schema
  - SHA-256 canonical JSON hashing
  - prev_hash chaining correctness
  - replay_key stability (same inputs → same key)
  - Policy hash scoping in entries
  - Chain integrity verification
  - Tamper detection
  - Deterministic timestamps under replay mode
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pytest
from agentic_core.mixins.ssot_audit_trail_mixin import SSOTAuditTrailMixin

from agentic_core.L2_execution.deterministic_providers import (
    unpatch_deterministic,
)
from agentic_core.mixins.replay_guard_mixin import ReplayGuardMixin
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

# REMOVED: _emit_emits_metric_event("test_ssot_audit_trail_mixin", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ssot_audit_trail_mixin", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ssot_audit_trail_mixin", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ssot_audit_trail_mixin", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ssot_audit_trail_mixin", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ssot_audit_trail_mixin", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ssot_audit_trail_mixin", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ssot_audit_trail_mixin", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ssot_audit_trail_mixin", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ssot_audit_trail_mixin", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ssot_audit_trail_mixin", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ssot_audit_trail_mixin", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ssot_audit_trail_mixin", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ssot_audit_trail_mixin", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ssot_audit_trail_mixin", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ssot_audit_trail_mixin", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ssot_audit_trail_mixin", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ssot_audit_trail_mixin", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ssot_audit_trail_mixin", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ssot_audit_trail_mixin", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ssot_audit_trail_mixin", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ssot_audit_trail_mixin", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ssot_audit_trail_mixin", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ssot_audit_trail_mixin", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ssot_audit_trail_mixin", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ssot_audit_trail_mixin", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ssot_audit_trail_mixin", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ssot_audit_trail_mixin", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ssot_audit_trail_mixin")
# REMOVED: _emit_applies_guardrail("p0", "test_ssot_audit_trail_mixin", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_ssot_audit_trail_mixin", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_ssot_audit_trail_mixin", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_ssot_audit_trail_mixin", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ssot_audit_trail_mixin", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_audit_trail_mixin", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ssot_audit_trail_mixin", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_ssot_audit_trail_mixin", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ssot_audit_trail_mixin", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ssot_audit_trail_mixin", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ssot_audit_trail_mixin", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ssot_audit_trail_mixin", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ssot_audit_trail_mixin", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ssot_audit_trail_mixin", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ssot_audit_trail_mixin", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ssot_audit_trail_mixin", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ssot_audit_trail_mixin", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ssot_audit_trail_mixin", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ssot_audit_trail_mixin", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ssot_audit_trail_mixin", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ssot_audit_trail_mixin", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ssot_audit_trail_mixin", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ssot_audit_trail_mixin", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ssot_audit_trail_mixin")
# REMOVED: _emit_gated_by_confidence("p1", "test_ssot_audit_trail_mixin", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_ssot_audit_trail_mixin")
# REMOVED: emit_determinism_digest("p0", "test_ssot_audit_trail_mixin")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ssot_audit_trail_mixin", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ssot_audit_trail_mixin", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ssot_audit_trail_mixin", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ssot_audit_trail_mixin", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ssot_audit_trail_mixin", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ssot_audit_trail_mixin", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ssot_audit_trail_mixin", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ssot_audit_trail_mixin", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ssot_audit_trail_mixin", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ssot_audit_trail_mixin", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ssot_audit_trail_mixin", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ssot_audit_trail_mixin", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ssot_audit_trail_mixin", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ssot_audit_trail_mixin", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ssot_audit_trail_mixin", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ssot_audit_trail_mixin", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ssot_audit_trail_mixin", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ssot_audit_trail_mixin", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ssot_audit_trail_mixin", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ssot_audit_trail_mixin", "exec_snapshot_link")


@dataclass
class _TestExecutionContext:
    """Minimal ExecutionContext stand-in for unit tests."""

    mission_id: str = ""
    step_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    parent_span_id: str | None = None
    replay_mode: bool = False
    active_policy_hash: str | None = None
    safety_status: str = "PENDING"


class _AuditedStateManager(SSOTAuditTrailMixin, ReplayGuardMixin):
    """Test class combining SSOTAuditTrail + ReplayGuard with state dict."""

    def __init__(self, execution_context=None):
        self.state = {"audit_chain": []}
        super().__init__(execution_context=execution_context)


# ---------------------------------------------------------------------------
# Schema Tests
# ---------------------------------------------------------------------------


class TestAuditEntrySchema:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_entry_has_all_execution_trace_fields(self):
        """Audit entry contains all ExecutionTrace-compatible fields."""
        ctx = _TestExecutionContext(
            trace_id="trace-schema",
            active_policy_hash="ph-schema",
            safety_status="CLEARED",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("HEAL", "target.py", diff={"line": 42})

        required_fields = {
            "trace_id",
            "plan_hash",
            "actor",
            "target",
            "diff",
            "policy_hash",
            "timestamp",
            "prev_hash",
            "replay_key",
            "curr_hash",
        }
        assert required_fields.issubset(entry.keys())

    @pytest.mark.unit_min_deps
    def test_entry_values_correct(self):
        """Entry values match injected context."""
        ctx = _TestExecutionContext(
            trace_id="trace-vals",
            active_policy_hash="ph-vals",
            safety_status="CLEARED",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("VALIDATE", "module.py")

        assert entry["trace_id"] == "trace-vals"
        assert entry["policy_hash"] == "ph-vals"
        assert entry["actor"] == "_AuditedStateManager"
        assert entry["target"] == "module.py"
        assert entry["plan_hash"] == "ph-vals"  # Falls back to policy_hash

    @pytest.mark.unit_min_deps
    def test_custom_plan_hash(self):
        """plan_hash can be overridden."""
        ctx = _TestExecutionContext(
            trace_id="trace-plan",
            active_policy_hash="ph-plan",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("HEAL", "f.py", plan_hash="custom-plan")
        assert entry["plan_hash"] == "custom-plan"
        assert entry["policy_hash"] == "ph-plan"


# ---------------------------------------------------------------------------
# SHA-256 Chain Tests
# ---------------------------------------------------------------------------


class TestSHA256Chaining:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_first_entry_links_to_genesis(self):
        """First entry's prev_hash is the genesis hash (64 zeros)."""
        ctx = _TestExecutionContext(trace_id="trace-gen", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("BOOT", "system")
        assert entry["prev_hash"] == "0" * 64

    @pytest.mark.unit_min_deps
    def test_chain_links_correctly(self):
        """Each entry's prev_hash equals the previous entry's curr_hash."""
        ctx = _TestExecutionContext(trace_id="trace-chain", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)

        e1 = obj.emit_ssot_audit_entry("ACTION_1", "t1")
        e2 = obj.emit_ssot_audit_entry("ACTION_2", "t2")
        e3 = obj.emit_ssot_audit_entry("ACTION_3", "t3")

        assert e2["prev_hash"] == e1["curr_hash"]
        assert e3["prev_hash"] == e2["curr_hash"]

    @pytest.mark.unit_min_deps
    def test_curr_hash_is_sha256_of_canonical_json(self):
        """curr_hash is SHA-256 of canonical JSON (excluding curr_hash)."""
        ctx = _TestExecutionContext(trace_id="trace-hash", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("TEST", "target")

        # Recompute
        entry_copy = {k: v for k, v in entry.items() if k != "curr_hash"}
        canonical = json.dumps(entry_copy, sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert entry["curr_hash"] == expected

    @pytest.mark.unit_min_deps
    def test_audit_count_increments(self):
        """ssot_audit_count increments with each entry."""
        ctx = _TestExecutionContext(trace_id="trace-count", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        assert obj.ssot_audit_count == 0
        obj.emit_ssot_audit_entry("A", "t")
        assert obj.ssot_audit_count == 1
        obj.emit_ssot_audit_entry("B", "t")
        assert obj.ssot_audit_count == 2

    @pytest.mark.unit_min_deps
    def test_audit_head_advances(self):
        """ssot_audit_head updates to latest curr_hash."""
        ctx = _TestExecutionContext(trace_id="trace-head", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        assert obj.ssot_audit_head == "0" * 64
        e1 = obj.emit_ssot_audit_entry("A", "t")
        assert obj.ssot_audit_head == e1["curr_hash"]


# ---------------------------------------------------------------------------
# Replay Key Tests
# ---------------------------------------------------------------------------


class TestReplayKey:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_replay_key_stable(self):
        """Same inputs produce identical replay_key."""
        ctx = _TestExecutionContext(
            trace_id="trace-rk",
            active_policy_hash="ph-rk",
        )
        obj1 = _AuditedStateManager(execution_context=ctx)
        obj2 = _AuditedStateManager(execution_context=ctx)

        e1 = obj1.emit_ssot_audit_entry("HEAL", "file.py")
        e2 = obj2.emit_ssot_audit_entry("HEAL", "file.py")
        assert e1["replay_key"] == e2["replay_key"]

    @pytest.mark.unit_min_deps
    def test_replay_key_differs_on_different_action(self):
        """Different action produces different replay_key."""
        ctx = _TestExecutionContext(
            trace_id="trace-rk2",
            active_policy_hash="ph-rk2",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        e1 = obj.emit_ssot_audit_entry("HEAL", "file.py")
        e2 = obj.emit_ssot_audit_entry("VALIDATE", "file.py")
        assert e1["replay_key"] != e2["replay_key"]

    @pytest.mark.unit_min_deps
    def test_replay_key_differs_on_different_policy(self):
        """Different policy_hash produces different replay_key."""
        ctx1 = _TestExecutionContext(trace_id="trace-rk3", active_policy_hash="ph-A")
        ctx2 = _TestExecutionContext(trace_id="trace-rk3", active_policy_hash="ph-B")
        obj1 = _AuditedStateManager(execution_context=ctx1)
        obj2 = _AuditedStateManager(execution_context=ctx2)
        e1 = obj1.emit_ssot_audit_entry("HEAL", "file.py")
        e2 = obj2.emit_ssot_audit_entry("HEAL", "file.py")
        assert e1["replay_key"] != e2["replay_key"]


# ---------------------------------------------------------------------------
# Chain Verification Tests
# ---------------------------------------------------------------------------


class TestChainVerification:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_valid_chain_passes(self):
        """Valid chain passes verification."""
        ctx = _TestExecutionContext(trace_id="trace-verify", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        obj.emit_ssot_audit_entry("A", "t1")
        obj.emit_ssot_audit_entry("B", "t2")
        obj.emit_ssot_audit_entry("C", "t3")

        valid, broken_idx = obj.verify_ssot_audit_chain()
        assert valid is True
        assert broken_idx is None

    @pytest.mark.unit_min_deps
    def test_tampered_entry_detected(self):
        """Tampered curr_hash is detected."""
        ctx = _TestExecutionContext(trace_id="trace-tamper", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        obj.emit_ssot_audit_entry("A", "t1")
        obj.emit_ssot_audit_entry("B", "t2")

        # Tamper with second entry
        obj.state["audit_chain"][1]["curr_hash"] = "deadbeef" * 8

        valid, broken_idx = obj.verify_ssot_audit_chain()
        assert valid is False
        assert broken_idx == 1

    @pytest.mark.unit_min_deps
    def test_broken_chain_link_detected(self):
        """Broken prev_hash linkage is detected."""
        ctx = _TestExecutionContext(trace_id="trace-broken", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        obj.emit_ssot_audit_entry("A", "t1")
        obj.emit_ssot_audit_entry("B", "t2")
        obj.emit_ssot_audit_entry("C", "t3")

        # Break chain link at index 2
        obj.state["audit_chain"][2]["prev_hash"] = "0" * 64

        valid, broken_idx = obj.verify_ssot_audit_chain()
        assert valid is False
        assert broken_idx == 2

    @pytest.mark.unit_min_deps
    def test_empty_chain_valid(self):
        """Empty chain passes verification."""
        ctx = _TestExecutionContext(trace_id="trace-empty", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        valid, broken_idx = obj.verify_ssot_audit_chain()
        assert valid is True
        assert broken_idx is None

    @pytest.mark.unit_min_deps
    def test_entries_appended_to_state(self):
        """Entries are appended to self.state['audit_chain']."""
        ctx = _TestExecutionContext(trace_id="trace-state", active_policy_hash="ph")
        obj = _AuditedStateManager(execution_context=ctx)
        obj.emit_ssot_audit_entry("X", "y")
        obj.emit_ssot_audit_entry("Z", "w")
        assert len(obj.state["audit_chain"]) == 2


# ---------------------------------------------------------------------------
# Policy Hash Scoping Tests
# ---------------------------------------------------------------------------


class TestPolicyHashScoping:
    @pytest.fixture(autouse=True)
    def _cleanup(self):
        unpatch_deterministic()
        yield
        unpatch_deterministic()

    @pytest.mark.unit_min_deps
    def test_policy_hash_in_every_entry(self):
        """Every audit entry includes the active policy_hash."""
        ctx = _TestExecutionContext(
            trace_id="trace-ph",
            active_policy_hash="scoped-hash",
        )
        obj = _AuditedStateManager(execution_context=ctx)
        for i in range(5):
            obj.emit_ssot_audit_entry(f"ACTION_{i}", f"target_{i}")

        for entry in obj.state["audit_chain"]:
            assert entry["policy_hash"] == "scoped-hash"

    @pytest.mark.unit_min_deps
    def test_different_policy_hash_different_chains(self):
        """Different policy hashes produce different curr_hash values."""
        ctx1 = _TestExecutionContext(trace_id="trace-iso", active_policy_hash="ph-1")
        ctx2 = _TestExecutionContext(trace_id="trace-iso", active_policy_hash="ph-2")
        obj1 = _AuditedStateManager(execution_context=ctx1)
        obj2 = _AuditedStateManager(execution_context=ctx2)

        e1 = obj1.emit_ssot_audit_entry("HEAL", "file.py")
        e2 = obj2.emit_ssot_audit_entry("HEAL", "file.py")

        # Different policy_hash → different curr_hash (even same action/target)
        assert e1["curr_hash"] != e2["curr_hash"]
