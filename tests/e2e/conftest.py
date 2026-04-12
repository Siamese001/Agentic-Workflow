"""Agentic System E2E Test Suite — Full Architecture Coverage v12.

This module provides the comprehensive test infrastructure for validating
the full agentic system across all layers (L0-L6), execution paths (A-D),
bus communications, and sovereignty enforcement.

Test Coverage Matrix:
- Layer Sovereignty: L0-L6 boundary enforcement, gravity rules
- Execution Paths: Path A (read-only), B (policy-check), C (direct), D (HITL)
- Bus Communications: C (control), D (deny), E (escalation), T (telemetry), P (preference), U (updates)
- UWG & Determinism: Universal Write Gateway, replay proofs, digests
- Full Integration: End-to-end workflows with agents, logic, hardening

Reference: docs/reference/agentic_process_mapping_v12.md
"""

from __future__ import annotations

import hashlib
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# =============================================================================
# Test Infrastructure Types
# =============================================================================


class ExecutionPath(Enum):
    """Execution paths per agentic process mapping v12."""

    PATH_A = auto()  # Read-only response
    PATH_B = auto()  # Policy check first
    PATH_C = auto()  # Execute script direct
    PATH_D = auto()  # Human review first (HITL)


class BusType(Enum):
    """System bus types per agentic process mapping v12."""

    BUS_C = "control"  # Real-time reroute (L6 → L0)
    BUS_D = "deny"  # Safety fail → re-entry (L5 → L1)
    BUS_E = "escalation"  # Drift → Path D
    BUS_T = "telemetry"  # Read-only signals
    BUS_P = "preference"  # Eval/DPO signals
    BUS_U = "updates"  # Governed ML commits


class Layer(Enum):
    """System layers per agentic process mapping v12."""

    U0 = "user"  # User input
    L1 = "cognition"  # Reasoning, context
    L0 = "routing"  # Route authority
    L3 = "orchestration"  # Coordination
    L5 = "safety"  # Policy, certification
    L2 = "execution"  # Execute only
    L6 = "observability"  # Verify only
    L4 = "state"  # Store only


@dataclass
class TestExecutionContext:
    """Context for tracking test execution state."""

    trace_id: str
    policy_hash: str
    path: ExecutionPath
    layer_states: dict[Layer, dict[str, Any]] = field(default_factory=dict)
    bus_events: list[tuple[BusType, dict[str, Any]]] = field(default_factory=list)
    mutations: list[dict[str, Any]] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)

    def record_bus_event(self, bus: BusType, payload: dict[str, Any]) -> None:
        """Record a bus communication event."""
        self.bus_events.append((bus, payload))

    def record_mutation(self, layer: Layer, operation: str, details: dict[str, Any]) -> None:
        """Record a mutation attempt."""
        self.mutations.append(
            {
                "layer": layer.value,
                "operation": operation,
                "details": details,
                "timestamp": time.time(),
            }
        )


@dataclass
class RobustnessResult:
    """Result of a robustness test execution."""

    test_name: str
    success: bool
    edge_cases_passed: int
    state_transitions_valid: bool
    determinism_verified: bool
    fail_closed_verified: bool
    side_effects_contained: bool
    errors: list[str] = field(default_factory=list)


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def temp_test_dir(tmp_path: Path) -> Path:
    """Provide isolated temporary directory for test artifacts."""
    test_dir = tmp_path / "agentic_test"
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


@pytest.fixture
def execution_context(temp_test_dir: Path) -> TestExecutionContext:
    """Provide fresh execution context for testing."""
    trace_id = f"e2e-{uuid.uuid4().hex[:12]}"
    policy_hash = f"sha256:{hashlib.sha256(trace_id.encode()).hexdigest()[:16]}"
    return TestExecutionContext(
        trace_id=trace_id,
        policy_hash=policy_hash,
        path=ExecutionPath.PATH_B,  # Default to policy-check path
    )


@pytest.fixture
def mock_layer_boundary_guard() -> MagicMock:
    """Provide mocked layer boundary guard for testing."""
    guard = MagicMock()
    guard.check_import_allowed.return_value = True
    guard.check_mutation_allowed.return_value = True
    guard.check_bus_communication.return_value = True
    return guard


@pytest.fixture
def mock_uwg() -> MagicMock:
    """Provide mocked Universal Write Gateway for testing."""
    uwg = MagicMock()
    uwg.write.return_value = {"status": "success", "digest": "sha256:mock_digest"}
    uwg.validate_mutation.return_value = True
    uwg.get_mutation_chain.return_value = []
    return uwg


@pytest.fixture
def bus_monitor() -> BusCommunicationMonitor:
    """Provide bus communication monitor."""
    return BusCommunicationMonitor()


@pytest.fixture(autouse=True)
def reset_global_state() -> None:
    """Reset all global state before each test."""
    # Reset any singletons or global state
    yield


# =============================================================================
# Test Infrastructure Classes
# =============================================================================


class BusCommunicationMonitor:
    """Monitor and validate bus communications."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def record(self, bus_type: BusType, source: Layer, target: Layer, payload: dict[str, Any]) -> None:
        """Record a bus communication event."""
        with self._lock:
            self.events.append(
                {
                    "bus": bus_type,
                    "source": source,
                    "target": target,
                    "payload": payload,
                    "timestamp": time.time(),
                }
            )

    def get_events_for_bus(self, bus_type: BusType) -> list[dict[str, Any]]:
        """Get all events for a specific bus type."""
        with self._lock:
            return [e for e in self.events if e["bus"] == bus_type]

    def verify_bus_rules(self, bus_type: BusType) -> tuple[bool, list[str]]:
        """Verify bus communication follows architectural rules.

        Rules per v12:
        - BUS C: L6 → L0 (control only, real-time reroute)
        - BUS D: L5 → L1 (deny, safety fail re-entry)
        - BUS E: Any → Escalation (drift → Path D)
        - BUS T: Read-only signals (any → any, no mutation)
        - BUS P: Eval/DPO signals (L6 → Meta-Learning)
        - BUS U: Governed ML commits (Meta-Learning → L5)
        """
        errors = []
        events = self.get_events_for_bus(bus_type)

        for event in events:
            source = event["source"]
            target = event["target"]

            if bus_type == BusType.BUS_C:
                # BUS C: Only L6 → L0
                if source != Layer.L6 or target != Layer.L0:
                    errors.append(f"BUS_C violation: {source.value} → {target.value}")

            elif bus_type == BusType.BUS_D:
                # BUS D: Only L5 → L1
                if source != Layer.L5 or target != Layer.L1:
                    errors.append(f"BUS_D violation: {source.value} → {target.value}")

            elif bus_type == BusType.BUS_T:
                # BUS T: Read-only, any direction allowed but no mutation
                if event["payload"].get("mutates_state", False):
                    errors.append("BUS_T mutation violation: attempted state mutation")

            elif bus_type == BusType.BUS_U:
                # BUS U: Only to L5 (governed commits)
                if target != Layer.L5:
                    errors.append(f"BUS_U violation: target must be L5, got {target.value}")

        return len(errors) == 0, errors

    def assert_no_violations(self) -> None:
        """Assert no bus communication violations occurred."""
        for bus_type in BusType:
            valid, errors = self.verify_bus_rules(bus_type)
            if not valid:
                raise AssertionError(f"Bus {bus_type.value} violations: {errors}")


class LayerBoundaryValidator:
    """Validate layer boundary enforcement (sovereignty rules)."""

    # Layer gravity: lower index = lower layer, can only import from lower indices
    # Order from v12: U0 → L1 → L0 → L3 → L5 → L2 → L6 → L4
    LAYER_ORDER = [Layer.U0, Layer.L1, Layer.L0, Layer.L3, Layer.L5, Layer.L2, Layer.L6, Layer.L4]

    # Hard constraints from v12
    HARD_RULES = {
        Layer.L2: {
            "can_mutate": [Layer.L4],
            "cannot_mutate": [Layer.L5, Layer.L0, Layer.L3, Layer.L6, Layer.L1],
            "description": "Execute only",
        },
        Layer.L4: {
            "can_mutate": [],
            "cannot_mutate": [Layer.L5, Layer.L0, Layer.L2, Layer.L3, Layer.L6, Layer.L1],
            "description": "Store only",
        },
        Layer.L5: {
            "can_mutate": [],
            "cannot_mutate": [Layer.L0, Layer.L2, Layer.L4, Layer.L3, Layer.L6, Layer.L1],
            "description": "Certify only",
        },
        Layer.L6: {
            "can_mutate": [],
            "cannot_mutate": [Layer.L0, Layer.L2, Layer.L4, Layer.L5, Layer.L3, Layer.L1],
            "description": "Observe only",
        },
        Layer.L0: {
            "can_mutate": [],
            "cannot_mutate": [Layer.L5, Layer.L2, Layer.L4, Layer.L3, Layer.L6, Layer.L1],
            "description": "Route only",
        },
        Layer.L3: {
            "can_mutate": [],
            "cannot_mutate": [Layer.L5, Layer.L0, Layer.L2, Layer.L4, Layer.L6, Layer.L1],
            "description": "Orchestrate only",
        },
    }

    @classmethod
    def check_import_allowed(cls, source: Layer, target: Layer) -> tuple[bool, str | None]:
        """Check if import from source to target is allowed (gravity rule)."""
        source_idx = cls.LAYER_ORDER.index(source)
        target_idx = cls.LAYER_ORDER.index(target)

        # Lower layer can import from same or lower index
        if target_idx > source_idx:
            return False, f"Layer gravity violation: {target.value} cannot import from {source.value}"
        return True, None

    @classmethod
    def check_mutation_allowed(cls, source: Layer, target: Layer) -> tuple[bool, str | None]:
        """Check if mutation from source to target is allowed."""
        rules = cls.HARD_RULES.get(source, {})
        cannot = rules.get("cannot_mutate", [])

        if target in cannot:
            return False, f"Sovereignty violation: {source.value} cannot mutate {target.value}"

        return True, None


class DeterminismValidator:
    """Validate determinism proof standards."""

    REQUIRED_DIGEST_COMPONENTS = [
        "registry_digest",
        "agent_inventory_hash",
        "tool_inventory_hash",
        "meta_learning_config_hash",
    ]

    @classmethod
    def validate_digest_chain(cls, mutations: list[dict[str, Any]]) -> tuple[bool, list[str]]:
        """Validate mutation digest chain for replay."""
        errors = []

        if not mutations:
            return True, []

        previous_digest = None
        for i, mutation in enumerate(mutations):
            # Check required fields
            if "digest" not in mutation:
                errors.append(f"Mutation {i}: missing digest")
                continue

            # Check chain linkage
            if previous_digest and mutation.get("previous_digest") != previous_digest:
                errors.append(f"Mutation {i}: digest chain broken")

            previous_digest = mutation["digest"]

        return len(errors) == 0, errors

    @classmethod
    def validate_execution_trace(cls, trace: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate execution trace contains all required determinism components."""
        errors = []

        for component in cls.REQUIRED_DIGEST_COMPONENTS:
            if component not in trace:
                errors.append(f"Missing determinism component: {component}")

        # Validate semantic clock
        if "semantic_clock" not in trace:
            errors.append("Missing semantic_clock (sole time authority)")

        return len(errors) == 0, errors


# =============================================================================
# Test Result Collectors
# =============================================================================


class E2ETestReport:
    """Collect and report E2E test results."""

    def __init__(self) -> None:
        self.results: list[RobustnessResult] = []
        self.start_time = time.time()

    def add_result(self, result: RobustnessResult) -> None:
        """Add a test result."""
        self.results.append(result)

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive test report."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed

        # Categorize by dimension
        edge_cases = sum(r.edge_cases_passed for r in self.results)
        determinism = sum(1 for r in self.results if r.determinism_verified)
        fail_closed = sum(1 for r in self.results if r.fail_closed_verified)
        side_effects = sum(1 for r in self.results if r.side_effects_contained)

        return {
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": passed / total if total > 0 else 0,
                "duration_seconds": time.time() - self.start_time,
            },
            "dimensions": {
                "edge_cases": {"total": edge_cases, "target": total * 3},  # ~3 edge cases per test
                "determinism_verified": {"passed": determinism, "total": total},
                "fail_closed_verified": {"passed": fail_closed, "total": total},
                "side_effects_contained": {"passed": side_effects, "total": total},
            },
            "failed_tests": [
                {"name": r.test_name, "errors": r.errors} for r in self.results if not r.success
            ],
        }


# Global report collector
_e2e_report = E2ETestReport()


def record_test_result(result: RobustnessResult) -> None:
    """Record a test result globally."""
    _e2e_report.add_result(result)


def get_final_report() -> dict[str, Any]:
    """Get final E2E test report."""
    return _e2e_report.generate_report()
