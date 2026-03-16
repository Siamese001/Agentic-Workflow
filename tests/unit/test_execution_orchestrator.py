"""
Unit tests for L0→L2 Execution Orchestrator - deterministic layer binding.
"""

from unittest.mock import Mock

import pytest

from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
from agentic_core.L0_routing.engines.path_router import Path
from agentic_core.L2_execution.cid_registry import ExecutionCycle
from agentic_core.L5_safety.enforcement.conf_calib_gate import RiskDecision, RiskLevel
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_execution_orchestrator")
_emit_applies_guardrail("p0", "test_execution_orchestrator", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_orchestrator", "policy_binding")
_emit_snapshots_state("p0", "test_execution_orchestrator", "state_snapshot")
emit_replay_key("p0", "test_execution_orchestrator")
emit_determinism_digest("p0", "test_execution_orchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit
class TestExecutionOrchestrator:
    """Test ExecutionOrchestrator deterministic behavior."""

    def setup_method(self):
        """Set up test dependencies."""
        # Create mock dependencies
        self.assembler = Mock()
        self.path_router = Mock()
        self.d0_engine = Mock()
        self.risk_gate = Mock()
        self.cid_registry = Mock()
        self.reentry_loop = Mock()
        self.vigilance_dispatcher = Mock()
        self.meta_bus = Mock()

        # Create orchestrator
        self.orchestrator = ExecutionOrchestrator(
            assembler=self.assembler,
            path_router=self.path_router,
            d0_engine=self.d0_engine,
            risk_gate=self.risk_gate,
            cid_registry=self.cid_registry,
            reentry_loop=self.reentry_loop,
            vigilance_dispatcher=self.vigilance_dispatcher,
            meta_bus=self.meta_bus,
        )

    def test_orchestrator_initialization(self):
        """Test orchestrator stores all dependencies."""
        assert self.orchestrator.assembler is self.assembler
        assert self.orchestrator.path_router is self.path_router
        assert self.orchestrator.d0_engine is self.d0_engine
        assert self.orchestrator.risk_gate is self.risk_gate
        assert self.orchestrator.cid_registry is self.cid_registry
        assert self.orchestrator.reentry_loop is self.reentry_loop
        assert self.orchestrator.vigilance_dispatcher is self.vigilance_dispatcher
        assert self.orchestrator.meta_bus is self.meta_bus

    def test_execute_deterministic_identical_inputs_identical_results(self):
        """Test identical inputs produce identical result dicts."""
        # Setup mocks
        payload = Mock()
        payload.d0_injections = []

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.A
        self.d0_engine.render_d0.return_value = "<D0>content</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(allow=True, level=RiskLevel.LOW, reasons=())

        cycle = ExecutionCycle(cid="execute_A", attempt=1, status="new")
        self.cid_registry.new_cycle.return_value = cycle

        # Execute twice with same input
        intent_input = {"action": "test", "data": "value"}
        result1 = self.orchestrator.execute(intent_input)
        result2 = self.orchestrator.execute(intent_input)

        # Results should be structurally identical
        assert result1["path"] == result2["path"] == Path.A
        assert result1["risk"].allow is True and result2["risk"].allow is True
        assert result1["risk"].level == result2["risk"].level == RiskLevel.LOW
        assert result1["cycle"].attempt == result2["cycle"].attempt == 1

    def test_execute_no_mutation_of_inputs(self):
        """Test execute does not mutate input parameters."""
        intent_input = {"action": "test", "data": "original"}
        original_input = intent_input.copy()

        # Setup mocks
        payload = Mock()
        payload.d0_injections = []

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.B
        self.d0_engine.render_d0.return_value = "<D0>content</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(
            allow=True, level=RiskLevel.MEDIUM, reasons=("SANITIZED_INPUT",)
        )

        cycle = ExecutionCycle(cid="execute_B", attempt=1, status="new")
        self.cid_registry.new_cycle.return_value = cycle

        # Execute
        result = self.orchestrator.execute(intent_input)

        # Verify input unchanged
        assert intent_input == original_input

        # Verify result structure
        assert result["path"] == Path.B
        assert result["risk"].allow is True
        assert result["risk"].level == RiskLevel.MEDIUM
        assert result["cycle"].attempt == 1

    def test_execute_flow_calls_all_components(self):
        """Test execute calls all components in correct order."""
        # Setup mocks
        payload = Mock()
        payload.d0_injections = [Mock()]

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.C
        self.d0_engine.render_d0.return_value = "<D0>rendered</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(
            allow=False, level=RiskLevel.HIGH, reasons=("D0_DENY_EXECUTION",)
        )

        cycle = ExecutionCycle(cid="execute_C", attempt=1, status="new")
        self.cid_registry.new_cycle.return_value = cycle

        # Execute
        intent_input = {"action": "test"}
        result = self.orchestrator.execute(intent_input)

        # Verify all components called
        self.assembler.assemble.assert_called_once_with(intent_input)
        self.path_router.select_path.assert_called_once_with(payload)
        self.d0_engine.render_d0.assert_called_once_with(payload.d0_injections)
        self.risk_gate.evaluate.assert_called_once_with(
            payload_like=payload, d0_injections="<D0>rendered</D0>"
        )
        self.cid_registry.new_cycle.assert_called_once_with("execute_C")

        # Verify result structure
        assert result["path"] == Path.C
        assert result["risk"].allow is False
        assert result["risk"].level == RiskLevel.HIGH
        assert result["state"] == "retry"  # Risk disallowed, should retry
        # Cycle should be advanced since should_retry defaults to True for Mock
        self.reentry_loop.advance.assert_called_once_with(cycle)

    def test_execute_with_different_paths(self):
        """Test execute works correctly with different paths."""
        # Setup for Path.D
        payload = Mock()
        payload.d0_injections = []

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.D
        self.d0_engine.render_d0.return_value = "<D0>path D</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(allow=True, level=RiskLevel.LOW, reasons=())

        cycle = ExecutionCycle(cid="execute_D", attempt=1, status="new")
        self.cid_registry.new_cycle.return_value = cycle

        # Execute
        result = self.orchestrator.execute({"path": "D"})

        # Verify result
        assert result["path"] == Path.D
        assert result["cycle"].cid == "execute_D"

        # Verify CID registry called with correct path
        self.cid_registry.new_cycle.assert_called_once_with("execute_D")

    def test_execute_result_structure_completeness(self):
        """Test execute returns complete result structure."""
        # Setup mocks
        payload = Mock()
        payload.d0_injections = []

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.A
        self.d0_engine.render_d0.return_value = "<D0>test</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(
            allow=True, level=RiskLevel.MEDIUM, reasons=("MANY_CHECK_IDS",)
        )

        cycle = ExecutionCycle(cid="execute_A", attempt=1, status="new")
        self.cid_registry.new_cycle.return_value = cycle

        # Execute
        result = self.orchestrator.execute({"test": "data"})

        # Verify result has all required keys
        assert "path" in result
        assert "risk" in result
        assert "cycle" in result

        # Verify result types
        assert isinstance(result["path"], Path)
        assert isinstance(result["risk"], RiskDecision)
        assert isinstance(result["cycle"], ExecutionCycle)

        # Verify no extra keys
        assert len(result) == 4
        assert "state" in result
        assert result["state"] == "success"

    def test_execute_risk_disallowed_with_retry_available(self):
        """Test execute returns retry state when risk disallowed and retry available."""
        # Setup mocks
        payload = Mock()
        payload.d0_injections = []

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.A
        self.d0_engine.render_d0.return_value = "<D0>content</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(
            allow=False, level=RiskLevel.HIGH, reasons=("D0_DENY_EXECUTION",)
        )

        # Setup cycle and reentry loop for retry
        initial_cycle = ExecutionCycle(cid="execute_A", attempt=1, status="new")
        advanced_cycle = ExecutionCycle(cid="execute_A", attempt=2, status="retry")

        self.cid_registry.new_cycle.return_value = initial_cycle
        self.reentry_loop.should_retry.return_value = True
        self.reentry_loop.advance.return_value = advanced_cycle

        # Execute
        result = self.orchestrator.execute({"test": "data"})

        # Verify retry state
        assert result["path"] == Path.A
        assert result["risk"].allow is False
        assert result["cycle"] == advanced_cycle  # Advanced cycle
        assert result["state"] == "retry"

        # Verify reentry loop called correctly
        self.reentry_loop.should_retry.assert_called_once_with(initial_cycle)
        self.reentry_loop.advance.assert_called_once_with(initial_cycle)

    def test_execute_risk_disallowed_no_retry_available(self):
        """Test execute returns blocked state when risk disallowed and no retry available."""
        # Setup mocks
        payload = Mock()
        payload.d0_injections = []

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.B
        self.d0_engine.render_d0.return_value = "<D0>content</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(
            allow=False, level=RiskLevel.HIGH, reasons=("D0_DENY_EXECUTION",)
        )

        # Setup cycle and reentry loop for no retry
        cycle = ExecutionCycle(cid="execute_B", attempt=3, status="retry")

        self.cid_registry.new_cycle.return_value = cycle
        self.reentry_loop.should_retry.return_value = False

        # Execute
        result = self.orchestrator.execute({"test": "data"})

        # Verify blocked state
        assert result["path"] == Path.B
        assert result["risk"].allow is False
        assert result["cycle"] == cycle  # Original cycle (not advanced)
        assert result["state"] == "blocked"

        # Verify reentry loop called but advance not called
        self.reentry_loop.should_retry.assert_called_once_with(cycle)
        self.reentry_loop.advance.assert_not_called()

    def test_execute_max_attempts_enforced(self):
        """Test that max_attempts is enforced through reentry loop."""
        # Setup mocks
        payload = Mock()
        payload.d0_injections = []

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.C
        self.d0_engine.render_d0.return_value = "<D0>content</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(
            allow=False, level=RiskLevel.HIGH, reasons=("D0_DENY_EXECUTION",)
        )

        # Simulate reaching max_attempts
        cycle_at_max = ExecutionCycle(cid="execute_C", attempt=5, status="retry")

        self.cid_registry.new_cycle.return_value = cycle_at_max
        self.reentry_loop.should_retry.return_value = False  # Max attempts reached

        # Execute
        result = self.orchestrator.execute({"test": "data"})

        # Verify blocked state at max attempts
        assert result["state"] == "blocked"
        assert result["cycle"].attempt == 5
        self.reentry_loop.advance.assert_not_called()

    def test_execute_deterministic_cycle_increments(self):
        """Test cycle increments are deterministic."""
        # Setup mocks
        payload = Mock()
        payload.d0_injections = []

        self.assembler.assemble.return_value = payload
        self.path_router.select_path.return_value = Path.A
        self.d0_engine.render_d0.return_value = "<D0>content</D0>"
        self.risk_gate.evaluate.return_value = RiskDecision(
            allow=False, level=RiskLevel.HIGH, reasons=("D0_DENY_EXECUTION",)
        )

        # Setup deterministic cycle progression
        cycle1 = ExecutionCycle(cid="execute_A", attempt=1, status="new")
        cycle2 = ExecutionCycle(cid="execute_A", attempt=2, status="retry")

        self.cid_registry.new_cycle.return_value = cycle1
        self.reentry_loop.should_retry.return_value = True
        self.reentry_loop.advance.return_value = cycle2

        # Execute twice with same input
        intent_input = {"test": "deterministic"}
        result1 = self.orchestrator.execute(intent_input)
        result2 = self.orchestrator.execute(intent_input)

        # Both should produce same deterministic result
        assert result1["state"] == result2["state"] == "retry"
        assert result1["cycle"].attempt == result2["cycle"].attempt == 2
        assert result1["cycle"].cid == result2["cycle"].cid == "execute_A"
