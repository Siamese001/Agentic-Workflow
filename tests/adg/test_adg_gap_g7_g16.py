"""Tests for ADG G7-G16 runtime modules and static AST visitors.

Covers:
  G7:  sandbox_airlock.py + _SandboxAirlockVisitor
  G8:  capability_budget.py + _CapabilityBudgetVisitor
  G9:  jit_context.py + _JITContextVisitor
  G10: boundary_verifier.py + _BoundaryVerifierVisitor
  G11: determinism_control.py + _DeterminismControlVisitor
  G12: io_interception.py + _IOInterceptionVisitor
  G13: mutation_transport.py + _MutationTransportVisitor
  G14: execution_proof.py + _ExecutionProofVisitor
  G15: path_control.py + _PathControlVisitor
  G16: eval_spine.py + _EvalSpineVisitor
"""

from __future__ import annotations

import ast
import textwrap

import pytest

# ---------------------------------------------------------------------------
# G10: Boundary verifier
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.boundary_verifier import (
    BoundaryPacket,
    CapabilityChokepoint,
    L2BoundaryVerifier,
    VerificationOutcome,
)

# ---------------------------------------------------------------------------
# G8: Capability budget
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.capability_budget import (
    BudgetExceededError,
    BudgetStatus,
    ResourceGovernor,
    ResourceGrant,
    ToolBudget,
)

# ---------------------------------------------------------------------------
# G11: Determinism control
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.determinism_control import (
    DeterminismController,
    DeterminismViolationType,
    ReplayGuard,
    SemanticClock,
)

# ---------------------------------------------------------------------------
# G16: Evaluation spine
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.eval_spine import (
    DPOBatch,
    DriftAlert,
    EvalSpine,
    OptimizationStage,
)

# ---------------------------------------------------------------------------
# G14: Execution proof
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.execution_proof import (
    ExecutionProofRecorder,
    ExecutionTrace,
    ProofComparisonOutcome,
    ReplayKey,
)

# ---------------------------------------------------------------------------
# G12: IO interception
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.io_interception import (
    InterceptionOutcome,
    IOInterceptor,
    NetworkTranscript,
)

# ---------------------------------------------------------------------------
# G9: JIT context
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.jit_context import (
    ContextSnapshot,
    FreezeState,
    JITContextSynchronizer,
)

# ---------------------------------------------------------------------------
# G13: Mutation transport
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.mutation_transport import (
    CommitPhase,
    MutationTransport,
)

# ---------------------------------------------------------------------------
# G15: Path control
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.path_control import (
    ExecutionPath,
    ExecutionPathController,
)

# ---------------------------------------------------------------------------
# G7: Sandbox airlock
# ---------------------------------------------------------------------------
from agentic_core.adg.runtime.sandbox_airlock import (
    AirlockPhase,
    CapabilityToken,
    SandboxAirlockRecorder,
    SandboxEnvelope,
    WorkContract,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
)

_emit_applies_guardrail("p0", "test_adg_gap_g7_g16", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_gap_g7_g16", "policy_binding")
_emit_snapshots_state("p0", "test_adg_gap_g7_g16", "state_snapshot")
_emit_authorize_and_execute("p2", "test_adg_gap_g7_g16", "execution_auth")
_emit_validates_capability("p2", "test_adg_gap_g7_g16", "capability_check")
_emit_routes_to_capability("p2", "test_adg_gap_g7_g16", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_gap_g7_g16", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_gap_g7_g16", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_gap_g7_g16", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_gap_g7_g16", "exec_output")
_emit_dispatches_agent("p3", "test_adg_gap_g7_g16", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_gap_g7_g16", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_gap_g7_g16", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_gap_g7_g16", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_gap_g7_g16", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_gap_g7_g16", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_gap_g7_g16", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_gap_g7_g16", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_gap_g7_g16", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_gap_g7_g16", "eval_metric")
_emit_stores_embedding("p4", "test_adg_gap_g7_g16", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_gap_g7_g16", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_gap_g7_g16", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_adg_gap_g7_g16", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_gap_g7_g16", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_gap_g7_g16", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_gap_g7_g16", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_gap_g7_g16", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_gap_g7_g16", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_gap_g7_g16", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_gap_g7_g16", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_gap_g7_g16", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_gap_g7_g16", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_gap_g7_g16", "p4obs", "alert")
_emit_links_incident_trace("test_adg_gap_g7_g16", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_gap_g7_g16", "p3lm", "pattern")
_emit_records_learning_event("test_adg_gap_g7_g16", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_gap_g7_g16", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_gap_g7_g16", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_gap_g7_g16", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_gap_g7_g16", "p3lm", "policy")
_emit_stores_learning_state("test_adg_gap_g7_g16", "p3lm", "state")
_emit_records_execution_trace("test_adg_gap_g7_g16", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_gap_g7_g16", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_gap_g7_g16", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_gap_g7_g16", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_gap_g7_g16", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_gap_g7_g16", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_gap_g7_g16", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_gap_g7_g16", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_gap_g7_g16", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_gap_g7_g16", "context_pull")
_emit_pulls_context("p1", "test_adg_gap_g7_g16", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_gap_g7_g16", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_gap_g7_g16", "uwg_term_2")
_emit_writes_through("p1", "test_adg_gap_g7_g16", "write_through")
_emit_writes_through("p1", "test_adg_gap_g7_g16", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_gap_g7_g16", "safety_validation")
_emit_invokes_eval("p1", "test_adg_gap_g7_g16", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_gap_g7_g16", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_gap_g7_g16", "human_escalation")
_emit_routes_through("p1", "test_adg_gap_g7_g16", "route_through")
_emit_checks_agent_registry("p1", "test_adg_gap_g7_g16", "agent_registry")
_emit_validates_agent_capability("p1", "test_adg_gap_g7_g16", "capability")
_emit_dispatches_execution_plan("p1", "test_adg_gap_g7_g16", "exec_plan")
_emit_agent_executes_agent("p1", "test_adg_gap_g7_g16", "sub_agent")
_emit_routes_to_agent("p1", "test_adg_gap_g7_g16", "target_agent")
_emit_verifies_policy("p1", "test_adg_gap_g7_g16", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_gap_g7_g16", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_gap_g7_g16", "boundary_check")
_emit_transcripts_response("p1", "test_adg_gap_g7_g16", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_gap_g7_g16")
_emit_gated_by_confidence("p1", "test_adg_gap_g7_g16", "confidence_gate")

# ===========================================================================
# G7 — Sandbox Airlock
# ===========================================================================


class TestWorkContract:
    def test_stamp_sets_fields(self) -> None:
        wc = WorkContract()
        wc.stamp("agent-1", "run-1", payload="hello", ttl_seconds=60.0)
        assert wc.agent_id == "agent-1"
        assert wc.run_id == "run-1"
        assert wc.payload_hash != ""
        assert wc.expires_at > wc.issued_at

    def test_is_expired_false_for_fresh(self) -> None:
        wc = WorkContract()
        wc.stamp("a", "r", ttl_seconds=300.0)
        assert not wc.is_expired

    def test_to_dict(self) -> None:
        wc = WorkContract()
        d = wc.to_dict()
        assert "contract_id" in d
        assert "is_expired" in d


class TestCapabilityToken:
    def test_bind(self) -> None:
        wc = WorkContract()
        wc.stamp("a", "r")
        token = CapabilityToken()
        token.bind(wc, ["read", "write"])
        assert token.contract_id == wc.contract_id
        assert "read" in token.scope

    def test_revoke(self) -> None:
        token = CapabilityToken()
        assert not token.revoked
        token.revoke()
        assert token.revoked


class TestSandboxEnvelope:
    def test_enter_exit(self) -> None:
        wc = WorkContract()
        wc.stamp("a", "r")
        token = CapabilityToken()
        token.bind(wc, [])
        env = SandboxEnvelope()
        env.enter(wc, token)
        assert env.phase == AirlockPhase.ENTERED
        env.exit()
        assert env.phase == AirlockPhase.EXITED
        assert env.duration_ms >= 0.0

    def test_reject(self) -> None:
        env = SandboxEnvelope()
        env.reject("contract_expired")
        assert env.phase == AirlockPhase.REJECTED
        assert env.rejection_reason == "contract_expired"


class TestSandboxAirlockRecorder:
    def test_full_lifecycle(self) -> None:
        rec = SandboxAirlockRecorder("agent-x", "run-1")
        contract = rec.stamp_contract(payload="task", ttl_seconds=120.0)
        token = rec.issue_token(contract, scope=["tool:write"])
        env = rec.enter_sandbox(contract, token)
        assert env.phase == AirlockPhase.ENTERED
        rec.exit_sandbox(env)
        assert env.phase == AirlockPhase.EXITED
        assert token.revoked

    def test_rejected_on_revoked_token(self) -> None:
        rec = SandboxAirlockRecorder("agent-x", "run-2")
        contract = rec.stamp_contract()
        token = rec.issue_token(contract)
        token.revoke()
        env = rec.enter_sandbox(contract, token)
        assert env.phase == AirlockPhase.REJECTED

    def test_session_summary_keys(self) -> None:
        rec = SandboxAirlockRecorder("a", "r")
        summary = rec.session_summary
        assert "envelope_count" in summary
        assert "entry_count" in summary


# ===========================================================================
# G8 — Capability Budget
# ===========================================================================


class TestResourceGrant:
    def test_consume_within_limit(self) -> None:
        grant = ResourceGrant("compute_ms", 1000.0, unit="ms")
        grant.consume(200.0)
        assert grant.remaining == 800.0
        assert grant.status == BudgetStatus.OK

    def test_consume_exceeds_raises(self) -> None:
        grant = ResourceGrant("compute_ms", 100.0)
        with pytest.raises(BudgetExceededError):
            grant.consume(200.0)

    def test_warning_threshold(self) -> None:
        grant = ResourceGrant("memory_mb", 100.0)
        grant.consume(91.0)
        assert grant.status == BudgetStatus.WARNING


class TestToolBudget:
    def test_default_has_standard_grants(self) -> None:
        budget = ToolBudget.default(agent_id="a", contract_id="c")
        assert "compute_ms" in budget.grants
        assert "memory_mb" in budget.grants
        assert "tool_calls" in budget.grants

    def test_consume_tool_call(self) -> None:
        budget = ToolBudget.default()
        budget.consume("tool_calls", 1.0)
        assert budget.grants["tool_calls"].consumed == 1.0

    def test_revoke(self) -> None:
        budget = ToolBudget.default()
        budget.revoke()
        assert budget.overall_status == BudgetStatus.REVOKED

    def test_exceed_raises(self) -> None:
        budget = ToolBudget.default(compute_ms=10.0)
        with pytest.raises(BudgetExceededError):
            budget.consume("compute_ms", 20.0)


class TestResourceGovernor:
    def test_consume_and_report(self) -> None:
        gov = ResourceGovernor("a", "r")
        budget = ToolBudget.default()
        gov.activate_budget(budget)
        result = gov.consume("tool_calls", 1.0)
        assert result is True
        assert gov.report.exceeded_count == 0

    def test_consume_exceeded_returns_false(self) -> None:
        gov = ResourceGovernor("a", "r")
        budget = ToolBudget.default(compute_ms=5.0)
        gov.activate_budget(budget)
        result = gov.consume("compute_ms", 100.0)
        assert result is False
        assert gov.report.exceeded_count == 1


# ===========================================================================
# G9 — JIT Context
# ===========================================================================


class TestContextSnapshot:
    def test_freeze(self) -> None:
        snap = ContextSnapshot(agent_id="a", run_id="r")
        assert not snap.frozen
        snap.freeze()
        assert snap.frozen

    def test_to_dict(self) -> None:
        snap = ContextSnapshot()
        d = snap.to_dict()
        assert "snapshot_id" in d
        assert "frozen" in d


class TestJITContextSynchronizer:
    def test_pull_context(self) -> None:
        sync = JITContextSynchronizer("a", "r")
        snap = sync.pull_context(c0_context_hash="abc123", capability_token_id="ct-1")
        assert snap.c0_context_hash == "abc123"
        assert len(sync.session.snapshots) == 1

    def test_freeze_and_unfreeze(self) -> None:
        sync = JITContextSynchronizer("a", "r")
        snap = sync.pull_context()
        boundary = sync.freeze_context(snap)
        assert boundary.freeze_state == FreezeState.FROZEN
        assert snap.frozen
        sync.unfreeze_context(boundary)
        assert boundary.freeze_state == FreezeState.RELEASED

    def test_sync_context_atomic(self) -> None:
        sync = JITContextSynchronizer("a", "r")
        snap, boundary = sync.sync_context(state_hash="sh1", budget_id="b1")
        assert snap.frozen
        assert boundary.freeze_state == FreezeState.FROZEN

    def test_session_summary(self) -> None:
        sync = JITContextSynchronizer("a", "r")
        sync.sync_context()
        s = sync.session_summary
        assert s["frozen_count"] == 1


# ===========================================================================
# G10 — Boundary Verifier
# ===========================================================================


class TestL2BoundaryVerifier:
    def test_valid_packet_accepted(self) -> None:
        verifier = L2BoundaryVerifier("agent-a", "run-1")
        packet = BoundaryPacket(
            agent_id="agent-a",
            envelope_id="env-1",
            token_id="ct-1",
            l5_cert_hash="certabc",
        )
        result = verifier.verify(packet)
        assert result.accepted
        assert result.outcome == VerificationOutcome.ACCEPTED

    def test_missing_cert_rejected(self) -> None:
        verifier = L2BoundaryVerifier("agent-a", "run-1")
        packet = BoundaryPacket(agent_id="agent-a", envelope_id="env-1", token_id="ct-1")
        result = verifier.verify(packet)
        assert not result.accepted
        assert result.outcome == VerificationOutcome.REJECTED_NO_CERT

    def test_missing_token_rejected(self) -> None:
        verifier = L2BoundaryVerifier("agent-a", "run-1")
        packet = BoundaryPacket(agent_id="a", envelope_id="e", l5_cert_hash="cert")
        result = verifier.verify(packet)
        assert not result.accepted

    def test_certify_envelope(self) -> None:
        verifier = L2BoundaryVerifier("agent-a", "run-1")
        result = verifier.certify_envelope("env-1", "ct-1", "cert123")
        assert result.accepted

    def test_report_counts(self) -> None:
        verifier = L2BoundaryVerifier("agent-a", "run-1")
        verifier.certify_envelope("e1", "t1", "cert1")
        verifier.certify_envelope("", "", "")
        assert verifier.report.accepted_count == 1
        assert verifier.report.rejected_count == 1


class TestCapabilityChokepoint:
    def test_certify_valid(self) -> None:
        cp = CapabilityChokepoint("a")
        assert cp.certify("tok1", "cert1") is True
        assert cp.is_certified("tok1")

    def test_certify_invalid(self) -> None:
        cp = CapabilityChokepoint("a")
        assert cp.certify("", "") is False
        assert cp.rejected_count == 1


# ===========================================================================
# G11 — Determinism Control
# ===========================================================================


class TestSemanticClock:
    def test_now_increments_seq(self) -> None:
        clock = SemanticClock("run-1")
        r1 = clock.now()
        r2 = clock.now()
        assert r2.logical_seq > r1.logical_seq
        assert clock.tick_count == 2

    def test_readings_recorded(self) -> None:
        clock = SemanticClock("run-1")
        clock.now()
        assert len(clock.readings) == 1


class TestReplayGuard:
    def test_install_patches(self) -> None:
        guard = ReplayGuard("run-1")
        patches = guard.install_replay_patches()
        assert len(patches) > 0
        assert guard.patch_count > 0

    def test_seed_rng(self) -> None:
        guard = ReplayGuard("run-1")
        rec = guard.seed_rng(42)
        assert rec.patch_type == "rng_seed"


class TestDeterminismController:
    def test_install_all_patches(self) -> None:
        ctrl = DeterminismController("a", "r")
        ctrl.install_all_patches(seed=99)
        assert ctrl.report.rng_seed == 99

    def test_record_violation(self) -> None:
        ctrl = DeterminismController("a", "r")
        v = ctrl.record_violation(DeterminismViolationType.UNSEEDED_RNG, "module.py", "detail")
        assert v.violation_type == DeterminismViolationType.UNSEEDED_RNG
        assert ctrl.report.violation_count == 1

    def test_emit_digest(self) -> None:
        ctrl = DeterminismController("a", "r")
        ctrl.seed_rng(42)
        digest = ctrl.emit_determinism_digest(events=["e1", "e2"])
        assert digest.digest_hash != ""
        assert digest.rng_seed == 42
        assert ctrl.report.digest is not None

    def test_fully_deterministic(self) -> None:
        ctrl = DeterminismController("a", "r")
        ctrl.seed_rng(1)
        assert ctrl.report.is_fully_deterministic

    def test_not_fully_deterministic_with_violations(self) -> None:
        ctrl = DeterminismController("a", "r")
        ctrl.seed_rng(1)
        ctrl.record_violation(DeterminismViolationType.UNTRANSCRIPTED_RANDOM)
        assert not ctrl.report.is_fully_deterministic


# ===========================================================================
# G12 — IO Interception
# ===========================================================================


class TestNetworkTranscript:
    def test_capture_hashes(self) -> None:
        t = NetworkTranscript()
        t.capture("https://api.example.com", "POST", '{"q": "hello"}', '{"ok": true}', 200)
        assert t.request_hash != ""
        assert t.response_hash != ""
        assert t.url == "https://api.example.com"


class TestIOInterceptor:
    def test_intercept_io_transcripted(self) -> None:
        interceptor = IOInterceptor("a", "r")
        ev = interceptor.intercept_io("https://example.com", "GET", response_body='{"x":1}')
        assert ev.outcome == InterceptionOutcome.TRANSCRIPTED
        assert len(interceptor.report.transcripts) == 1

    def test_transcript_response(self) -> None:
        interceptor = IOInterceptor("a", "r")
        t = interceptor.transcript_response("https://api.com", '{"data": []}')
        assert isinstance(t, NetworkTranscript)

    def test_hard_fail_raises(self) -> None:
        interceptor = IOInterceptor("a", "r", hard_fail_on_untranscripted=True)
        with pytest.raises(RuntimeError, match="Hard-fail"):
            interceptor.hard_fail_untranscripted("https://evil.com")

    def test_hard_fail_no_raise(self) -> None:
        interceptor = IOInterceptor("a", "r", hard_fail_on_untranscripted=False)
        ev = interceptor.hard_fail_untranscripted("https://evil.com")
        assert ev.outcome == InterceptionOutcome.HARD_FAILED

    def test_report_summary(self) -> None:
        interceptor = IOInterceptor("a", "r", hard_fail_on_untranscripted=False)
        interceptor.intercept_io("https://a.com")
        interceptor.hard_fail_untranscripted("https://b.com")
        assert interceptor.report.transcripted_count == 1
        assert interceptor.report.hard_failed_count == 1


# ===========================================================================
# G13 — Mutation Transport
# ===========================================================================


class TestMutationTransport:
    def test_package_diff(self) -> None:
        mt = MutationTransport("a", "r")
        patches = [{"op": "replace", "path": "/x", "value": 1}]
        packet = mt.package_diff(patches)
        assert packet.phase == CommitPhase.DIFF_PACKAGED
        assert packet.diff_hash != ""

    def test_validate_blast_radius_approved(self) -> None:
        mt = MutationTransport("a", "r")
        packet = mt.package_diff([{"op": "add", "path": "/y", "value": 2}])
        approved = mt.validate_blast_radius(packet, score=0.3)
        assert approved
        assert packet.blast_radius_approved

    def test_validate_blast_radius_exceeded(self) -> None:
        mt = MutationTransport("a", "r")
        packet = mt.package_diff([])
        approved = mt.validate_blast_radius(packet, score=0.95)
        assert not approved

    def test_sign_and_commit(self) -> None:
        mt = MutationTransport("a", "r")
        packet = mt.package_diff([{"op": "remove", "path": "/z"}])
        mt.validate_blast_radius(packet, score=0.1)
        mt.sign_execution_trace(packet, "my-trace-payload")
        committed = mt.commit_mutation(packet)
        assert committed
        assert packet.phase == CommitPhase.PHASE2_COMMITTED

    def test_commit_aborts_without_signature(self) -> None:
        mt = MutationTransport("a", "r")
        packet = mt.package_diff([])
        mt.validate_blast_radius(packet, score=0.1)
        committed = mt.commit_mutation(packet)
        assert not committed
        assert packet.phase == CommitPhase.ABORTED

    def test_distribute(self) -> None:
        mt = MutationTransport("a", "r")
        packet = mt.package_diff([])
        mt.validate_blast_radius(packet, score=0.0)
        mt.sign_execution_trace(packet)
        mt.commit_mutation(packet)
        mt.distribute_mutation(packet)
        assert packet.phase == CommitPhase.DISTRIBUTED


# ===========================================================================
# G14 — Execution Proof
# ===========================================================================


class TestExecutionTrace:
    def test_record_and_seal(self) -> None:
        trace = ExecutionTrace(run_id="r", agent_id="a")
        trace.record_event("tool_call", {"tool": "search"})
        trace.record_event("tool_response")
        hash_ = trace.seal()
        assert trace.sealed
        assert hash_ != ""
        assert trace.event_count == 2

    def test_sign(self) -> None:
        trace = ExecutionTrace(run_id="r", agent_id="a")
        trace.record_event("evt")
        sig = trace.sign("secret")
        assert sig != ""
        assert trace.signature == sig


class TestExecutionProofRecorder:
    def test_start_and_record_trace(self) -> None:
        rec = ExecutionProofRecorder("a", "r")
        trace = rec.start_trace()
        rec.record_execution_trace("step1")
        assert trace.event_count == 1

    def test_emit_replay_key(self) -> None:
        rec = ExecutionProofRecorder("a", "r")
        rec.start_trace()
        key = rec.emit_replay_key(rng_seed=42, clock_start_ns=100)
        assert isinstance(key, ReplayKey)
        assert key.rng_seed == 42

    def test_compare_proof_match(self) -> None:
        rec = ExecutionProofRecorder("a", "r")
        t1 = rec.start_trace()
        rec.record_execution_trace("e1")
        rec.sign_execution_trace("key")

        rec2 = ExecutionProofRecorder("a", "r")
        t2 = rec2.start_trace()
        rec2.record_execution_trace("e1")
        rec2.sign_execution_trace("key")

        t1.seal()
        t2.seal()

        cmp = rec.compare_proof(t1, t2)
        assert cmp.matches

    def test_compare_proof_mismatch(self) -> None:
        rec = ExecutionProofRecorder("a", "r")
        t1 = rec.start_trace()
        rec.record_execution_trace("e1")
        t1.seal()

        t2 = ExecutionTrace(run_id="r", agent_id="a")
        t2.record_event("different_event")
        t2.seal()

        cmp = rec.compare_proof(t1, t2)
        assert not cmp.matches
        assert cmp.outcome == ProofComparisonOutcome.DIGEST_MISMATCH

    def test_emit_singleton_digest(self) -> None:
        rec = ExecutionProofRecorder("a", "r")
        t = rec.start_trace()
        rec.record_execution_trace("e1")
        t.seal()
        digest = rec.emit_singleton_digest()
        assert isinstance(digest, str)
        assert len(digest) == 64


# ===========================================================================
# G15 — Path Control
# ===========================================================================


class TestExecutionPathController:
    def test_initial_path_a(self) -> None:
        ctrl = ExecutionPathController("a", "r")
        assert ctrl.current_path == ExecutionPath.PATH_A

    def test_route_path(self) -> None:
        ctrl = ExecutionPathController("a", "r")
        ctrl.route_path(ExecutionPath.PATH_B)
        assert ctrl.current_path == ExecutionPath.PATH_B

    def test_force_stall(self) -> None:
        ctrl = ExecutionPathController("a", "r")
        t = ctrl.force_stall(reason="confidence_too_low")
        assert ctrl.current_path == ExecutionPath.PATH_D
        assert ctrl.report.stall_count == 1

    def test_reenter_safety(self) -> None:
        ctrl = ExecutionPathController("a", "r")
        ctrl.reenter_safety()
        assert ctrl.current_path == ExecutionPath.SAFETY_REENTRY
        assert ctrl.report.safety_reentry_count == 1

    def test_vigilance_reroute(self) -> None:
        ctrl = ExecutionPathController("a", "r")
        ctrl.vigilance_reroute(triggered_by="L6")
        assert ctrl.current_path == ExecutionPath.VIGILANCE_REROUTE
        assert ctrl.report.vigilance_reroute_count == 1

    def test_reroute_to_l0(self) -> None:
        ctrl = ExecutionPathController("a", "r")
        t = ctrl.reroute_to_l0("test")
        assert ctrl.current_path == ExecutionPath.VIGILANCE_REROUTE

    def test_path_summary(self) -> None:
        ctrl = ExecutionPathController("a", "r")
        ctrl.force_stall()
        s = ctrl.report.summary
        assert "stall" in s.lower() or "PathControl" in s

    def test_path_visit_counts(self) -> None:
        ctrl = ExecutionPathController("a", "r")
        ctrl.route_path(ExecutionPath.PATH_B)
        ctrl.route_path(ExecutionPath.PATH_B)
        counts = ctrl.report.path_visit_counts()
        assert counts[ExecutionPath.PATH_B.value] == 2


# ===========================================================================
# G16 — Evaluation Spine
# ===========================================================================


class TestEvalSpine:
    def test_score_groundedness(self) -> None:
        spine = EvalSpine("a", "r")
        m = spine.score_groundedness(0.87)
        assert m.metric_name == "groundedness"
        assert m.value == pytest.approx(0.87)

    def test_compute_pk(self) -> None:
        spine = EvalSpine("a", "r")
        m = spine.compute_pk(0.75, k=5)
        assert "P@5" in m.metric_name

    def test_compute_mrr(self) -> None:
        spine = EvalSpine("a", "r")
        m = spine.compute_mrr(0.62)
        assert m.metric_name == "MRR"

    def test_compute_ndcg(self) -> None:
        spine = EvalSpine("a", "r")
        m = spine.compute_ndcg(0.91, k=10)
        assert "NDCG" in m.metric_name

    def test_emit_drift_alert(self) -> None:
        spine = EvalSpine("a", "r")
        alert = spine.emit_drift_alert("groundedness", 0.5, 0.8, threshold=0.05)
        assert isinstance(alert, DriftAlert)
        assert alert.is_critical
        assert len(spine.report.drift_alerts) == 1

    def test_build_dpo_batch(self) -> None:
        spine = EvalSpine("a", "r")
        batch = spine.build_dpo_batch()
        assert isinstance(batch, DPOBatch)
        assert len(spine.report.dpo_batches) == 1

    def test_stage_and_commit_proposal(self) -> None:
        spine = EvalSpine("a", "r")
        batch = spine.build_dpo_batch()
        proposal = spine.stage_proposal(batch, {"layer.weight": 0.001})
        assert proposal.stage == OptimizationStage.PROPOSAL_STAGED
        result = spine.commit_optimization(proposal)
        assert result
        assert proposal.is_committed
        assert spine.report.committed_proposal_count == 1

    def test_reject_proposal(self) -> None:
        spine = EvalSpine("a", "r")
        batch = spine.build_dpo_batch()
        proposal = spine.stage_proposal(batch)
        spine.reject_proposal(proposal, "divergence")
        assert proposal.stage == OptimizationStage.PROPOSAL_REJECTED

    def test_average_metric(self) -> None:
        spine = EvalSpine("a", "r")
        spine.score_groundedness(0.8)
        spine.score_groundedness(0.6)
        avg = spine.report.average_metric("groundedness")
        assert avg == pytest.approx(0.7)

    def test_summary_keys(self) -> None:
        spine = EvalSpine("a", "r")
        spine.score_groundedness(0.9)
        spine.emit_drift_alert("MRR", 0.3, 0.7)
        s = spine.report.summary
        assert "EvalSpine" in s


# ===========================================================================
# Static AST visitors — smoke tests
# ===========================================================================


def _scan_source(source: str) -> list:
    """Run all gap-plane visitors against a code snippet and collect edges."""
    from agentic_core.adg.extraction.static_scanner import (
        _BoundaryVerifierVisitor,
        _CapabilityBudgetVisitor,
        _DeterminismControlVisitor,
        _EvalSpineVisitor,
        _ExecutionProofVisitor,
        _IOInterceptionVisitor,
        _JITContextVisitor,
        _MutationTransportVisitor,
        _PathControlVisitor,
        _SandboxAirlockVisitor,
    )

    tree = ast.parse(textwrap.dedent(source))
    module_name = "ADG::Module::test_module"
    source_file = "test_module.py"
    edges = []
    for VisitorCls in [
        _SandboxAirlockVisitor,
        _CapabilityBudgetVisitor,
        _JITContextVisitor,
        _BoundaryVerifierVisitor,
        _DeterminismControlVisitor,
        _IOInterceptionVisitor,
        _MutationTransportVisitor,
        _ExecutionProofVisitor,
        _PathControlVisitor,
        _EvalSpineVisitor,
    ]:
        v = VisitorCls(module_name, source_file)
        v.visit(tree)
        edges.extend(v.edges)
    return edges


class TestG7SandboxAirlockVisitor:
    def test_detects_sandbox_envelope(self) -> None:
        src = "SandboxEnvelope()"
        edges = _scan_source(src)
        assert any(e.relation_type == "enters_sandbox" for e in edges)

    def test_detects_capability_token(self) -> None:
        src = "CapabilityToken()"
        edges = _scan_source(src)
        assert any(e.relation_type == "issues_capability_token" for e in edges)

    def test_detects_work_contract_method(self) -> None:
        src = "stamp_work_contract(contract)"
        edges = _scan_source(src)
        assert any(e.relation_type == "stamps_work_contract" for e in edges)


class TestG8CapabilityBudgetVisitor:
    def test_detects_tool_budget(self) -> None:
        src = "ToolBudget.default()"
        edges = _scan_source(src)
        assert any(e.relation_type == "grants_resource" for e in edges)

    def test_detects_budget_exceeded_raise(self) -> None:
        src = "raise BudgetExceededError"
        edges = _scan_source(src)
        assert any(e.relation_type == "exceeds_budget" for e in edges)


class TestG9JITContextVisitor:
    def test_detects_jit_context_class(self) -> None:
        src = "JITContext()"
        edges = _scan_source(src)
        assert any(e.relation_type == "pulls_context" for e in edges)

    def test_detects_freeze_method(self) -> None:
        src = "freeze_context(snap)"
        edges = _scan_source(src)
        assert any(e.relation_type == "freezes_context" for e in edges)


class TestG10BoundaryVerifierVisitor:
    def test_detects_boundary_verifier(self) -> None:
        src = "L2BoundaryVerifier('a', 'r')"
        edges = _scan_source(src)
        assert any(e.relation_type == "verifies_boundary" for e in edges)

    def test_detects_chokepoint(self) -> None:
        src = "CapabilityChokepoint('a')"
        edges = _scan_source(src)
        assert any(e.relation_type == "certifies_envelope" for e in edges)


class TestG11DeterminismControlVisitor:
    def test_detects_semantic_clock(self) -> None:
        src = "SemanticClock('run-1')"
        edges = _scan_source(src)
        assert any(e.relation_type == "patches_time" for e in edges)

    def test_detects_replay_guard(self) -> None:
        src = "ReplayGuard('run-1')"
        edges = _scan_source(src)
        assert any(e.relation_type == "guards_replay" for e in edges)

    def test_detects_seed_rng(self) -> None:
        src = "seed_rng(42)"
        edges = _scan_source(src)
        assert any(e.relation_type == "seeds_rng" for e in edges)

    def test_detects_emit_determinism_digest(self) -> None:
        src = "emit_determinism_digest([])"
        edges = _scan_source(src)
        assert any(e.relation_type == "emits_determinism_digest" for e in edges)


class TestG12IOInterceptionVisitor:
    def test_detects_io_interceptor(self) -> None:
        src = "IOInterceptor('a', 'r')"
        edges = _scan_source(src)
        assert any(e.relation_type == "intercepts_io" for e in edges)

    def test_detects_transcript_response(self) -> None:
        src = "transcript_response('https://a.com', 'body')"
        edges = _scan_source(src)
        assert any(e.relation_type == "transcripts_response" for e in edges)

    def test_detects_hard_fail(self) -> None:
        src = "hard_fail_untranscripted('https://bad.com')"
        edges = _scan_source(src)
        assert any(e.relation_type == "hard_fails_untranscripted" for e in edges)


class TestG13MutationTransportVisitor:
    def test_detects_package_diff(self) -> None:
        src = "package_diff(patches)"
        edges = _scan_source(src)
        assert any(e.relation_type == "packages_diff" for e in edges)

    def test_detects_blast_radius(self) -> None:
        src = "validate_blast_radius(packet, 0.5)"
        edges = _scan_source(src)
        assert any(e.relation_type == "validates_blast_radius" for e in edges)

    def test_detects_two_phase_commit(self) -> None:
        src = "TwoPhaseCommit()"
        edges = _scan_source(src)
        assert any(e.relation_type == "commits_mutation" for e in edges)


class TestG14ExecutionProofVisitor:
    def test_detects_execution_trace(self) -> None:
        src = "ExecutionTrace(run_id='r', agent_id='a')"
        edges = _scan_source(src)
        assert any(e.relation_type == "records_execution_trace" for e in edges)

    def test_detects_emit_replay_key(self) -> None:
        src = "emit_replay_key(rng_seed=42)"
        edges = _scan_source(src)
        assert any(e.relation_type == "emits_replay_key" for e in edges)

    def test_detects_compare_proof(self) -> None:
        src = "compare_proof(t1, t2)"
        edges = _scan_source(src)
        assert any(e.relation_type == "compares_proof" for e in edges)


class TestG15PathControlVisitor:
    def test_detects_path_controller(self) -> None:
        src = "ExecutionPathController('a', 'r')"
        edges = _scan_source(src)
        assert any(e.relation_type == "routes_path" for e in edges)

    def test_detects_force_stall(self) -> None:
        src = "force_stall('low_confidence')"
        edges = _scan_source(src)
        assert any(e.relation_type == "forces_stall" for e in edges)

    def test_detects_reenter_safety(self) -> None:
        src = "reenter_safety()"
        edges = _scan_source(src)
        assert any(e.relation_type == "reenters_safety" for e in edges)

    def test_detects_vigilance_reroute(self) -> None:
        src = "vigilance_reroute('L6')"
        edges = _scan_source(src)
        assert any(e.relation_type == "vigilance_reroute" for e in edges)


class TestG16EvalSpineVisitor:
    def test_detects_eval_spine(self) -> None:
        src = "EvalSpine('a', 'r')"
        edges = _scan_source(src)
        assert any(e.relation_type == "scores_groundedness" for e in edges)

    def test_detects_dpo_batch(self) -> None:
        src = "DPOBatchBuilder()"
        edges = _scan_source(src)
        assert any(e.relation_type == "builds_dpo_batch" for e in edges)

    def test_detects_emit_drift_alert(self) -> None:
        src = "emit_drift_alert('MRR', 0.3, 0.7)"
        edges = _scan_source(src)
        assert any(e.relation_type == "emits_drift_alert" for e in edges)

    def test_detects_build_dpo_batch_method(self) -> None:
        src = "build_dpo_batch(pairs)"
        edges = _scan_source(src)
        assert any(e.relation_type == "builds_dpo_batch" for e in edges)

    def test_detects_commit_optimization(self) -> None:
        src = "commit_optimization(proposal)"
        edges = _scan_source(src)
        assert any(e.relation_type == "commits_optimization" for e in edges)


# ===========================================================================
# Schema constants smoke test
# ===========================================================================


class TestSchemaG7G16Constants:
    def test_sandbox_envelope_classes(self) -> None:
        from agentic_core.adg.schema_util import SANDBOX_ENVELOPE_CLASSES

        assert "SandboxEnvelope" in SANDBOX_ENVELOPE_CLASSES

    def test_capability_token_classes(self) -> None:
        from agentic_core.adg.schema_util import CAPABILITY_TOKEN_CLASSES

        assert "CapabilityToken" in CAPABILITY_TOKEN_CLASSES

    def test_tool_budget_classes(self) -> None:
        from agentic_core.adg.schema_util import TOOL_BUDGET_CLASSES

        assert "ToolBudget" in TOOL_BUDGET_CLASSES

    def test_jit_context_classes(self) -> None:
        from agentic_core.adg.schema_util import JIT_CONTEXT_CLASSES

        assert "JITContext" in JIT_CONTEXT_CLASSES

    def test_boundary_verifier_classes(self) -> None:
        from agentic_core.adg.schema_util import BOUNDARY_VERIFIER_CLASSES

        assert "L2BoundaryVerifier" in BOUNDARY_VERIFIER_CLASSES

    def test_semantic_clock_classes(self) -> None:
        from agentic_core.adg.schema_util import SEMANTIC_CLOCK_CLASSES

        assert "SemanticClock" in SEMANTIC_CLOCK_CLASSES

    def test_io_intercept_classes(self) -> None:
        from agentic_core.adg.schema_util import IO_INTERCEPT_CLASSES

        assert "IOInterceptor" in IO_INTERCEPT_CLASSES

    def test_mutation_transport_classes(self) -> None:
        from agentic_core.adg.schema_util import MUTATION_TRANSPORT_CLASSES

        assert "MutationTransport" in MUTATION_TRANSPORT_CLASSES

    def test_execution_trace_classes(self) -> None:
        from agentic_core.adg.schema_util import EXECUTION_TRACE_CLASSES

        assert "ExecutionTrace" in EXECUTION_TRACE_CLASSES

    def test_path_control_classes(self) -> None:
        from agentic_core.adg.schema_util import PATH_CONTROL_CLASSES

        assert "ExecutionPathController" in PATH_CONTROL_CLASSES

    def test_eval_metric_classes(self) -> None:
        from agentic_core.adg.schema_util import EVAL_METRIC_CLASSES

        assert "EvalSpine" in EVAL_METRIC_CLASSES

    def test_dpo_batch_classes(self) -> None:
        from agentic_core.adg.schema_util import DPO_BATCH_CLASSES

        assert "DPOBatchBuilder" in DPO_BATCH_CLASSES

    def test_all_new_relation_types_valid(self) -> None:
        import typing

        from agentic_core.adg.schema_util import RelationType

        args = typing.get_args(RelationType)
        for rel in [
            "stamps_work_contract",
            "issues_capability_token",
            "enters_sandbox",
            "consumes_budget",
            "grants_resource",
            "exceeds_budget",
            "pulls_context",
            "freezes_context",
            "verifies_boundary",
            "certifies_envelope",
            "seeds_rng",
            "patches_time",
            "guards_replay",
            "emits_determinism_digest",
            "intercepts_io",
            "transcripts_response",
            "hard_fails_untranscripted",
            "packages_diff",
            "validates_blast_radius",
            "commits_mutation",
            "records_execution_trace",
            "emits_replay_key",
            "compares_proof",
            "routes_path",
            "forces_stall",
            "reenters_safety",
            "vigilance_reroute",
            "scores_groundedness",
            "emits_drift_alert",
            "builds_dpo_batch",
        ]:
            assert rel in args, f"Missing RelationType: {rel}"

    def test_all_new_edge_kinds_valid(self) -> None:
        import typing

        from agentic_core.adg.schema_util import EdgeKind

        args = typing.get_args(EdgeKind)
        for ek in [
            "sandbox_entry",
            "capability_token_issue",
            "budget_grant",
            "budget_exceeded",
            "context_pull",
            "context_freeze",
            "boundary_accept",
            "boundary_reject",
            "determinism_seed",
            "replay_patch",
            "determinism_digest_emit",
            "io_transcript",
            "io_hard_fail",
            "diff_package",
            "blast_radius_check",
            "two_phase_commit",
            "execution_trace_record",
            "replay_key_emit",
            "proof_comparison",
            "path_route",
            "path_stall",
            "eval_score",
            "drift_alert",
        ]:
            assert ek in args, f"Missing EdgeKind: {ek}"
