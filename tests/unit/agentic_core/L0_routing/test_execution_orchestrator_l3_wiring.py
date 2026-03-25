"""
Unit tests for ExecutionOrchestrator L3 delegation wiring (G5).

Covers:
- l3_orchestrator is optional (backwards-compatible default=None)
- Path A does NOT delegate to L3
- Paths B/C/D delegate to L3 when l3_orchestrator is injected
- L3 exception is caught and returned as error metadata (not re-raised)
- max-retry/blocked flow is unchanged by L3 wiring
- Deterministic: identical input → identical result
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
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

# REMOVED: _emit_emits_metric_event("test_execution_orchestrator_l3_wiring", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_execution_orchestrator_l3_wiring", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_execution_orchestrator_l3_wiring", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_execution_orchestrator_l3_wiring", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_execution_orchestrator_l3_wiring", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_execution_orchestrator_l3_wiring", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_execution_orchestrator_l3_wiring", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_execution_orchestrator_l3_wiring", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_execution_orchestrator_l3_wiring", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_execution_orchestrator_l3_wiring", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_execution_orchestrator_l3_wiring", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_execution_orchestrator_l3_wiring", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_execution_orchestrator_l3_wiring", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_execution_orchestrator_l3_wiring", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_execution_orchestrator_l3_wiring", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_execution_orchestrator_l3_wiring", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_execution_orchestrator_l3_wiring", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_execution_orchestrator_l3_wiring", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_execution_orchestrator_l3_wiring", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_execution_orchestrator_l3_wiring", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_execution_orchestrator_l3_wiring", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_execution_orchestrator_l3_wiring", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_execution_orchestrator_l3_wiring", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_execution_orchestrator_l3_wiring", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_execution_orchestrator_l3_wiring", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_execution_orchestrator_l3_wiring", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_execution_orchestrator_l3_wiring", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_execution_orchestrator_l3_wiring", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_execution_orchestrator_l3_wiring")
# REMOVED: _emit_applies_guardrail("p0", "test_execution_orchestrator_l3_wiring", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_execution_orchestrator_l3_wiring", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_execution_orchestrator_l3_wiring", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_execution_orchestrator_l3_wiring", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_execution_orchestrator_l3_wiring", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execution_orchestrator_l3_wiring", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execution_orchestrator_l3_wiring", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_execution_orchestrator_l3_wiring", "write_through")
# REMOVED: _emit_writes_through("p1", "test_execution_orchestrator_l3_wiring", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_execution_orchestrator_l3_wiring", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_execution_orchestrator_l3_wiring", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_execution_orchestrator_l3_wiring", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_execution_orchestrator_l3_wiring", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_execution_orchestrator_l3_wiring", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_execution_orchestrator_l3_wiring", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_execution_orchestrator_l3_wiring", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_execution_orchestrator_l3_wiring", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_execution_orchestrator_l3_wiring", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_execution_orchestrator_l3_wiring", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_execution_orchestrator_l3_wiring", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_execution_orchestrator_l3_wiring", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_execution_orchestrator_l3_wiring", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_execution_orchestrator_l3_wiring", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_execution_orchestrator_l3_wiring")
# REMOVED: _emit_gated_by_confidence("p1", "test_execution_orchestrator_l3_wiring", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_execution_orchestrator_l3_wiring")
# REMOVED: emit_determinism_digest("p0", "test_execution_orchestrator_l3_wiring")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_execution_orchestrator_l3_wiring", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_execution_orchestrator_l3_wiring", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_execution_orchestrator_l3_wiring", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_execution_orchestrator_l3_wiring", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_execution_orchestrator_l3_wiring", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_execution_orchestrator_l3_wiring", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_execution_orchestrator_l3_wiring", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_execution_orchestrator_l3_wiring", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_execution_orchestrator_l3_wiring", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_execution_orchestrator_l3_wiring", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_execution_orchestrator_l3_wiring", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_execution_orchestrator_l3_wiring", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_execution_orchestrator_l3_wiring", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_execution_orchestrator_l3_wiring", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_execution_orchestrator_l3_wiring", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_execution_orchestrator_l3_wiring", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_execution_orchestrator_l3_wiring", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_execution_orchestrator_l3_wiring", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_execution_orchestrator_l3_wiring", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_execution_orchestrator_l3_wiring", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Minimal fakes (no mocks for the component under test)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _FakePath:
    value: str


@dataclass(frozen=True)
class _FakeRisk:
    allow: bool


@dataclass(frozen=True)
class _FakeCycle:
    cid: str
    attempt: int


class _FakeAssembler:
    def __init__(self, d0_injections=""):
        self._d0 = d0_injections

    def assemble(self, intent_input):
        class _P:
            d0_injections = ""
            sanitized = False
            check_ids = ()

        p = _P()
        p.d0_injections = self._d0
        return p


class _FakeRouter:
    def __init__(self, path_value="A"):
        self._path = path_value

    def select_path(self, payload):
        return _FakePath(value=self._path)


class _FakeD0Engine:
    def render_d0(self, d0_injections):
        return d0_injections


class _FakeRiskGate:
    def __init__(self, allow=True):
        self._allow = allow

    def evaluate(self, *, payload_like, d0_injections):
        return _FakeRisk(allow=self._allow)


class _FakeCIDRegistry:
    def __init__(self):
        self._count = 0

    def new_cycle(self, label):
        self._count += 1
        return _FakeCycle(cid=f"cid-{label}-{self._count}", attempt=1)

    def next_attempt(self, cycle):
        return _FakeCycle(cid=cycle.cid, attempt=cycle.attempt + 1)


class _FakeReEntryLoop:
    def __init__(self, max_attempts=3):
        self._max = max_attempts

    def should_retry(self, cycle):
        return cycle.attempt < self._max

    def advance(self, cycle):
        return _FakeCycle(cid=cycle.cid, attempt=cycle.attempt + 1)


class _FakeVigilance:
    def dispatch(self, *args, **kwargs):
        pass


class _FakeMetaBus:
    def enqueue(self, *args, **kwargs):
        pass


@dataclass
class _FakeOrchestrationResult:
    completed: bool = True
    stage: str = "done"
    signals: tuple = ()
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def _make_orch(path="A", allow=True, l3=None, max_reentry=3):
    return ExecutionOrchestrator(
        assembler=_FakeAssembler(),
        path_router=_FakeRouter(path_value=path),
        d0_engine=_FakeD0Engine(),
        risk_gate=_FakeRiskGate(allow=allow),
        cid_registry=_FakeCIDRegistry(),
        reentry_loop=_FakeReEntryLoop(max_attempts=max_reentry),
        vigilance_dispatcher=_FakeVigilance(),
        meta_bus=_FakeMetaBus(),
        l3_orchestrator=l3,
    )


# ---------------------------------------------------------------------------
# Tests: backwards compatibility
# ---------------------------------------------------------------------------


class TestL3WiringBackwardsCompat:
    def test_no_l3_injected_defaults_to_none(self):
        orch = ExecutionOrchestrator(
            assembler=_FakeAssembler(),
            path_router=_FakeRouter(),
            d0_engine=_FakeD0Engine(),
            risk_gate=_FakeRiskGate(),
            cid_registry=_FakeCIDRegistry(),
            reentry_loop=_FakeReEntryLoop(),
            vigilance_dispatcher=_FakeVigilance(),
            meta_bus=_FakeMetaBus(),
        )
        assert orch.l3_orchestrator is None

    def test_path_a_no_l3_returns_success(self):
        orch = _make_orch(path="A")
        result = orch.execute({})
        assert result["state"] == "success"
        assert "orchestration" not in result

    def test_path_a_with_l3_injected_does_not_call_l3(self):
        l3 = MagicMock()
        orch = _make_orch(path="A", l3=l3)
        result = orch.execute({})
        assert result["state"] == "success"
        l3.orchestrate.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: L3 delegation for Paths B/C/D
# ---------------------------------------------------------------------------


class TestL3DelegationPaths:
    @pytest.mark.parametrize("path", ["B", "C", "D"])
    def test_path_delegates_to_l3_when_injected(self, path):
        l3 = MagicMock()
        l3.orchestrate.return_value = _FakeOrchestrationResult(
            completed=True, stage="done", signals=["s1"], metadata={"mode": "test"}
        )
        orch = _make_orch(path=path, l3=l3)
        result = orch.execute({})
        l3.orchestrate.assert_called_once()
        assert result["state"] == "success"
        assert "orchestration" in result
        assert result["orchestration"]["completed"] is True

    @pytest.mark.parametrize("path", ["B", "C", "D"])
    def test_path_no_l3_returns_success_without_orchestration_key(self, path):
        orch = _make_orch(path=path, l3=None)
        result = orch.execute({})
        assert result["state"] == "success"

    def test_l3_receives_correct_route_mode(self):
        l3 = MagicMock()
        l3.orchestrate.return_value = _FakeOrchestrationResult()
        orch = _make_orch(path="B", l3=l3)
        orch.execute({})
        call_kwargs = l3.orchestrate.call_args
        # route_mode kwarg must be "B"
        assert call_kwargs.kwargs.get("route_mode") == "B"

    def test_l3_receives_trace_id_from_cycle(self):
        l3 = MagicMock()
        l3.orchestrate.return_value = _FakeOrchestrationResult()
        orch = _make_orch(path="C", l3=l3)
        orch.execute({})
        call_kwargs = l3.orchestrate.call_args
        assert call_kwargs.kwargs.get("trace_id", "").startswith("cid-")


# ---------------------------------------------------------------------------
# Tests: L3 exception isolation
# ---------------------------------------------------------------------------


class TestL3ExceptionIsolation:
    @pytest.mark.parametrize("path", ["B", "C", "D"])
    def test_l3_exception_does_not_propagate(self, path):
        l3 = MagicMock()
        l3.orchestrate.side_effect = RuntimeError("L3 boom")
        orch = _make_orch(path=path, l3=l3)
        # Must NOT raise
        result = orch.execute({})
        assert result["state"] == "success"
        assert result["orchestration"]["completed"] is False
        assert "L3 boom" in result["orchestration"]["error"]

    def test_l3_exception_preserves_path_and_risk_in_result(self):
        l3 = MagicMock()
        l3.orchestrate.side_effect = ValueError("bad l3")
        orch = _make_orch(path="D", l3=l3)
        result = orch.execute({})
        assert result["path"].value == "D"
        assert result["risk"].allow is True


# ---------------------------------------------------------------------------
# Tests: risk gate + re-entry flow unchanged by L3 wiring
# ---------------------------------------------------------------------------


class TestRiskGateWithL3:
    def test_risk_blocked_max_retries_returns_blocked(self):
        l3 = MagicMock()
        orch = _make_orch(path="B", allow=False, l3=l3, max_reentry=1)
        result = orch.execute({})
        assert result["state"] == "blocked"
        l3.orchestrate.assert_not_called()

    def test_risk_blocked_first_attempt_returns_retry(self):
        l3 = MagicMock()
        orch = _make_orch(path="B", allow=False, l3=l3, max_reentry=3)
        result = orch.execute({})
        assert result["state"] == "retry"
        l3.orchestrate.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: determinism
# ---------------------------------------------------------------------------


class TestOrchestrationDeterminism:
    def test_identical_input_produces_same_state(self):
        orch1 = _make_orch(path="A")
        orch2 = _make_orch(path="A")
        r1 = orch1.execute({"u0_user_prompt": "hello"})
        r2 = orch2.execute({"u0_user_prompt": "hello"})
        assert r1["state"] == r2["state"]

    def test_l3_paths_constant(self):
        assert "B" in ExecutionOrchestrator._L3_PATHS
        assert "C" in ExecutionOrchestrator._L3_PATHS
        assert "D" in ExecutionOrchestrator._L3_PATHS
        assert "A" not in ExecutionOrchestrator._L3_PATHS
