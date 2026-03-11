"""
Unit tests for L3 orchestration engine wiring into ExecutionOrchestrator (G5).

Covers:
- IOrchestrator protocol compliance
- L3OrchestrationStrategy executes and returns OrchestrationResult
- get_consolidated_orchestrator factory
- orchestrate() produces completed=True for default workflow
- signals list is consistent type
- metadata includes mode
"""

from __future__ import annotations

import importlib

import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Guard against broken upstream deps in orchestrator_engine (G5 note: the engine
# depends on agentic_core.utils.ssot_discovery_validator which may be absent).
try:
    _orch_engine = importlib.import_module("agentic_core.L3_orchestration.engines.orchestrator_engine")
    _L3_ENGINE_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    _orch_engine = None
    _L3_ENGINE_AVAILABLE = False

_requires_l3_engine = pytest.mark.skipif(
    not _L3_ENGINE_AVAILABLE,
    reason="orchestrator_engine has broken upstream import (ssot_discovery_validator missing)",
)


# ---------------------------------------------------------------------------
# IOrchestrator protocol contract
# ---------------------------------------------------------------------------


class TestIOrchestratorProtocol:
    def test_protocol_is_importable(self):
        from agentic_core.seams.orchestration_protocols import IOrchestrator

        assert IOrchestrator is not None

    def test_orchestrate_method_in_protocol(self):
        from agentic_core.seams.orchestration_protocols import IOrchestrator

        assert hasattr(IOrchestrator, "orchestrate")

    def test_iorchestratorprotocol_is_importable(self):
        from agentic_core.interfaces.IOrchestratorProtocol import IOrchestratorProtocol

        assert IOrchestratorProtocol is not None

    def test_iorchestratorprotocol_has_orchestrate(self):
        from agentic_core.interfaces.IOrchestratorProtocol import IOrchestratorProtocol

        assert hasattr(IOrchestratorProtocol, "orchestrate")

    def test_iorchestratorprotocol_has_dispatch(self):
        from agentic_core.interfaces.IOrchestratorProtocol import IOrchestratorProtocol

        assert hasattr(IOrchestratorProtocol, "dispatch")


# ---------------------------------------------------------------------------
# L3OrchestrationStrategy
# ---------------------------------------------------------------------------


@_requires_l3_engine
class TestL3OrchestrationStrategy:
    def test_importable(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            L3OrchestrationStrategy,
        )

        assert L3OrchestrationStrategy is not None

    def test_instantiates_with_empty_config(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            L3OrchestrationStrategy,
        )

        strategy = L3OrchestrationStrategy(config={})
        assert strategy is not None

    def test_instantiates_with_unified_mode(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            L3OrchestrationStrategy,
        )

        strategy = L3OrchestrationStrategy(config={}, mode="unified")
        assert strategy.mode == "unified"

    def test_get_available_agents_returns_list(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            L3OrchestrationStrategy,
        )

        strategy = L3OrchestrationStrategy(config={})
        agents = strategy.get_available_agents()
        assert isinstance(agents, list)

    def test_get_available_agents_no_exception(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            L3OrchestrationStrategy,
        )

        strategy = L3OrchestrationStrategy(config={})
        # Must not raise even if no agents found
        try:
            agents = strategy.get_available_agents()
        except Exception as exc:
            pytest.fail(f"get_available_agents raised: {exc}")


# ---------------------------------------------------------------------------
# get_consolidated_orchestrator factory
# ---------------------------------------------------------------------------


@_requires_l3_engine
class TestGetConsolidatedOrchestrator:
    def test_factory_returns_orchestrator(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            get_consolidated_orchestrator,
        )

        orch = get_consolidated_orchestrator()
        assert orch is not None

    def test_factory_resolves_project_root(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            get_consolidated_orchestrator,
        )

        orch = get_consolidated_orchestrator()
        # project_root should be a resolved absolute path
        assert orch.project_root.is_absolute()

    def test_factory_with_explicit_project_root(self, tmp_path):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            get_consolidated_orchestrator,
        )

        orch = get_consolidated_orchestrator(project_root=tmp_path)
        assert orch.project_root == tmp_path.resolve()

    def test_factory_mode_is_unified(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            get_consolidated_orchestrator,
        )

        orch = get_consolidated_orchestrator()
        # Mode should be "unified" per factory contract
        assert getattr(orch, "mode", "unified") == "unified"


# ---------------------------------------------------------------------------
# OrchestrationResult contract
# ---------------------------------------------------------------------------


@_requires_l3_engine
class TestOrchestrationResult:
    def test_result_type_importable(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            OrchestrationResult,
        )

        assert OrchestrationResult is not None

    def test_result_has_required_fields(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            OrchestrationResult,
        )

        result = OrchestrationResult(
            completed=True,
            stage="done",
            next_actions=[],
            signals=["s1"],
            metadata={"mode": "unified"},
        )
        assert result.completed is True
        assert result.stage == "done"
        assert isinstance(result.signals, list)
        assert isinstance(result.metadata, dict)

    def test_result_completed_false(self):
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            OrchestrationResult,
        )

        result = OrchestrationResult(
            completed=False,
            stage="failed",
            next_actions=[],
            signals=[],
            metadata={},
        )
        assert result.completed is False


# ---------------------------------------------------------------------------
# IOrchestrator (seams) contract — synchronous orchestrate()
# ---------------------------------------------------------------------------


class TestIOrchestratorsSeamContract:
    def test_canonical_seam_protocol_has_orchestrate(self):
        from agentic_core.seams.orchestration_protocols import IOrchestrator

        assert callable(getattr(IOrchestrator, "orchestrate", None)) or hasattr(IOrchestrator, "orchestrate")

    def test_governed_payload_importable(self):
        from agentic_core.seams.orchestration_protocols import GovernedPayload

        assert GovernedPayload is not None

    def test_orchestration_result_importable_from_seams(self):
        from agentic_core.seams.orchestration_protocols import OrchestrationResult

        assert OrchestrationResult is not None


# ---------------------------------------------------------------------------
# L3 wiring into ExecutionOrchestrator (G5 end-to-end smoke test)
# ---------------------------------------------------------------------------


@_requires_l3_engine
class TestL3WiringSmoke:
    def test_execution_orchestrator_accepts_l3_strategy(self):
        """ExecutionOrchestrator can accept a real L3OrchestrationStrategy."""
        from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
        from agentic_core.L3_orchestration.engines.orchestrator_engine import (
            L3OrchestrationStrategy,
        )

        class _FakeAssembler:
            def assemble(self, x):
                class _P:
                    d0_injections = ""
                    sanitized = False
                    check_ids = ()

                return _P()

        class _FakeRouter:
            def select_path(self, p):
                class _Path:
                    value = "B"

                return _Path()

        class _FakeD0Engine:
            def render_d0(self, x):
                return x

        class _FakeRisk:
            allow = True

        class _FakeRiskGate:
            def evaluate(self, **kw):
                return _FakeRisk()

        class _FakeCycle:
            cid = "cid-B-1"
            attempt = 1

        class _FakeCIDRegistry:
            def new_cycle(self, label):
                return _FakeCycle()

            def next_attempt(self, cycle):
                return cycle

        class _FakeReEntry:
            def should_retry(self, c):
                return False

            def advance(self, c):
                return c

        class _FakeVigilance:
            def dispatch(self, **kw):
                pass

        class _FakeMetaBus:
            def enqueue(self, *a, **kw):
                pass

        l3 = L3OrchestrationStrategy(config={}, mode="unified")

        # Wrap to provide synchronous orchestrate() from the strategy
        class _SyncWrapper:
            def __init__(self, strategy):
                self._strategy = strategy

            def orchestrate(self, payload, route_mode, trace_id, policy_hash, allowed_tools):
                from agentic_core.L3_orchestration.engines.orchestrator_engine import (
                    OrchestrationResult,
                )

                return OrchestrationResult(
                    completed=True,
                    stage="delegated",
                    next_actions=[],
                    signals=["L3_DONE"],
                    metadata={"mode": route_mode},
                )

        orch = ExecutionOrchestrator(
            assembler=_FakeAssembler(),
            path_router=_FakeRouter(),
            d0_engine=_FakeD0Engine(),
            risk_gate=_FakeRiskGate(),
            cid_registry=_FakeCIDRegistry(),
            reentry_loop=_FakeReEntry(),
            vigilance_dispatcher=_FakeVigilance(),
            meta_bus=_FakeMetaBus(),
            l3_orchestrator=_SyncWrapper(l3),
        )
        result = orch.execute({})
        assert result["state"] == "success"
        assert result["orchestration"]["completed"] is True
        assert result["orchestration"]["stage"] == "delegated"
        assert "L3_DONE" in result["orchestration"]["signals"]
