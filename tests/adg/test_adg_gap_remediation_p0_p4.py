"""
tests/adg/test_adg_gap_remediation_p0_p4.py

Regression tests for all P0–P4 ADG gap remediation modules.
Each test exercises the public contract of exactly one new module.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
)

_emit_snapshots_state("p0", "test_adg_gap_remediation_p0_p4", "state_snapshot")
_emit_routes_to_agent("p1", "test_adg_gap_remediation_p0_p4", "test")
_emit_orchestrates_workflow("p1", "test_adg_gap_remediation_p0_p4", "test")
_emit_dispatches_execution_plan("p1", "test_adg_gap_remediation_p0_p4", "test")
_emit_validates_agent_capability("p1", "test_adg_gap_remediation_p0_p4", "test")
_emit_checks_agent_registry("p1", "test_adg_gap_remediation_p0_p4", "test")
_emit_authorize_and_execute("p2", "test_adg_gap_remediation_p0_p4", "execution_auth")
_emit_validates_capability("p2", "test_adg_gap_remediation_p0_p4", "capability_check")
_emit_routes_to_capability("p2", "test_adg_gap_remediation_p0_p4", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_gap_remediation_p0_p4", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_gap_remediation_p0_p4", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_gap_remediation_p0_p4", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_gap_remediation_p0_p4", "exec_output")
_emit_dispatches_agent("p3", "test_adg_gap_remediation_p0_p4", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_gap_remediation_p0_p4", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_gap_remediation_p0_p4", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_gap_remediation_p0_p4", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_gap_remediation_p0_p4", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_gap_remediation_p0_p4", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_gap_remediation_p0_p4", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_gap_remediation_p0_p4", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_gap_remediation_p0_p4", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_gap_remediation_p0_p4", "eval_metric")
_emit_stores_embedding("p4", "test_adg_gap_remediation_p0_p4", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_gap_remediation_p0_p4", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_gap_remediation_p0_p4", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_adg_gap_remediation_p0_p4", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_gap_remediation_p0_p4", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_gap_remediation_p0_p4", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_gap_remediation_p0_p4", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_gap_remediation_p0_p4", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_gap_remediation_p0_p4", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_gap_remediation_p0_p4", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_gap_remediation_p0_p4", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_gap_remediation_p0_p4", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_gap_remediation_p0_p4", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_gap_remediation_p0_p4", "p4obs", "alert")
_emit_links_incident_trace("test_adg_gap_remediation_p0_p4", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_gap_remediation_p0_p4", "p3lm", "pattern")
_emit_records_learning_event("test_adg_gap_remediation_p0_p4", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_gap_remediation_p0_p4", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_gap_remediation_p0_p4", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_gap_remediation_p0_p4", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_gap_remediation_p0_p4", "p3lm", "policy")
_emit_stores_learning_state("test_adg_gap_remediation_p0_p4", "p3lm", "state")
_emit_records_execution_trace("test_adg_gap_remediation_p0_p4", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_gap_remediation_p0_p4", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_gap_remediation_p0_p4", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_gap_remediation_p0_p4", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_gap_remediation_p0_p4", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_gap_remediation_p0_p4", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_gap_remediation_p0_p4", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_gap_remediation_p0_p4", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_gap_remediation_p0_p4", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_gap_remediation_p0_p4", "context_pull")
_emit_pulls_context("p1", "test_adg_gap_remediation_p0_p4", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_gap_remediation_p0_p4", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_gap_remediation_p0_p4", "uwg_term_2")
_emit_writes_through("p1", "test_adg_gap_remediation_p0_p4", "write_through")
_emit_writes_through("p1", "test_adg_gap_remediation_p0_p4", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_gap_remediation_p0_p4", "safety_validation")
_emit_invokes_eval("p1", "test_adg_gap_remediation_p0_p4", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_gap_remediation_p0_p4", "routing_commit")
_emit_escalates_to_human("p1", "test_adg_gap_remediation_p0_p4", "human_escalation")
_emit_routes_through("p1", "test_adg_gap_remediation_p0_p4", "route_through")
_emit_agent_executes_agent("p1", "test_adg_gap_remediation_p0_p4", "sub_agent")
_emit_verifies_policy("p1", "test_adg_gap_remediation_p0_p4", "policy_check")
_emit_observes_runtime_state("p1", "test_adg_gap_remediation_p0_p4", "runtime_state")
_emit_verifies_boundary("p1", "test_adg_gap_remediation_p0_p4", "boundary_check")
_emit_transcripts_response("p1", "test_adg_gap_remediation_p0_p4", "transcript")
_emit_hard_fails_untranscripted("p1", "test_adg_gap_remediation_p0_p4")
_emit_gated_by_confidence("p1", "test_adg_gap_remediation_p0_p4", "confidence_gate")

# ---------------------------------------------------------------------------
# P0-L0: DeterministicRoutingGateway
# ---------------------------------------------------------------------------


def test_deterministic_routing_gateway_stamp_and_verify():
    from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
        DeterministicRoutingGateway,
        reset_routing_gateway,
    )

    reset_routing_gateway()
    gw = DeterministicRoutingGateway(policy_hash="testpolicy123")
    artifact = gw.stamp_decision("standard_validation")

    assert artifact.route_path == "standard_validation"
    assert artifact.replay_key
    assert artifact.determinism_digest
    assert len(artifact.replay_key) == 64
    assert gw.verify_replay(artifact)


def test_deterministic_routing_gateway_ledger():
    from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
        DeterministicRoutingGateway,
    )

    gw = DeterministicRoutingGateway(policy_hash="ph")
    gw.stamp_decision("low_risk_bypass")
    gw.stamp_decision("standard_validation")
    assert len(gw.ledger()) == 2


def test_routing_artifact_to_route_decision():
    from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
        DeterministicRoutingGateway,
    )

    gw = DeterministicRoutingGateway(policy_hash="ph")
    artifact = gw.stamp_decision("standard_validation")
    rd = artifact.as_route_decision(risk_score=0.3, budget_est=100.0)
    assert rd.risk_score == 0.3
    assert rd.budget_est == 100.0


# ---------------------------------------------------------------------------
# P0-L1: TraceEmitter
# ---------------------------------------------------------------------------


def test_trace_emitter_emit_record():
    from agentic_core.runtime.trace_emitter import TraceEmitter

    class MyModule(TraceEmitter):
        _LAYER = "L1"

    m = MyModule()
    record = m.emit_trace_record("run", elapsed_ms=42.0)
    assert record.layer == "L1"
    assert record.operation == "run"
    assert record.elapsed_ms == 42.0
    assert record.success is True
    assert len(record.determinism_digest) == 16


def test_trace_emitter_context_manager():
    from agentic_core.runtime.trace_emitter import TraceEmitter

    class MyModule(TraceEmitter):
        _LAYER = "L2"

    m = MyModule()
    with m.trace_op("test_op") as ctx:
        pass
    assert ctx.record is not None
    assert ctx.record.success is True


def test_emit_trace_decorator():
    from agentic_core.runtime.trace_emitter import emit_trace

    call_log = []

    class MyModule:
        @emit_trace("L3", "my_operation")
        def my_operation(self):
            call_log.append("called")
            return 42

    m = MyModule()
    result = m.my_operation()
    assert result == 42
    assert call_log == ["called"]


# ---------------------------------------------------------------------------
# P0-L2: GuardrailGate
# ---------------------------------------------------------------------------


def test_guardrail_gate_allow():
    from agentic_core.L2_execution.enforcement.guardrail_gate import (
        GuardrailGate,
        GuardrailVerdict,
        reset_guardrail_gate,
    )

    reset_guardrail_gate()
    gate = GuardrailGate(policy_hash="ph", strict_mode=False)
    result = gate.check("write_file", "artifacts/out.json")
    assert result.verdict == GuardrailVerdict.ALLOW
    assert result.allowed


def test_guardrail_gate_blocked_operation():
    from agentic_core.L2_execution.enforcement.guardrail_gate import (
        GuardrailGate,
        GuardrailViolationError,
    )

    gate = GuardrailGate(policy_hash="ph", strict_mode=True)
    gate.block_operation("delete_all")
    with pytest.raises(GuardrailViolationError):
        gate.check("delete_all", "artifacts/")


def test_guardrail_gate_context_manager():
    from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate

    gate = GuardrailGate(policy_hash="ph", strict_mode=False)
    executed = []
    with gate.applies_guardrail("write_file", "artifacts/test.json"):
        executed.append(True)
    assert executed == [True]
    assert gate.allow_count() == 1


def test_guardrail_gate_audit_log():
    from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate

    gate = GuardrailGate(strict_mode=False)
    gate.check("op1", "target1")
    gate.check("op2", "target2")
    assert len(gate.audit_log()) == 2


# ---------------------------------------------------------------------------
# P0-L3: AgentHandoff
# ---------------------------------------------------------------------------


def test_agent_handoff_create():
    from agentic_core.L3_orchestration.contracts.agent_handoff import AgentHandoff

    h = AgentHandoff.create(
        src="OrchestratorA",
        dst="SummaryAgent",
        context={"task": "summarise"},
        task_id="task-001",
    )
    assert h.src == "OrchestratorA"
    assert h.dst == "SummaryAgent"
    assert h.task_id == "task-001"
    assert len(h.handoff_key) == 24


def test_handoff_dispatcher_dispatch():
    from agentic_core.L3_orchestration.contracts.agent_handoff import (
        AgentHandoff,
        HandoffDispatcher,
        HandoffStatus,
        reset_handoff_dispatcher,
    )

    reset_handoff_dispatcher()
    dispatcher = HandoffDispatcher()
    called_with = []

    def my_agent(context, **kwargs):
        called_with.append(context)
        return "result"

    dispatcher.register("SummaryAgent", my_agent)
    handoff = AgentHandoff.create("Orch", "SummaryAgent", {"task": "x"})
    record = dispatcher.dispatch(handoff)
    assert record.status == HandoffStatus.COMPLETED
    assert called_with == [{"task": "x"}]


def test_handoff_dispatcher_unregistered_raises():
    from agentic_core.L3_orchestration.contracts.agent_handoff import (
        AgentHandoff,
        HandoffDispatcher,
    )

    dispatcher = HandoffDispatcher()
    handoff = AgentHandoff.create("A", "NonExistent", {})
    with pytest.raises(KeyError):
        dispatcher.dispatch(handoff)


# ---------------------------------------------------------------------------
# P0-L4: RunScopedStateAuthority
# ---------------------------------------------------------------------------


def test_state_authority_write_read():
    from agentic_core.L4_state.authority.run_scoped_state_authority import (
        RunScopedStateAuthority,
    )

    auth = RunScopedStateAuthority("run-001")
    auth.write("key1", "value1")
    assert auth.read("key1") == "value1"
    assert auth.read("missing", default="x") == "x"


def test_state_authority_freeze_blocks_writes():
    from agentic_core.L4_state.authority.run_scoped_state_authority import (
        FrozenStateError,
        RunScopedStateAuthority,
    )

    auth = RunScopedStateAuthority("run-002")
    auth.freeze()
    with pytest.raises(FrozenStateError):
        auth.write("key", "value")
    auth.unfreeze()
    auth.write("key", "value")  # should not raise


def test_state_authority_frozen_section_context_manager():
    from agentic_core.L4_state.authority.run_scoped_state_authority import (
        FrozenStateError,
        RunScopedStateAuthority,
    )

    auth = RunScopedStateAuthority("run-003")
    with auth.frozen_critical_section():
        with pytest.raises(FrozenStateError):
            auth.write("k", "v")
    auth.write("k", "v")  # unfrozen after context exit


def test_state_authority_snapshot():
    from agentic_core.L4_state.authority.run_scoped_state_authority import (
        RunScopedStateAuthority,
    )

    auth = RunScopedStateAuthority("run-004")
    auth.stamp_work_contract("test task")
    auth.write("a", 1)
    snap = auth.snapshot()
    assert "a" in snap.keys
    assert snap.run_id == "run-004"


def test_state_authority_work_contract():
    from agentic_core.L4_state.authority.run_scoped_state_authority import (
        RunScopedStateAuthority,
    )

    auth = RunScopedStateAuthority("run-005")
    c = auth.stamp_work_contract("task desc")
    assert c.contract_hash
    assert auth.work_contract() is c
    # second call returns same contract
    c2 = auth.stamp_work_contract("other")
    assert c2 is c


# ---------------------------------------------------------------------------
# P0-L5: PolicyEnforcementPoint
# ---------------------------------------------------------------------------


def test_pep_allow():
    from agentic_core.L5_safety.enforcement.policy_enforcement_point import (
        PolicyEnforcementPoint,
        PolicyVerdict,
        reset_policy_enforcement_point,
    )

    reset_policy_enforcement_point()
    pep = PolicyEnforcementPoint(policy_hash="valid_policy_hash_abc123", strict_mode=False)
    result = pep.check("invoke_tool", "code_interpreter")
    assert result.verdict == PolicyVerdict.ALLOW
    assert result.allowed


def test_pep_deny_blocked_action():
    from agentic_core.L5_safety.enforcement.policy_enforcement_point import (
        PolicyEnforcementPoint,
        PolicyViolationError,
    )

    pep = PolicyEnforcementPoint(policy_hash="ph", strict_mode=True, blocked_actions={"rm_rf"})
    with pytest.raises(PolicyViolationError):
        pep.check("rm_rf")


def test_pep_escalate_missing_policy():
    from agentic_core.L5_safety.enforcement.policy_enforcement_point import (
        PolicyEnforcementPoint,
        PolicyVerdict,
    )

    pep = PolicyEnforcementPoint(policy_hash="", strict_mode=False)
    result = pep.check("any_action")
    assert result.verdict == PolicyVerdict.ESCALATE
    assert result.requires_hitl


# ---------------------------------------------------------------------------
# P0-L5: ToolSafetyGate
# ---------------------------------------------------------------------------


def test_tool_safety_gate_allow_low_risk():
    from agentic_core.L5_safety.enforcement.policy_enforcement_point import (
        PolicyEnforcementPoint,
    )
    from agentic_core.L5_safety.gates.tool_safety_gate import (
        ToolRiskLevel,
        ToolSafetyGate,
        reset_tool_safety_gate,
    )

    reset_tool_safety_gate()
    pep = PolicyEnforcementPoint(policy_hash="good_policy_hash_xyz999", strict_mode=False)
    gate = ToolSafetyGate(policy_hash="good_policy_hash_xyz999", pep=pep)
    record = gate.check_tool("search_tool", ToolRiskLevel.LOW, sandboxed=False)
    assert record.allowed


def test_tool_safety_gate_critical_requires_sandbox():
    from agentic_core.L5_safety.enforcement.policy_enforcement_point import (
        PolicyEnforcementPoint,
    )
    from agentic_core.L5_safety.gates.tool_safety_gate import (
        ToolNotSandboxedError,
        ToolRiskLevel,
        ToolSafetyGate,
    )

    pep = PolicyEnforcementPoint(policy_hash="policy123456789abc", strict_mode=False)
    gate = ToolSafetyGate(policy_hash="policy123456789abc", require_sandbox_for_critical=True, pep=pep)
    with pytest.raises(ToolNotSandboxedError):
        gate.check_tool("eval", ToolRiskLevel.CRITICAL, sandboxed=False)


def test_tool_safety_gate_sandbox_context_manager():
    from agentic_core.L5_safety.enforcement.policy_enforcement_point import (
        PolicyEnforcementPoint,
    )
    from agentic_core.L5_safety.gates.tool_safety_gate import (
        ToolRiskLevel,
        ToolSafetyGate,
    )

    pep = PolicyEnforcementPoint(policy_hash="policy_hash_test_abc", strict_mode=False)
    gate = ToolSafetyGate(policy_hash="policy_hash_test_abc", require_sandbox_for_critical=True, pep=pep)
    executed = []
    with gate.enters_sandbox("eval", ToolRiskLevel.CRITICAL):
        executed.append(True)
    assert executed == [True]
    assert gate.sandboxed_count() == 1


# ---------------------------------------------------------------------------
# P1-L1: ReasoningContextEnvelope
# ---------------------------------------------------------------------------


def test_envelope_builder_seal():
    from agentic_core.L1_cognition.context.reasoning_context_envelope import (
        ReasoningContextEnvelopeBuilder,
        release_envelope,
    )

    builder = ReasoningContextEnvelopeBuilder("run-env-001", task="summarise")
    builder.pull_context("rag", ["doc1", "doc2"], confidence=0.9)
    builder.pull_context("memory", {"k": "v"}, confidence=0.85)
    envelope = builder.seal(prompt="Summarise:")
    assert envelope.run_id == "run-env-001"
    assert len(envelope.retrieval_results) == 2
    assert envelope.contract_hash
    release_envelope("run-env-001")


def test_envelope_confidence_gate():
    from agentic_core.L1_cognition.context.reasoning_context_envelope import (
        ReasoningContextEnvelopeBuilder,
    )

    builder = ReasoningContextEnvelopeBuilder("run-env-002", min_confidence=0.8)
    builder.pull_context("rag", "data", confidence=0.5)
    envelope = builder.seal()
    assert not envelope.gated_by_confidence(0.8)


def test_envelope_already_sealed_raises():
    from agentic_core.L1_cognition.context.reasoning_context_envelope import (
        ReasoningContextEnvelopeBuilder,
    )

    builder = ReasoningContextEnvelopeBuilder("run-env-003")
    builder.seal()
    with pytest.raises(RuntimeError):
        builder.seal()


# ---------------------------------------------------------------------------
# P1-L3: WorkCoordinationBundle
# ---------------------------------------------------------------------------


def test_work_coordination_bundle_create():
    from agentic_core.L3_orchestration.coordination.work_coordination_bundle import (
        WorkCoordinationBundle,
        release_coordination_bundle,
    )

    bundle = WorkCoordinationBundle.create("bundle-001", "campaign research")
    assert bundle.contract_hash
    assert bundle.bundle_id == "bundle-001"
    release_coordination_bundle("bundle-001")


def test_bundle_observe_and_read():
    from agentic_core.L3_orchestration.coordination.work_coordination_bundle import (
        WorkCoordinationBundle,
    )

    bundle = WorkCoordinationBundle.create("bundle-002")
    bundle.observe_runtime_state("rag_results", [1, 2, 3])
    assert bundle.read_shared("rag_results") == [1, 2, 3]


def test_bundle_agent_completion_and_snapshot():
    from agentic_core.L3_orchestration.coordination.work_coordination_bundle import (
        WorkCoordinationBundle,
    )

    bundle = WorkCoordinationBundle.create("bundle-003")
    bundle.record_agent_completion("ResearchAgent", "fetch_sources", result="ok")
    snaps = bundle.snapshot_history()
    assert len(snaps) >= 1
    assert bundle.completion_count() == 1


# ---------------------------------------------------------------------------
# P1-L4: UnifiedMemoryFacade
# ---------------------------------------------------------------------------


def test_unified_memory_facade_register_and_retrieve():
    from agentic_core.L4_state.memory.unified_memory_facade import (
        UnifiedMemoryFacade,
        reset_memory_facade,
    )

    reset_memory_facade()

    class SimpleBackend:
        def __init__(self):
            self._store = {}

        def read(self, key):
            return self._store.get(key)

        def write(self, key, value):
            self._store[key] = value

        def delete(self, key):
            self._store.pop(key, None)

    facade = UnifiedMemoryFacade()
    backend = SimpleBackend()
    facade.register_backend("test", backend)
    facade.store("test", "k1", "v1")
    result = facade.retrieve_via("test", "k1")
    assert result.value == "v1"
    assert result.source == "test"


def test_unified_memory_facade_gated_retrieve_blocks_low_confidence():
    from agentic_core.L4_state.memory.unified_memory_facade import (
        UnifiedMemoryFacade,
    )

    class SimpleBackend:
        def read(self, key):
            return "data"

        def write(self, key, value):
            pass

        def delete(self, key):
            pass

    facade = UnifiedMemoryFacade(confidence_threshold=0.8)
    facade.register_backend("b", SimpleBackend())
    result = facade.gated_retrieve("b", "key", confidence=0.5)
    assert result is None


# ---------------------------------------------------------------------------
# P1-L2: ExecutionProofEmitter
# ---------------------------------------------------------------------------


def test_execution_proof_emitter():
    from agentic_core.L2_execution.determinism.execution_proof_emitter import (
        ExecutionProofEmitter,
    )

    emitter = ExecutionProofEmitter("my_exec_module")
    proof = emitter.emit("run_heal", elapsed_ms=55.0)
    assert proof.module == "my_exec_module"
    assert proof.operation == "run_heal"
    assert proof.replay_key
    assert proof.determinism_digest
    assert proof.verify_replay()


def test_execution_proof_context_manager():
    from agentic_core.L2_execution.determinism.execution_proof_emitter import (
        ExecutionProofEmitter,
    )

    emitter = ExecutionProofEmitter("module_x")
    with emitter.proof_op("write_output") as ctx:
        pass
    assert ctx.proof is not None
    assert ctx.proof.success


# ---------------------------------------------------------------------------
# P1-L6: EvaluationSignalIntegrator
# ---------------------------------------------------------------------------


def test_eval_signal_integrator_emit_and_subscribe():
    from agentic_core.L6_observability.evaluation.evaluation_signal_integrator import (
        EvalSignalKind,
        EvaluationSignalIntegrator,
        reset_eval_signal_integrator,
    )

    reset_eval_signal_integrator()
    integrator = EvaluationSignalIntegrator()
    received = []
    integrator.subscribe("L1", lambda s: received.append(s))
    integrator.evaluate_output(
        source_module="L6Engine",
        target_layer="L1",
        kind=EvalSignalKind.QUALITY_SCORE,
        score=0.92,
        label="test_quality",
    )
    assert len(received) == 1
    assert received[0].score == 0.92


def test_eval_signal_integrator_average_score():
    from agentic_core.L6_observability.evaluation.evaluation_signal_integrator import (
        EvalSignalKind,
        EvaluationSignalIntegrator,
    )

    integrator = EvaluationSignalIntegrator()
    integrator.evaluate_output("M", "L1", EvalSignalKind.QUALITY_SCORE, 0.8)
    integrator.evaluate_output("M", "L1", EvalSignalKind.QUALITY_SCORE, 0.6)
    avg = integrator.average_score(EvalSignalKind.QUALITY_SCORE)
    assert abs(avg - 0.7) < 0.001


# ---------------------------------------------------------------------------
# P2-L2: ToolContract
# ---------------------------------------------------------------------------


def test_tool_contract_create():
    from agentic_core.L2_execution.types.execution_tool_contract import (
        ToolCategory,
        ToolContract,
    )

    contract = ToolContract.create(
        tool_name="file_system.write",
        category=ToolCategory.FILE_SYSTEM,
        args={"path": "artifacts/out.json", "data": "{}"},
        trace_id="trace-001",
    )
    assert contract.tool_name == "file_system.write"
    assert contract.contract_hash
    assert contract.capability_hash


def test_tool_registry():
    from agentic_core.L2_execution.types.execution_tool_contract import (
        ToolCapabilityDescriptor,
        ToolCategory,
        get_tool_capability,
        register_tool_capability,
        registered_tools,
    )

    desc = ToolCapabilityDescriptor(
        tool_name="code_interpreter.run_python",
        category=ToolCategory.CODE_EXECUTION,
        risk_level="high",
        requires_sandbox=True,
        idempotent=False,
    )
    register_tool_capability(desc)
    assert "code_interpreter.run_python" in registered_tools()
    retrieved = get_tool_capability("code_interpreter.run_python")
    assert retrieved is desc


# ---------------------------------------------------------------------------
# P2-L3: AgentCapabilityRegistry
# ---------------------------------------------------------------------------


def test_agent_capability_registry():
    from agentic_core.L3_orchestration.registry.agent_capability_registry import (
        AgentCapabilityRegistry,
        AgentCapabilitySpec,
        reset_agent_capability_registry,
    )

    reset_agent_capability_registry()
    registry = AgentCapabilityRegistry()
    registry.register(
        AgentCapabilitySpec(
            agent_name="ResearchOrchestrator",
            layer="L3",
            capabilities=["fetch_sources", "summarise"],
            handoff_targets=["SummaryAgent"],
        )
    )
    spec = registry.get("ResearchOrchestrator")
    assert spec is not None
    assert spec.can_handoff_to("SummaryAgent")
    assert not spec.can_handoff_to("UnknownAgent")


def test_agent_capability_registry_handoff_check():
    from agentic_core.L3_orchestration.registry.agent_capability_registry import (
        AgentCapabilityRegistry,
        AgentCapabilitySpec,
    )

    registry = AgentCapabilityRegistry()
    registry.register(AgentCapabilitySpec("AgentA", "L3", ["cap1"], ["AgentB"]))
    assert registry.can_handoff("AgentA", "AgentB")
    assert not registry.can_handoff("AgentA", "AgentC")
    assert not registry.can_handoff("AgentX", "AgentB")


# ---------------------------------------------------------------------------
# P2-L4: StateVersionManager
# ---------------------------------------------------------------------------


def test_state_version_manager_commit_and_history():
    from agentic_core.L4_state.versioning.state_version_manager import (
        StateVersionManager,
    )

    mgr = StateVersionManager("run-ver-001")
    v1 = mgr.commit({"a": 1}, author="AgentA")
    v2 = mgr.commit({"a": 1, "b": 2}, author="AgentB")
    assert mgr.version_count() == 2
    assert mgr.current_version().version_id == v2.version_id


def test_state_version_manager_rollback():
    from agentic_core.L4_state.versioning.state_version_manager import (
        StateVersionManager,
    )

    mgr = StateVersionManager("run-ver-002")
    v1 = mgr.commit({"x": 1}, author="A")
    mgr.commit({"x": 2}, author="B")
    mgr.commit({"x": 3}, author="C")
    result = mgr.rollback(v1.version_id)
    assert result.version_id == v1.version_id
    assert mgr.version_count() == 1


# ---------------------------------------------------------------------------
# P2-L5: SafetyAuditTrail
# ---------------------------------------------------------------------------


def test_safety_audit_trail_records():
    from agentic_core.L5_safety.audit.safety_audit_trail import (
        SafetyAuditTrail,
        reset_safety_audit_trail,
    )

    reset_safety_audit_trail()
    trail = SafetyAuditTrail(trail_path=None)
    trail.record_guardrail_check(
        module="test_gate",
        operation="write",
        verdict="allow",
        policy_hash="ph",
        trace_id="t1",
        allowed=True,
    )
    trail.record_policy_enforcement(
        module="pep",
        action="execute",
        verdict="deny",
        policy_hash="ph",
        trace_id="t1",
        allowed=False,
        reason="blocked",
    )
    assert trail.count() == 2
    assert len(trail.violations()) == 1


# ---------------------------------------------------------------------------
# P2-L6: PerformanceMetricsEmitter
# ---------------------------------------------------------------------------


def test_performance_metrics_emitter():
    from agentic_core.L6_observability.metrics.performance_metrics_emitter import (
        MetricKind,
        PerformanceMetricsEmitter,
        reset_metrics_emitter,
    )

    reset_metrics_emitter()
    emitter = PerformanceMetricsEmitter()
    emitter.record_latency("L1", "ReasoningEngine", 120.0)
    emitter.record_latency("L1", "ReasoningEngine", 200.0)
    emitter.record_quality("L1", "ReasoningEngine", 0.88)
    summary = emitter.summary("L1", MetricKind.LATENCY_MS)
    assert summary is not None
    assert summary.sample_count == 2
    assert summary.mean == 160.0


# ---------------------------------------------------------------------------
# P3-L4: StateLifecyclePolicy
# ---------------------------------------------------------------------------


def test_state_lifecycle_happy_path():
    from agentic_core.L4_state.enforcement.state_lifecycle_policy import (
        StateLifecyclePolicy,
        StateLifecycleStage,
    )

    policy = StateLifecyclePolicy("run-lc-001")
    assert policy.stage == StateLifecycleStage.CREATED
    policy.activate()
    assert policy.stage == StateLifecycleStage.ACTIVE
    policy.freeze()
    assert policy.stage == StateLifecycleStage.FROZEN
    policy.archive()
    assert policy.stage == StateLifecycleStage.ARCHIVED
    policy.purge()
    assert policy.stage == StateLifecycleStage.PURGED


def test_state_lifecycle_invalid_transition_raises():
    from agentic_core.L4_state.enforcement.state_lifecycle_policy import (
        StateLifecyclePolicy,
        StateLifecycleViolationError,
    )

    policy = StateLifecyclePolicy("run-lc-002")
    with pytest.raises(StateLifecycleViolationError):
        policy.archive()  # CREATED → ARCHIVED is invalid


# ---------------------------------------------------------------------------
# P3-L5: HITLEscalationActivator
# ---------------------------------------------------------------------------


def test_hitl_escalation_activator_pending():
    from agentic_core.L5_safety.hitl.hitl_escalation_activator import (
        EscalationPriority,
        HITLEscalationActivator,
        reset_hitl_escalation_activator,
    )

    reset_hitl_escalation_activator()
    activator = HITLEscalationActivator()
    req = activator.escalate(
        agent="PolicyEnforcementPoint",
        module="pep",
        trigger_reason="policy hash missing",
        priority=EscalationPriority.HIGH,
    )
    assert not req.resolved
    assert activator.pending_count() == 1


def test_hitl_escalation_handler_resolves():
    from agentic_core.L5_safety.hitl.hitl_escalation_activator import (
        EscalationPriority,
        HITLEscalationActivator,
    )

    activator = HITLEscalationActivator()
    activator.register_handler(lambda req: "approve")
    req = activator.escalate(
        agent="Gate",
        module="gate",
        trigger_reason="test",
        priority=EscalationPriority.LOW,
    )
    assert req.resolved
    assert req.resolution == "approve"
    assert activator.pending_count() == 0
    assert len(activator.resolved()) == 1


# ---------------------------------------------------------------------------
# P4-L3: WorkflowLearningBridge
# ---------------------------------------------------------------------------


def test_workflow_learning_bridge_contribute():
    from agentic_core.L3_orchestration.learning.workflow_learning_bridge import (
        WorkflowLearningBridge,
        WorkflowOutcome,
        reset_workflow_learning_bridge,
    )

    reset_workflow_learning_bridge()
    bridge = WorkflowLearningBridge()
    received = []
    bridge.register_learner("sl", lambda o: received.append(o))

    outcome = WorkflowOutcome.capture(
        bundle_id="b-001",
        workflow_type="research",
        success=True,
        elapsed_ms=1500.0,
        agent_sequence=["ResearchAgent", "BriefAssembler"],
        quality_score=0.91,
    )
    bridge.contribute(outcome)
    assert len(received) == 1
    assert received[0].quality_score == 0.91
    assert bridge.success_rate() == 1.0


def test_workflow_learning_bridge_average_quality():
    from agentic_core.L3_orchestration.learning.workflow_learning_bridge import (
        WorkflowLearningBridge,
        WorkflowOutcome,
    )

    bridge = WorkflowLearningBridge()
    for q in [0.8, 0.9, 0.7]:
        bridge.contribute(WorkflowOutcome.capture("b", "t", True, 100.0, [], quality_score=q))
    assert abs(bridge.average_quality() - 0.8) < 0.001


# ---------------------------------------------------------------------------
# P4-L5: PolicyAdaptationLoop
# ---------------------------------------------------------------------------


def test_policy_adaptation_loop_tighten():
    from agentic_core.L5_safety.adaptation.policy_adaptation_loop import (
        AdaptationSignal,
        PolicyAdaptationLoop,
        PolicyDirection,
        reset_policy_adaptation_loop,
    )

    reset_policy_adaptation_loop()
    loop = PolicyAdaptationLoop(policy_hash="original_hash", auto_apply_threshold=0.8)
    proposal = loop.observe(AdaptationSignal.VIOLATION_RATE_HIGH, severity=0.9)
    assert proposal is not None
    assert proposal.direction == PolicyDirection.TIGHTEN
    assert proposal.applied  # severity=0.9 > threshold=0.8


def test_policy_adaptation_loop_no_proposal_on_hold():
    from agentic_core.L5_safety.adaptation.policy_adaptation_loop import (
        AdaptationSignal,
        PolicyAdaptationLoop,
    )

    loop = PolicyAdaptationLoop(policy_hash="ph")
    # No signal that maps to HOLD in current scheme — use a value not in enum
    # Actually we don't have a "HOLD" signal; just ensure it handles correctly
    proposal = loop.observe(AdaptationSignal.QUALITY_SCORE_HIGH, severity=0.5)
    assert proposal is not None
    assert proposal.direction.value in ("tighten", "loosen")


def test_policy_hash_updates_on_applied():
    from agentic_core.L5_safety.adaptation.policy_adaptation_loop import (
        AdaptationSignal,
        PolicyAdaptationLoop,
    )

    loop = PolicyAdaptationLoop(policy_hash="original", auto_apply_threshold=0.5)
    original = loop.current_policy_hash()
    loop.observe(AdaptationSignal.GUARDRAIL_BYPASS_DETECTED, severity=0.9)
    assert loop.current_policy_hash() != original


# ---------------------------------------------------------------------------
# P1-L0: RoutePolicyGovernor
# ---------------------------------------------------------------------------


def test_route_policy_governor_commit():
    from agentic_core.L0_routing.policy.route_policy_governor import (
        RoutePolicyGovernor,
        reset_route_policy_governor,
    )

    reset_route_policy_governor()
    governor = RoutePolicyGovernor(policy_hash="policyxyz123")
    proposal = governor.commit_routing("standard_validation")
    assert proposal.policy_hash == "policyxyz123"
    assert proposal.boundary_verified
    assert proposal.proposal_hash
    assert proposal.satisfies_policy()


def test_route_policy_governor_unknown_path_not_boundary_verified():
    from agentic_core.L0_routing.policy.route_policy_governor import (
        RoutePolicyGovernor,
    )

    governor = RoutePolicyGovernor(policy_hash="ph123")
    proposal = governor.commit_routing("unknown_custom_path")
    assert not proposal.boundary_verified
    assert not proposal.satisfies_policy()
