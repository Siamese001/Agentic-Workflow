"""
Test Base Eval Engine.
"""
import unittest

from apps_eval.engines.base_eval_engine import BaseEvalEngine
from apps_eval.types import EvalRequest, EvalResult


class MockEvalEngine(BaseEvalEngine):
    """Mock implementation for testing."""

    def __init__(self):
        super().__init__()
        self.config = {}

    def _load_config(self) -> None:
        """Load minimal config."""
        self.config = {"test": True}

    def execute(self, request: EvalRequest) -> EvalResult:
        """Execute evaluation - abstract method implementation."""
        return EvalResult(
            trace_id=request.trace_id,
            status="complete",
            overall_score=0.95,
        )

    def run(self, request: EvalRequest) -> EvalResult:
        """Execute evaluation."""
        return self.execute(request)


class TestBaseEvalEngine(unittest.TestCase):
    """Test cases for base eval engine."""

    def setUp(self):
        self.engine = MockEvalEngine()

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        self.assertIsNotNone(self.engine)

    def test_engine_run(self):
        """Test engine run method."""
        request = EvalRequest(trace_id="test-001", suite_ids=["suite-001"])
        result = self.engine.run(request)

        self.assertIsNotNone(result)
        self.assertEqual(result.trace_id, "test-001")
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.overall_score, 0.95)

    def test_eval_request_defaults(self):
        """Test EvalRequest with defaults."""
        request = EvalRequest()
        self.assertEqual(request.suite_ids, [])
        self.assertFalse(request.dry_run)

    def test_eval_result_defaults(self):
        """Test EvalResult with defaults."""
        result = EvalResult()
        self.assertEqual(result.status, "pending")
        self.assertEqual(result.overall_score, 0.0)
        self.assertEqual(result.gate_violations, [])


if __name__ == "__main__":
    unittest.main()
