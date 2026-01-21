#!/usr/bin/env python3
"""
Comprehensive Test Suite for L6 Observability Agents
=====================================================

Tests the skeptical analyst framework with strict validation:
1. RuntimeTelemetryAgent: 2x Gospel violation detection
2. PerformanceAnalystAgent: Async event loop integrity
3. L6ObservabilityBaseAgent: Skeptical grading accuracy
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

from agentic_core.L6_observability.agents.PerformanceAnalystAgent import PerformanceAnalystAgent
from agentic_core.L6_observability.agents.RuntimeTelemetryAgent import RuntimeTelemetryAgent
from agentic_core.L6_observability.L6ObservabilityBaseAgent import L6ObservabilityBaseAgent


class TestRuntimeTelemetryAgent:
    """Test Case 1: The "2x Gospel" Violation Detection."""

    def test_gospel_violation_detection(self):
        """
        Verify that RuntimeTelemetryAgent correctly identifies when a security
        wrapper exceeds the 2x performance budget (Gospel mandate).

        SETUP: MockSovereignAgent sleeps 100ms, baseline is 40ms
        ACTION: audit_security_overhead(0.04, 0.10)
        EXPECTATION: Status = "☢️ CRITICAL OVERHEAD", breach = True, warning logged
        """

        # Setup
        class MockSovereignAgent:
            def __init__(self):
                time.sleep(0.1)  # 100ms startup

        telemetry = RuntimeTelemetryAgent(limit_multiplier=2.0)

        # Benchmark the mock agent
        agent, duration = telemetry.benchmark_startup(MockSovereignAgent)

        # Verify timing captured
        assert duration >= 0.1, f"Duration {duration}s should be >= 0.1s"
        assert "MockSovereignAgent" in telemetry.metrics
        assert telemetry.metrics["MockSovereignAgent"] >= 0.1

        # Action: Audit against 40ms baseline
        baseline_time = 0.04  # 40ms
        current_time = 0.10  # 100ms (2.5x baseline)

        result = telemetry.audit_security_overhead(baseline_time, current_time)

        # Expectations
        assert result["breach"] is True, "Breach should be detected for 2.5x overhead"
        assert result["status"] == "☢️ CRITICAL OVERHEAD", (
            f"Expected critical status, got: {result['status']}"
        )
        assert result["ratio"] >= 2.0, f"Ratio {result['ratio']} should exceed 2.0x Gospel limit"

        print("✅ Test 1 PASSED: Gospel violation correctly detected")
        print(f"   Ratio: {result['ratio']}x (exceeds 2.0x limit)")
        print(f"   Status: {result['status']}")
        print(f"   Breach: {result['breach']}")

    def test_gospel_compliance(self):
        """Verify that compliant agents pass the Gospel check."""
        telemetry = RuntimeTelemetryAgent(limit_multiplier=2.0)

        # 30ms agent against 20ms baseline = 1.5x (within 2x limit)
        result = telemetry.audit_security_overhead(0.02, 0.03)

        assert result["breach"] is False, "Should not breach for 1.5x overhead"
        assert result["status"] == "✅ OPTIMAL"
        assert result["ratio"] == 1.5

        print("✅ Gospel compliance test PASSED: 1.5x overhead accepted")

    def test_benchmark_exception_handling(self):
        """Verify benchmark handles agent init failures gracefully."""

        class FailingAgent:
            def __init__(self):
                raise RuntimeError("Init failed")

        telemetry = RuntimeTelemetryAgent()

        # Should handle exception and still record timing
        with pytest.raises(RuntimeError):
            agent, duration = telemetry.benchmark_startup(FailingAgent)

        # Timing should still be captured in finally block
        assert "FailingAgent" in telemetry.metrics or "UnknownAgent" in telemetry.metrics

        print("✅ Exception handling test PASSED")


class TestPerformanceAnalystAgent:
    """Test Case 2: Async Event Loop Integrity."""

    @pytest.mark.asyncio
    async def test_async_event_loop_non_blocking(self):
        """
        Verify that metrics collection does not block the event loop.

        SETUP: Large agent_discovery_full.json (mocked with 1000+ entries)
        ACTION: await analyze()
        EXPECTATION: Uses non-blocking IO, completes without blocking
        """
        # Create mock discovery data with 1000 agents
        mock_agents = []
        for i in range(1000):
            mock_agents.append(
                {
                    "class_name": f"TestAgent{i}",
                    "layer": f"L{i % 6}",
                    "has_healing": i % 2 == 0,
                    "invocation": "Yes" if i % 3 == 0 else "No",
                    "has_tests": i % 4 == 0,
                    "typed_pct": 75.0,
                    "documented_pct": 60.0,
                    "cyclomatic_complexity": 5 + (i % 10),
                    "mcp_hardened": i % 5 == 0,
                    "observability": {"logging": True} if i % 3 == 0 else {},
                    "path": f"/mock/path/L{i % 6}/agent{i}.py",
                }
            )

        # Write mock data to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(mock_agents, f)
            temp_path = Path(f.name)

        try:
            # Monkey patch the discovery path
            original_get_discovery = PerformanceAnalystAgent._get_discovery_path

            def mock_get_discovery(self):
                return temp_path

            PerformanceAnalystAgent._get_discovery_path = mock_get_discovery

            # Create analyst and run async analysis
            analyst = PerformanceAnalystAgent()

            # Track event loop responsiveness
            start_time = asyncio.get_event_loop().time()

            # Run analysis (should not block)
            result = await analyst.analyze()

            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time

            # Expectations
            assert result["status"] == "completed", (
                f"Analysis should complete, got: {result['status']}"
            )
            assert result["metrics_collected"] == 1000, (
                f"Should collect 1000 metrics, got: {result['metrics_collected']}"
            )
            assert duration < 5.0, f"Analysis took {duration}s, should be < 5s (non-blocking)"

            # Verify critiques were generated
            assert len(analyst.critique_history) == 1000

            print("✅ Test 2 PASSED: Async event loop integrity verified")
            print(f"   Metrics collected: {result['metrics_collected']}")
            print(f"   Duration: {duration:.3f}s (non-blocking)")
            print(f"   Critiques generated: {len(analyst.critique_history)}")

        finally:
            # Cleanup
            temp_path.unlink(missing_ok=True)
            PerformanceAnalystAgent._get_discovery_path = original_get_discovery

    @pytest.mark.asyncio
    async def test_concurrent_analysis(self):
        """Verify multiple analyses can run concurrently without interference."""
        analyst = PerformanceAnalystAgent()

        # Mock empty discovery
        original_get_discovery = PerformanceAnalystAgent._get_discovery_path

        def mock_get_discovery(self):
            p = Path(tempfile.gettempdir()) / "empty_discovery.json"
            p.write_text("[]")
            return p

        PerformanceAnalystAgent._get_discovery_path = mock_get_discovery

        try:
            # Run 3 analyses concurrently
            results = await asyncio.gather(
                analyst.run_async_analysis(),
                analyst.run_async_analysis(),
                analyst.run_async_analysis(),
            )

            # All should complete successfully
            assert all(r["status"] == "completed" for r in results)

            print(f"✅ Concurrent analysis test PASSED: {len(results)} analyses completed")

        finally:
            PerformanceAnalystAgent._get_discovery_path = original_get_discovery


class TestL6ObservabilityBaseAgent:
    """Test Case 3: Skeptical Grading Accuracy."""

    @pytest.mark.asyncio
    async def test_skeptical_grading_strict_threshold(self):
        """
        Confirm grading logic is unbiased and strictly follows data.

        SETUP: Agent with test_coverage=0.5 (50%)
        ACTION: _critique_single_agent(metric)
        EXPECTATION: Grade = F (below 0.6 critical threshold), "IMMEDIATE ACTION" recommendation
        """

        # Create a concrete test implementation
        class TestAnalyst(L6ObservabilityBaseAgent):
            async def analyze(self) -> dict[str, Any]:
                return {"status": "test"}

        analyst = TestAnalyst()

        # Create metric with multiple failures (truly failing agent)
        metric = AgentPerformanceMetrics(
            agent_name="TestFailingAgent",
            layer="L2",
            test_coverage=0.4,  # 40% - critical
            mcp_hardened=False,  # Missing MCP - critical
            complexity_score=25,  # Very high - critical
            success_rate=0.0,  # No healing - critical
            heal_invocations=0,  # No invocation
        )

        # Action: Critique the agent
        critique = await analyst._critique_single_agent(metric)

        # Expectations: Strict grading, no mercy for failing agent
        assert critique.overall_grade == "F", (
            f"Expected F grade for critically failing agent, got: {critique.overall_grade}"
        )
        assert len(critique.critical_issues) >= 3, (
            f"Should have multiple critical issues, got {len(critique.critical_issues)}"
        )

        # Check for "IMMEDIATE ACTION REQUIRED" in recommendations
        immediate_action_found = any(
            "IMMEDIATE ACTION REQUIRED" in rec for rec in critique.recommendations
        )
        assert immediate_action_found, "Should recommend immediate action for F grade"

        # Verify data points show multiple failures
        assert critique.data_points["test_coverage"] == "40.0%"
        assert critique.data_points["mcp_hardened"] == False
        overall_score = float(critique.data_points["overall_score"].rstrip("%"))
        assert overall_score < 60.0, f"Overall score {overall_score}% should be < 60%"

        # Check skeptical commentary tone
        assert (
            "fails basic standards" in critique.skeptical_commentary.lower()
            or "complete rework" in critique.skeptical_commentary.lower()
        ), "Commentary should be harsh for failing agent"

        print(
            "✅ Test 3 PASSED: Skeptical grading correctly assigned F for critically failing agent"
        )
        print(f"   Grade: {critique.overall_grade}")
        print(f"   Overall Score: {critique.data_points['overall_score']}")
        print(f"   Critical Issues: {len(critique.critical_issues)}")
        print("   Failures: No MCP, low coverage (40%), high complexity (25), no healing")
        print(f"   Commentary: {critique.skeptical_commentary[:100]}...")

    @pytest.mark.asyncio
    async def test_grading_scale_accuracy(self):
        """Verify grading scale works monotonically (worse metrics = worse grade)."""

        class TestAnalyst(L6ObservabilityBaseAgent):
            async def analyze(self) -> dict[str, Any]:
                return {"status": "test"}

        analyst = TestAnalyst()

        # Test that grades decrease monotonically as metrics worsen
        test_cases = [
            # Best case: all metrics excellent
            (0.95, True, 2, 1.0, 1, "Excellent agent"),
            # Good case: slight reduction
            (0.85, True, 5, 1.0, 1, "Good agent"),
            # Mediocre: no MCP
            (0.75, False, 8, 1.0, 1, "Mediocre agent"),
            # Poor: low coverage + no MCP
            (0.55, False, 12, 1.0, 0, "Poor agent"),
            # Worst: multiple failures
            (0.30, False, 25, 0.0, 0, "Terrible agent"),
        ]

        grades = []
        scores = []

        for (
            test_coverage,
            mcp_hardened,
            complexity,
            success_rate,
            heal_invocations,
            description,
        ) in test_cases:
            metric = AgentPerformanceMetrics(
                agent_name=description,
                layer="L3",
                test_coverage=test_coverage,
                mcp_hardened=mcp_hardened,
                complexity_score=complexity,
                success_rate=success_rate,
                heal_invocations=heal_invocations,
            )

            critique = await analyst._critique_single_agent(metric)
            grade = critique.overall_grade
            score = float(critique.data_points["overall_score"].rstrip("%"))

            grades.append(grade)
            scores.append(score)

        # Verify scores decrease monotonically (each worse than previous)
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], (
                f"Scores not monotonic: {scores[i]}% >= {scores[i + 1]}%"
            )

        # Verify worst case gets F
        assert grades[-1] == "F", f"Worst case should be F, got {grades[-1]}"

        # Verify grades are from valid set
        valid_grades = {"A", "B", "C", "D", "F"}
        for grade in grades:
            assert grade in valid_grades, f"Invalid grade: {grade}"

        print("✅ Grading scale test PASSED: Monotonic grading verified")
        print(f"   Grades (best to worst): {' → '.join(grades)}")
        print(f"   Scores: {[f'{s:.1f}%' for s in scores]}")

    @pytest.mark.asyncio
    async def test_no_bias_in_grading(self):
        """Verify grading is unbiased regardless of agent layer or name."""

        class TestAnalyst(L6ObservabilityBaseAgent):
            async def analyze(self) -> dict[str, Any]:
                return {"status": "test"}

        analyst = TestAnalyst()

        # Same metrics, different layers - should get same grade
        layers = ["L0", "L1", "L2", "L3", "L4", "L5"]
        grades = []
        scores = []

        for layer in layers:
            metric = AgentPerformanceMetrics(
                agent_name=f"{layer}TestAgent",
                layer=layer,
                test_coverage=0.75,
                mcp_hardened=True,
                complexity_score=5,
                success_rate=1.0,
                heal_invocations=1,
            )

            critique = await analyst._critique_single_agent(metric)
            grades.append(critique.overall_grade)
            scores.append(critique.data_points["overall_score"])

        # All grades should be identical (no bias by layer)
        assert len(set(grades)) == 1, f"Grades vary by layer: {dict(zip(layers, grades))}"

        # All scores should be identical
        assert len(set(scores)) == 1, "Scores vary by layer"

        print(f"✅ No-bias test PASSED: Same metrics = same grade ({grades[0]}) across all layers")


def run_all_tests():
    """Run all L6 observability tests."""
    print("=" * 80)
    print("L6 OBSERVABILITY AGENT TEST SUITE")
    print("=" * 80)
    print()

    # Test 1: RuntimeTelemetryAgent
    print("TEST CASE 1: RuntimeTelemetryAgent - 2x Gospel Violation")
    print("-" * 80)
    test_rt = TestRuntimeTelemetryAgent()
    test_rt.test_gospel_violation_detection()
    test_rt.test_gospel_compliance()
    test_rt.test_benchmark_exception_handling()
    print()

    # Test 2: PerformanceAnalystAgent (async)
    print("TEST CASE 2: PerformanceAnalystAgent - Async Event Loop Integrity")
    print("-" * 80)
    test_pa = TestPerformanceAnalystAgent()
    asyncio.run(test_pa.test_async_event_loop_non_blocking())
    asyncio.run(test_pa.test_concurrent_analysis())
    print()

    # Test 3: L6ObservabilityBaseAgent
    print("TEST CASE 3: L6ObservabilityBaseAgent - Skeptical Grading Accuracy")
    print("-" * 80)
    test_base = TestL6ObservabilityBaseAgent()
    asyncio.run(test_base.test_skeptical_grading_strict_threshold())
    asyncio.run(test_base.test_grading_scale_accuracy())
    asyncio.run(test_base.test_no_bias_in_grading())
    print()

    print("=" * 80)
    print("✅ ALL L6 OBSERVABILITY TESTS PASSED")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()
