"""Tests for Completion Gates - Phase 1 GraphDB integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from tools.graphdb.agent_integration.validators import CompletionGates, GateResult, GateStatus
from tools.graphdb.agent_integration.decision_engine import ArchitecturalContext, DecisionResult, RiskLevel
from tools.graphdb.agent_integration.guardrails import ArchitecturalGuardrails
from tools.graphdb.agent_integration.cache import QueryCache


class TestCompletionGates:
    """Test suite for CompletionGates."""

    @pytest.fixture
    def mock_decision_engine(self):
        """Create mock decision engine."""
        engine = Mock()
        engine.analyze_action.return_value = DecisionResult(
            approved=True,
            risk_level=RiskLevel.LOW,
            insights=["Test insight"],
            warnings=[],
            alternatives=[],
            architectural_justification="Safe action",
        )
        engine._analyze_blast_radius.return_value = {"total_impact": 0, "risk_level": "low"}
        engine._check_spine_completeness.return_value = {"spine_complete": True}
        return engine

    @pytest.fixture
    def mock_guardrails(self):
        """Create mock guardrails."""
        guardrails = Mock()
        guardrails.validate_action.return_value = Mock()
        guardrails.validate_action.return_value.decision_result.risk_level = RiskLevel.LOW
        guardrails.get_guardrail_statistics.return_value = {
            "total_blocked": 0,
            "total_warned": 0,
            "recent_blocks": [],
            "recent_warnings": [],
            "block_rate": 0.0,
        }
        return guardrails

    @pytest.fixture
    def mock_cache(self):
        """Create mock cache."""
        cache = Mock()
        cache.set.return_value = None
        cache.get.return_value = None
        cache.get_statistics.return_value = {"size": 0, "hit_rate": 0.0, "memory_estimate_bytes": 0}
        cache.cleanup_expired.return_value = 0
        return cache

    @pytest.fixture
    def completion_gates(self, mock_decision_engine, mock_guardrails, mock_cache):
        """Create completion gates with mocked dependencies."""
        return CompletionGates(mock_decision_engine, mock_guardrails, mock_cache)

    def test_initialization(self, mock_decision_engine, mock_guardrails, mock_cache):
        """Test completion gates initialization."""
        gates = CompletionGates(mock_decision_engine, mock_guardrails, mock_cache)

        assert gates.decision_engine == mock_decision_engine
        assert gates.guardrails == mock_guardrails
        assert gates.cache == mock_cache
        assert len(gates.gates) == 6
        assert "query_integration" in gates.gates
        assert "guardrail_effectiveness" in gates.gates
        assert "cache_performance" in gates.gates
        assert "test_coverage" in gates.gates
        assert "architectural_integrity" in gates.gates
        assert "performance_benchmarks" in gates.gates

    def test_run_all_gates_success(self, completion_gates):
        """Test running all gates successfully."""
        with (
            patch.object(completion_gates, "_validate_query_integration") as mock_query,
            patch.object(completion_gates, "_validate_guardrail_effectiveness") as mock_guardrail,
            patch.object(completion_gates, "_validate_cache_performance") as mock_cache,
            patch.object(completion_gates, "_validate_test_coverage") as mock_test,
            patch.object(completion_gates, "_validate_architectural_integrity") as mock_integrity,
            patch.object(completion_gates, "_validate_performance_benchmarks") as mock_perf,
        ):
            # Mock all gates to pass
            for mock_gate in [mock_query, mock_guardrail, mock_cache, mock_test, mock_integrity, mock_perf]:
                mock_gate.return_value = GateResult(
                    gate_name="test",
                    status=GateStatus.PASSED,
                    score=1.0,
                    details={},
                    issues=[],
                    recommendations=[],
                )

            results = completion_gates.run_all_gates()

            assert len(results) == 6
            for gate_name, result in results.items():
                assert result.status == GateStatus.PASSED
                assert result.score == 1.0
                assert result.execution_time_seconds >= 0

    def test_run_all_gates_with_failure(self, completion_gates):
        """Test running all gates with one failure."""
        with (
            patch.object(completion_gates, "_validate_query_integration") as mock_query,
            patch.object(completion_gates, "_validate_guardrail_effectiveness") as mock_guardrail,
            patch.object(completion_gates, "_validate_cache_performance") as mock_cache,
            patch.object(completion_gates, "_validate_test_coverage") as mock_test,
            patch.object(completion_gates, "_validate_architectural_integrity") as mock_integrity,
            patch.object(completion_gates, "_validate_performance_benchmarks") as mock_perf,
        ):
            # Mock most gates to pass, one to fail
            mock_query.return_value = GateResult(
                gate_name="query_integration",
                status=GateStatus.FAILED,
                score=0.5,
                details={},
                issues=["Test failure"],
                recommendations=["Fix it"],
            )

            for mock_gate in [mock_guardrail, mock_cache, mock_test, mock_integrity, mock_perf]:
                mock_gate.return_value = GateResult(
                    gate_name="test",
                    status=GateStatus.PASSED,
                    score=1.0,
                    details={},
                    issues=[],
                    recommendations=[],
                )

            results = completion_gates.run_all_gates()

            assert len(results) == 6
            assert results["query_integration"].status == GateStatus.FAILED
            assert results["query_integration"].score == 0.5

    def test_run_all_gates_with_exception(self, completion_gates):
        """Test running all gates with an exception."""
        with (
            patch.object(completion_gates, "_validate_query_integration") as mock_query,
            patch.object(completion_gates, "_validate_guardrail_effectiveness") as mock_guardrail,
            patch.object(completion_gates, "_validate_cache_performance") as mock_cache,
            patch.object(completion_gates, "_validate_test_coverage") as mock_test,
            patch.object(completion_gates, "_validate_architectural_integrity") as mock_integrity,
            patch.object(completion_gates, "_validate_performance_benchmarks") as mock_perf,
        ):
            # Mock one gate to raise an exception
            mock_query.side_effect = ValueError("Test error")

            for mock_gate in [mock_guardrail, mock_cache, mock_test, mock_integrity, mock_perf]:
                mock_gate.return_value = GateResult(
                    gate_name="test",
                    status=GateStatus.PASSED,
                    score=1.0,
                    details={},
                    issues=[],
                    recommendations=[],
                )

            results = completion_gates.run_all_gates()

            assert len(results) == 6
            assert results["query_integration"].status == GateStatus.FAILED
            assert results["query_integration"].score == 0.0
            assert "Gate execution failed" in results["query_integration"].issues[0]

    def test_get_overall_status_all_passed(self, completion_gates):
        """Test overall status calculation when all gates passed."""
        results = {
            "gate1": GateResult("gate1", GateStatus.PASSED, 1.0, {}, [], [], 0.0),
            "gate2": GateResult("gate2", GateStatus.PASSED, 0.8, {}, [], [], 0.0),
            "gate3": GateResult("gate3", GateStatus.PASSED, 0.9, {}, [], [], 0.0),
        }

        status, score = completion_gates.get_overall_status(results)

        assert status == GateStatus.PASSED
        assert score == (1.0 + 0.8 + 0.9) / 3

    def test_get_overall_status_with_failure(self, completion_gates):
        """Test overall status calculation with failures."""
        results = {
            "gate1": GateResult("gate1", GateStatus.PASSED, 1.0, {}, [], [], 0.0),
            "gate2": GateResult("gate2", GateStatus.FAILED, 0.5, {}, [], [], 0.0),
            "gate3": GateResult("gate3", GateStatus.PASSED, 0.9, {}, [], [], 0.0),
        }

        status, score = completion_gates.get_overall_status(results)

        assert status == GateStatus.FAILED
        assert score == (1.0 + 0.5 + 0.9) / 3

    def test_get_overall_status_empty(self, completion_gates):
        """Test overall status calculation with empty results."""
        status, score = completion_gates.get_overall_status({})

        assert status == GateStatus.PENDING
        assert score == 0.0

    def test_validate_query_integration_success(self, completion_gates, mock_decision_engine):
        """Test successful query integration validation."""
        result = completion_gates._validate_query_integration()

        assert result.gate_name == "query_integration"
        assert result.status == GateStatus.PASSED
        assert result.score == 1.0
        assert len(result.issues) == 0
        assert result.execution_time_seconds >= 0

    def test_validate_query_integration_failure(self, completion_gates, mock_decision_engine):
        """Test query integration validation with failures."""
        # Mock decision engine to raise exceptions
        mock_decision_engine.analyze_action.side_effect = ValueError("Test error")
        mock_decision_engine._analyze_blast_radius.side_effect = RuntimeError("Blast error")
        mock_decision_engine._check_spine_completeness.side_effect = KeyError("Spine error")

        result = completion_gates._validate_query_integration()

        assert result.status == GateStatus.FAILED
        assert result.score < 1.0
        assert len(result.issues) > 0
        assert len(result.recommendations) > 0

    def test_validate_guardrail_effectiveness_success(self, completion_gates, mock_guardrails):
        """Test successful guardrail effectiveness validation."""
        result = completion_gates._validate_guardrail_effectiveness()

        assert result.gate_name == "guardrail_effectiveness"
        assert result.status == GateStatus.PASSED
        assert result.score == 1.0
        assert len(result.issues) == 0

    def test_validate_cache_performance_success(self, completion_gates, mock_cache):
        """Test successful cache performance validation."""
        result = completion_gates._validate_cache_performance()

        assert result.gate_name == "cache_performance"
        assert result.status == GateStatus.PASSED
        assert result.score == 1.0
        assert len(result.issues) == 0

    def test_validate_cache_performance_slow_performance(self, completion_gates, mock_cache):
        """Test cache performance validation with slow performance."""

        # Mock slow cache operations
        def slow_operation(*args, **kwargs):
            time.sleep(0.02)  # 20ms per operation
            return None

        mock_cache.set.side_effect = slow_operation
        mock_cache.get.side_effect = slow_operation

        result = completion_gates._validate_cache_performance()

        # Should still pass but with lower score due to slow performance
        assert result.score < 1.0
        assert len(result.issues) > 0
        assert any("slow" in issue.lower() for issue in result.issues)

    def test_validate_test_coverage_success(self, completion_gates):
        """Test successful test coverage validation."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.__import__", side_effect=ImportError("No pytest")),
        ):
            result = completion_gates._validate_test_coverage()

            # Should pass even without pytest (just checks file existence)
            assert result.score >= 0.7  # Small deduction for missing pytest

    def test_validate_test_coverage_missing_files(self, completion_gates):
        """Test test coverage validation with missing files."""
        with patch("pathlib.Path.exists", return_value=False):
            result = completion_gates._validate_test_coverage()

            assert result.status == GateStatus.FAILED
            assert result.score < 0.8
            assert len(result.issues) > 0
            assert any("Missing test files" in issue for issue in result.issues)

    def test_validate_architectural_integrity_success(self, completion_gates, mock_decision_engine):
        """Test successful architectural integrity validation."""
        # Mock successful imports
        with patch("builtins.__import__", return_value=Mock()):
            result = completion_gates._validate_architectural_integrity()

        assert result.gate_name == "architectural_integrity"
        assert result.status == GateStatus.PASSED
        assert result.score == 1.0

    def test_validate_performance_benchmarks_success(self, completion_gates, mock_decision_engine):
        """Test successful performance benchmarks validation."""
        # Mock fast operations
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=True,
            risk_level=RiskLevel.LOW,
            insights=[],
            warnings=[],
            alternatives=[],
            architectural_justification="Fast",
        )

        with patch("time.time", side_effect=[0, 0.05, 0.05, 0.08]):  # Fast timing
            result = completion_gates._validate_performance_benchmarks()

        assert result.gate_name == "performance_benchmarks"
        assert result.status == GateStatus.PASSED
        assert result.score == 1.0

    def test_validate_performance_benchmarks_slow(self, completion_gates, mock_decision_engine):
        """Test performance benchmarks validation with slow performance."""
        # Mock slow operations
        mock_decision_engine.analyze_action.return_value = DecisionResult(
            approved=True,
            risk_level=RiskLevel.LOW,
            insights=[],
            warnings=[],
            alternatives=[],
            architectural_justification="Slow",
        )

        with patch("time.time", side_effect=[0, 0.15, 0.15, 0.25]):  # Slow timing
            result = completion_gates._validate_performance_benchmarks()

        assert result.score < 1.0
        assert len(result.issues) > 0
        assert any("slow" in issue.lower() for issue in result.issues)


class TestGateResult:
    """Test suite for GateResult."""

    def test_gate_result_creation(self):
        """Test gate result creation."""
        result = GateResult(
            gate_name="test_gate",
            status=GateStatus.PASSED,
            score=0.85,
            details={"test": "data"},
            issues=["Minor issue"],
            recommendations=["Fix it"],
            execution_time_seconds=1.23,
        )

        assert result.gate_name == "test_gate"
        assert result.status == GateStatus.PASSED
        assert result.score == 0.85
        assert result.details == {"test": "data"}
        assert result.issues == ["Minor issue"]
        assert result.recommendations == ["Fix it"]
        assert result.execution_time_seconds == 1.23


class TestGateStatus:
    """Test suite for GateStatus enum."""

    def test_gate_status_values(self):
        """Test gate status enum values."""
        assert GateStatus.PENDING.value == "pending"
        assert GateStatus.IN_PROGRESS.value == "in_progress"
        assert GateStatus.PASSED.value == "passed"
        assert GateStatus.FAILED.value == "failed"
        assert GateStatus.BLOCKED.value == "blocked"
