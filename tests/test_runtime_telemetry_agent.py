#!/usr/bin/env python3
"""
Robust Tests for RuntimeTelemetryAgent
"""

import sys
import time
from pathlib import Path

# Setup mock for MCPHardenedMixin
class MockMixin: pass
mock_module = type(sys)('mock')
mock_module.MCPHardenedMixin = MockMixin
sys.modules['agentic_core.utils.core_extensions.mcp_hardened_mixin'] = mock_module

# Direct import
import importlib.util
spec = importlib.util.spec_from_file_location(
    'RuntimeTelemetryAgent',
    Path('agentic_core/L6_observability/agents/RuntimeTelemetryAgent.py')
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RuntimeTelemetryAgent = module.RuntimeTelemetryAgent


def test_benchmark_startup():
    """TEST 1: Benchmark Startup"""
    print("=" * 60)
    print("TEST 1: BENCHMARK STARTUP")
    print("=" * 60)
    
    class MockAgent:
        def __init__(self):
            time.sleep(0.05)  # 50ms startup
    
    telemetry = RuntimeTelemetryAgent()
    agent, duration = telemetry.benchmark_startup(MockAgent)
    
    print(f"Agent class: {agent.__class__.__name__}")
    print(f"Duration: {duration*1000:.3f} ms")
    
    assert agent is not None
    assert duration >= 0.05, f"Expected >= 50ms, got {duration*1000:.3f}ms"
    assert 'MockAgent' in telemetry.metrics
    
    print("\n✅ TEST 1 PASSED: Benchmark startup working")


def test_overhead_audit_optimal():
    """TEST 2: Overhead Audit - Optimal"""
    print("\n" + "=" * 60)
    print("TEST 2: OVERHEAD AUDIT - OPTIMAL")
    print("=" * 60)
    
    telemetry = RuntimeTelemetryAgent(limit_multiplier=2.0)
    
    # 50ms current vs 30ms baseline = 1.67x (under 2x limit)
    report = telemetry.audit_security_overhead(0.03, 0.05)
    
    print(f"Baseline: 30ms")
    print(f"Current: 50ms")
    print(f"Ratio: {report['ratio']}x")
    print(f"Status: {report['status']}")
    print(f"Breached: {report['breach']}")
    
    assert report['ratio'] < 2.0
    assert report['status'] == "✅ OPTIMAL"
    assert report['breach'] is False
    
    print("\n✅ TEST 2 PASSED: Optimal overhead detected correctly")


def test_overhead_audit_critical():
    """TEST 3: Overhead Audit - Critical"""
    print("\n" + "=" * 60)
    print("TEST 3: OVERHEAD AUDIT - CRITICAL")
    print("=" * 60)
    
    telemetry = RuntimeTelemetryAgent(limit_multiplier=2.0)
    
    # 50ms current vs 20ms baseline = 2.5x (over 2x limit)
    report = telemetry.audit_security_overhead(0.02, 0.05)
    
    print(f"Baseline: 20ms")
    print(f"Current: 50ms")
    print(f"Ratio: {report['ratio']}x")
    print(f"Status: {report['status']}")
    print(f"Breached: {report['breach']}")
    
    assert report['ratio'] > 2.0
    assert "CRITICAL" in report['status']
    assert report['breach'] is True
    
    print("\n✅ TEST 3 PASSED: Critical overhead detected correctly")


def test_report_generation():
    """TEST 4: Report Generation"""
    print("\n" + "=" * 60)
    print("TEST 4: REPORT GENERATION")
    print("=" * 60)
    
    class FastAgent:
        def __init__(self):
            time.sleep(0.01)  # 10ms
    
    class SlowAgent:
        def __init__(self):
            time.sleep(0.03)  # 30ms
    
    telemetry = RuntimeTelemetryAgent()
    telemetry.benchmark_startup(FastAgent)
    telemetry.benchmark_startup(SlowAgent)
    
    print("\nGenerated Report:")
    print("-" * 40)
    telemetry.report_performance()
    
    assert len(telemetry.metrics) == 2
    assert 'FastAgent' in telemetry.metrics
    assert 'SlowAgent' in telemetry.metrics
    
    print("\n✅ TEST 4 PASSED: Report generated successfully")


def test_multiple_agents_benchmark():
    """TEST 5: Multiple Agents Benchmark"""
    print("\n" + "=" * 60)
    print("TEST 5: MULTIPLE AGENTS BENCHMARK")
    print("=" * 60)
    
    class Agent1:
        def __init__(self):
            time.sleep(0.01)
    
    class Agent2:
        def __init__(self):
            time.sleep(0.02)
    
    class Agent3:
        def __init__(self):
            time.sleep(0.03)
    
    telemetry = RuntimeTelemetryAgent()
    
    total_time = 0
    for agent_class in [Agent1, Agent2, Agent3]:
        _, duration = telemetry.benchmark_startup(agent_class)
        total_time += duration
        print(f"  {agent_class.__name__}: {duration*1000:.3f}ms")
    
    print(f"\nTotal startup time: {total_time*1000:.3f}ms")
    print(f"Agents benchmarked: {len(telemetry.metrics)}")
    
    assert len(telemetry.metrics) == 3
    assert total_time >= 0.06  # At least 60ms total
    
    print("\n✅ TEST 5 PASSED: Multiple agents benchmarked")


def test_zero_baseline_handling():
    """TEST 6: Zero Baseline Handling"""
    print("\n" + "=" * 60)
    print("TEST 6: ZERO BASELINE HANDLING")
    print("=" * 60)
    
    telemetry = RuntimeTelemetryAgent()
    
    # Zero baseline should not cause division by zero
    report = telemetry.audit_security_overhead(0.0, 0.05)
    
    print(f"Baseline: 0ms")
    print(f"Current: 50ms")
    print(f"Ratio: {report['ratio']}x")
    
    assert report['ratio'] == 0  # Should handle gracefully
    
    print("\n✅ TEST 6 PASSED: Zero baseline handled gracefully")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUNTIME TELEMETRY AGENT - ROBUST TESTING")
    print("=" * 60 + "\n")
    
    # Run tests
    test_benchmark_startup()
    test_overhead_audit_optimal()
    test_overhead_audit_critical()
    test_report_generation()
    test_multiple_agents_benchmark()
    test_zero_baseline_handling()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
