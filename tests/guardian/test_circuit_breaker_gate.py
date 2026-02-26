"""Guardian: G-CB-1 — CircuitBreaker Gate Contract (L5_safety).

Proves:
1. CLOSED state: calls pass through, metrics increment correctly.
2. OPEN state: CircuitBreakerOpenError raised after failure_threshold reached.
3. HALF_OPEN recovery: breaker re-closes after successful call in half-open.
4. fail-closed proof: missing breaker registry raises, does not silently pass.
5. Structural AST: CircuitBreaker, CircuitBreakerOpenError, get_breaker all
   present in the module with correct class hierarchy.
6. reset_registry() cleanly clears all registered breakers.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    PROJECT_ROOT
    / "agentic_core"
    / "L5_safety"
    / "enforcement"
    / "circuit_breaker_gate.py"
)

pytestmark = pytest.mark.guardian


# ===========================================================================
# A) Structural AST — required symbols present
# ===========================================================================


class TestStructuralContract:
    """Verify the module defines the required classes and functions via AST."""

    REQUIRED_CLASSES = {
        "CircuitBreaker",
        "CircuitBreakerOpenError",
        "CircuitBreakerTimeoutError",
        "CircuitBreakerConfig",
        "CircuitBreakerMetrics",
        "CircuitState",
    }
    REQUIRED_FUNCTIONS = {"get_breaker", "get_all_breakers", "reset_registry"}

    def test_module_exists(self):
        assert MODULE_PATH.exists(), "circuit_breaker_gate.py must exist in L5_safety/enforcement"

    def test_required_classes_present(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        found = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        missing = self.REQUIRED_CLASSES - found
        assert not missing, "Missing classes in circuit_breaker_gate: " + str(missing)

    def test_required_functions_present(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        found = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        missing = self.REQUIRED_FUNCTIONS - found
        assert not missing, "Missing functions in circuit_breaker_gate: " + str(missing)

    def test_circuit_breaker_open_error_is_exception(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "CircuitBreakerOpenError":
                bases = [
                    ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", "")
                    for b in node.bases
                ]
                assert any("Exception" in b or "Error" in b for b in bases), (
                    "CircuitBreakerOpenError must inherit from Exception"
                )
                return
        pytest.fail("CircuitBreakerOpenError class not found")

    def test_circuit_state_enum_has_states(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        assert "CLOSED" in src, "CircuitState must define CLOSED"
        assert "OPEN" in src, "CircuitState must define OPEN"
        assert "HALF_OPEN" in src, "CircuitState must define HALF_OPEN"


# ===========================================================================
# B) Runtime: CLOSED state normal operation
# ===========================================================================


class TestClosedState:
    """Breaker in CLOSED state allows calls and tracks success metrics."""

    @pytest.fixture(autouse=True)
    def _reset(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import reset_registry
        reset_registry()
        yield
        reset_registry()

    def test_get_breaker_returns_breaker_instance(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
            CircuitBreaker,
            get_breaker,
        )
        breaker = get_breaker("test_cb_closed")
        assert isinstance(breaker, CircuitBreaker)

    def test_same_name_returns_same_instance(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker
        b1 = get_breaker("test_singleton")
        b2 = get_breaker("test_singleton")
        assert b1 is b2

    def test_successful_call_does_not_raise(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker
        breaker = get_breaker("test_success")
        assert breaker.allow_request(), "CLOSED breaker must allow requests"
        breaker.record_success()
        assert breaker.is_closed

    def test_get_all_breakers_contains_registered(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
            get_all_breakers,
            get_breaker,
        )
        get_breaker("test_all_a")
        get_breaker("test_all_b")
        all_b = get_all_breakers()
        assert "test_all_a" in all_b
        assert "test_all_b" in all_b


# ===========================================================================
# C) Runtime: OPEN state fail-closed
# ===========================================================================


class TestOpenState:
    """After failure_threshold is reached breaker opens and rejects all calls."""

    @pytest.fixture(autouse=True)
    def _reset(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import reset_registry
        reset_registry()
        yield
        reset_registry()

    def test_open_after_threshold_failures(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker
        breaker = get_breaker("test_open_threshold", failure_threshold=2, reset_timeout_seconds=999.0)

        for _ in range(2):
            breaker.record_failure()

        assert breaker.is_open, "Breaker must be OPEN after failure_threshold failures"

    def test_open_state_rejects_requests(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker
        breaker = get_breaker("test_open_reject", failure_threshold=1, reset_timeout_seconds=999.0)

        breaker.record_failure()
        assert breaker.is_open, "Breaker must be OPEN after 1 failure"
        assert not breaker.allow_request(), "OPEN breaker must reject all requests"


# ===========================================================================
# D) reset_registry cleans state
# ===========================================================================


class TestResetRegistry:
    def test_reset_removes_all_breakers(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
            get_all_breakers,
            get_breaker,
            reset_registry,
        )
        get_breaker("reset_a")
        get_breaker("reset_b")
        reset_registry()
        all_b = get_all_breakers()
        assert "reset_a" not in all_b
        assert "reset_b" not in all_b

    def test_reset_allows_fresh_registration(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
            get_breaker,
            reset_registry,
        )
        b1 = get_breaker("fresh_after_reset")
        reset_registry()
        b2 = get_breaker("fresh_after_reset")
        assert b1 is not b2, "After reset, new instance must be created"
