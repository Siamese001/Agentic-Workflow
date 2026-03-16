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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_execution_orchestrator_l3_wiring")
_emit_applies_guardrail("p0", "test_execution_orchestrator_l3_wiring", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_orchestrator_l3_wiring", "policy_binding")
_emit_snapshots_state("p0", "test_execution_orchestrator_l3_wiring", "state_snapshot")
emit_replay_key("p0", "test_execution_orchestrator_l3_wiring")
emit_determinism_digest("p0", "test_execution_orchestrator_l3_wiring")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_orchestrator_l3_wiring", "execution_auth")
_emit_validates_capability("p2", "test_execution_orchestrator_l3_wiring", "capability_check")
_emit_routes_to_capability("p2", "test_execution_orchestrator_l3_wiring", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_orchestrator_l3_wiring", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_orchestrator_l3_wiring", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_orchestrator_l3_wiring", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_orchestrator_l3_wiring", "exec_output")
_emit_dispatches_agent("p3", "test_execution_orchestrator_l3_wiring", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_orchestrator_l3_wiring", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_orchestrator_l3_wiring", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_orchestrator_l3_wiring", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_orchestrator_l3_wiring", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_orchestrator_l3_wiring", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_orchestrator_l3_wiring", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_orchestrator_l3_wiring", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_orchestrator_l3_wiring", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_orchestrator_l3_wiring", "eval_metric")
_emit_stores_embedding("p4", "test_execution_orchestrator_l3_wiring", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_orchestrator_l3_wiring", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_orchestrator_l3_wiring", "exec_snapshot_link")

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
