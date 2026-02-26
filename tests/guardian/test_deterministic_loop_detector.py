"""Guardian: G-DLD-1 — DeterministicLoopDetector Contract (L2_execution).

Proves:
1. Structural AST: DeterministicLoopDetector, ToolBudget, ToolBudgetExceededError present.
2. ToolBudgetExceededError carries reason_code TOOL_BUDGET_EXCEEDED.
3. increment_and_check raises exactly at max_steps (not before, not after grace).
4. Isolation: separate trace_ids do NOT share counters.
5. reset_trace() clears counters for a trace without affecting others.
6. get_current_step_count() returns deterministic step count between calls.
7. Structural: module MUST NOT import wall-clock (time.time / datetime) — step
   budget must be clock-free (determinism contract).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    PROJECT_ROOT / "agentic_core" / "L2_execution" / "enforcement" / "deterministic_loop_detector.py"
)

pytestmark = pytest.mark.guardian


# ===========================================================================
# A) Structural AST contract
# ===========================================================================


class TestStructuralContract:
    REQUIRED_CLASSES = {"DeterministicLoopDetector", "ToolBudget", "ToolBudgetExceededError"}
    REQUIRED_METHODS = {"increment_and_check", "get_current_step_count", "reset_trace"}

    def test_module_exists(self):
        assert MODULE_PATH.exists(), "deterministic_loop_detector.py must exist in L2_execution/enforcement"

    def test_required_classes_present(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        found = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        missing = self.REQUIRED_CLASSES - found
        assert not missing, "Missing classes: " + str(missing)

    def test_required_methods_on_detector(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        detector_cls = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DeterministicLoopDetector":
                detector_cls = node
                break
        assert detector_cls is not None, "DeterministicLoopDetector class not found"
        method_names = {n.name for n in detector_cls.body if isinstance(n, ast.FunctionDef)}
        missing = self.REQUIRED_METHODS - method_names
        assert not missing, "Missing methods on DeterministicLoopDetector: " + str(missing)

    def test_tool_budget_exceeded_error_is_exception(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ToolBudgetExceededError":
                bases = [
                    ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", "") for b in node.bases
                ]
                assert any("Exception" in b or "Error" in b for b in bases), (
                    "ToolBudgetExceededError must inherit from Exception"
                )
                return
        pytest.fail("ToolBudgetExceededError not found")

    def test_no_wall_clock_imports(self):
        """Determinism contract: step budget must be clock-free."""
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        forbidden = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("time", "datetime"):
                        forbidden.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module in ("time", "datetime"):
                    forbidden.add(node.module)
        assert not forbidden, (
            "DeterministicLoopDetector must NOT import wall-clock modules "
            + str(forbidden)
            + " — step budget must be deterministic"
        )


# ===========================================================================
# B) ToolBudgetExceededError carries required fields
# ===========================================================================


class TestToolBudgetExceededError:
    def test_error_has_reason_code(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            ToolBudgetExceededError,
        )

        exc = ToolBudgetExceededError(tool_name="my_tool", budget=5)
        assert exc.reason_code == "TOOL_BUDGET_EXCEEDED"

    def test_error_carries_tool_name_and_budget(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            ToolBudgetExceededError,
        )

        exc = ToolBudgetExceededError(tool_name="analyze", budget=10)
        assert exc.tool_name == "analyze"
        assert exc.budget == 10

    def test_error_message_contains_tool_name(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            ToolBudgetExceededError,
        )

        exc = ToolBudgetExceededError(tool_name="crawl_tool", budget=3)
        assert "crawl_tool" in str(exc)


# ===========================================================================
# C) increment_and_check: raises exactly at max_steps
# ===========================================================================


class TestIncrementAndCheck:
    @pytest.fixture
    def detector(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
        )

        return DeterministicLoopDetector()

    @pytest.fixture
    def budget_3(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import ToolBudget

        return ToolBudget(max_steps=3)

    def test_allows_calls_up_to_budget_minus_one(self, detector, budget_3):
        for i in range(3):
            detector.increment_and_check("trace-a", "tool_x", budget_3)

    def test_raises_exactly_at_max_steps(self, detector, budget_3):
        for _ in range(3):
            detector.increment_and_check("trace-b", "tool_y", budget_3)
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            ToolBudgetExceededError,
        )

        with pytest.raises(ToolBudgetExceededError):
            detector.increment_and_check("trace-b", "tool_y", budget_3)

    def test_step_count_matches_increments(self, detector, budget_3):
        for i in range(2):
            detector.increment_and_check("trace-c", "tool_z", budget_3)
        assert detector.get_current_step_count("trace-c", "tool_z") == 2


# ===========================================================================
# D) Trace isolation — separate trace_ids do NOT share counters
# ===========================================================================


class TestTraceIsolation:
    def test_separate_traces_independent(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
            ToolBudget,
            ToolBudgetExceededError,
        )

        detector = DeterministicLoopDetector()
        budget = ToolBudget(max_steps=2)

        detector.increment_and_check("trace-alpha", "tool", budget)
        detector.increment_and_check("trace-alpha", "tool", budget)
        # trace-alpha at budget; trace-beta starts fresh
        detector.increment_and_check("trace-beta", "tool", budget)
        # trace-alpha must now raise
        with pytest.raises(ToolBudgetExceededError):
            detector.increment_and_check("trace-alpha", "tool", budget)
        # trace-beta still has one step left
        detector.increment_and_check("trace-beta", "tool", budget)

    def test_unrelated_tool_names_independent(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
            ToolBudget,
            ToolBudgetExceededError,
        )

        detector = DeterministicLoopDetector()
        budget = ToolBudget(max_steps=1)

        detector.increment_and_check("t1", "tool_a", budget)
        with pytest.raises(ToolBudgetExceededError):
            detector.increment_and_check("t1", "tool_a", budget)
        # tool_b on same trace is unaffected
        detector.increment_and_check("t1", "tool_b", budget)


# ===========================================================================
# E) reset_trace() clears without affecting other traces
# ===========================================================================


class TestResetTrace:
    def test_reset_clears_counts(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
            ToolBudget,
        )

        detector = DeterministicLoopDetector()
        budget = ToolBudget(max_steps=5)

        detector.increment_and_check("trace-r", "tool", budget)
        detector.increment_and_check("trace-r", "tool", budget)
        assert detector.get_current_step_count("trace-r", "tool") == 2

        detector.reset_trace("trace-r")
        assert detector.get_current_step_count("trace-r", "tool") == 0

    def test_reset_does_not_affect_other_traces(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
            ToolBudget,
        )

        detector = DeterministicLoopDetector()
        budget = ToolBudget(max_steps=5)

        detector.increment_and_check("trace-keep", "tool", budget)
        detector.increment_and_check("trace-keep", "tool", budget)
        detector.increment_and_check("trace-drop", "tool", budget)

        detector.reset_trace("trace-drop")

        assert detector.get_current_step_count("trace-keep", "tool") == 2
        assert detector.get_current_step_count("trace-drop", "tool") == 0
