#!/usr/bin/env python3
"""
Test Suite: SSOTOrchestratorAgent Stability Gates & Tiered Execution

Tests the 5 detailed test cases for:
1. Gate 1: Syntax Critical Failure
2. Gate 2: Structural Stability (Execute Mode)
3. Gate 2: Dry-Run Continuation
4. Two-Phase Deduplication Ordering
5. Full Green Path
"""
import sys
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Enable logging to capture orchestrator output
logging.basicConfig(level=logging.INFO, format='%(message)s')

from agentic_core.L3_orchestration.workflow_engines.SSOTOrchestratorAgent import (
    SSOTOrchestratorAgent,
    AgentResult,
    OrchestrationReport,
)


class MockAgentResult:
    """Helper to create mock agent results."""

    @staticmethod
    def passing(agent_name: str) -> AgentResult:
        return AgentResult(
            agent_name=agent_name,
            status='PASS',
            violations_found=0,
            violations_fixed=0,
            execution_time_ms=10.0
        )

    @staticmethod
    def failing(agent_name: str, violations: int = 1, fixed: int = 0) -> AgentResult:
        return AgentResult(
            agent_name=agent_name,
            status='FAIL',
            violations_found=violations,
            violations_fixed=fixed,
            execution_time_ms=10.0
        )

    @staticmethod
    def error(agent_name: str, message: str = "Test error") -> AgentResult:
        return AgentResult(
            agent_name=agent_name,
            status='ERROR',
            violations_found=0,
            violations_fixed=0,
            execution_time_ms=10.0,
            error_message=message
        )


def test_1_gate_1_syntax_critical_failure():
    """
    Test Case 1: Gate 1 - Syntax Critical Failure

    Run orchestrate(dry_run=True) with SyntaxValidatorAgent failing.
    Expect: Orchestrator stops immediately, NamingAgent (Tier 2) does NOT run.
    """
    print("\n" + "="*60)
    print("TEST 1: Gate 1 - Syntax Critical Failure")
    print("="*60)

    orchestrator = SSOTOrchestratorAgent(PROJECT_ROOT)

    # Track which agents were called
    agents_called = []

    def mock_run_agent(agent_name, dry_run=True, execute=False):
        agents_called.append(agent_name)
        if agent_name == 'SyntaxValidatorAgent':
            return MockAgentResult.failing(agent_name, violations=3)
        return MockAgentResult.passing(agent_name)

    # Patch run_agent to use our mock
    with patch.object(orchestrator, 'run_agent', side_effect=mock_run_agent):
        report = orchestrator.orchestrate(dry_run=True)

    # Verify SyntaxValidatorAgent was called
    assert 'SyntaxValidatorAgent' in agents_called, \
        "SyntaxValidatorAgent should have been called"

    # Verify Tier 2 agents were NOT called (stopped at Gate 1)
    tier2_agents = ['TwoPhaseDeduplicationAgent_PhaseA', 'HygieneGuardianAgent', 'NamingAgent', 'LocationAgent']
    for agent in tier2_agents:
        assert agent not in agents_called, \
            f"{agent} should NOT have been called after syntax failure"

    # Verify Tier 3 agents were NOT called
    tier3_agents = ['GravityEnforcerAgent', 'TwoPhaseDeduplicationAgent_PhaseB', 'CodeSSOTEnforcerAgent']
    for agent in tier3_agents:
        assert agent not in agents_called, \
            f"{agent} should NOT have been called after syntax failure"

    print(f"✅ PASSED: Gate 1 (Syntax Critical Failure) working")
    print(f"   Agents called: {agents_called}")
    print(f"   Tier 2/3 agents correctly skipped after syntax failure")
    return True


def test_2_gate_2_structural_stability_execute_mode():
    """
    Test Case 2: Gate 2 - Structural Stability (Execute Mode)

    Run orchestrate(execute=True) with Tier 1 passing but Tier 2 failing.
    Expect: Tier 3 does NOT run because structural violations persist in execute mode.
    """
    print("\n" + "="*60)
    print("TEST 2: Gate 2 - Structural Stability (Execute Mode)")
    print("="*60)

    orchestrator = SSOTOrchestratorAgent(PROJECT_ROOT)

    # Track which agents were called
    agents_called = []

    def mock_run_agent(agent_name, dry_run=True, execute=False):
        agents_called.append(agent_name)
        # Tier 1 passes
        if agent_name == 'SyntaxValidatorAgent':
            return MockAgentResult.passing(agent_name)
        # Tier 2: NamingAgent fails (simulating unfixable naming violation)
        if agent_name == 'NamingAgent':
            return MockAgentResult.failing(agent_name, violations=2, fixed=0)
        # All other agents pass
        return MockAgentResult.passing(agent_name)

    # Patch run_agent to use our mock
    with patch.object(orchestrator, 'run_agent', side_effect=mock_run_agent):
        report = orchestrator.orchestrate(dry_run=False, execute=True)

    # Verify Tier 1 completed
    assert 'SyntaxValidatorAgent' in agents_called, \
        "SyntaxValidatorAgent should have been called"

    # Verify Tier 2 ran (including the failing NamingAgent)
    assert 'NamingAgent' in agents_called, \
        "NamingAgent should have been called"

    # Verify Tier 3 agents were NOT called (stopped at Gate 2 in execute mode)
    tier3_agents = ['GravityEnforcerAgent', 'TwoPhaseDeduplicationAgent_PhaseB', 'CodeSSOTEnforcerAgent']
    for agent in tier3_agents:
        assert agent not in agents_called, \
            f"{agent} should NOT have been called after Tier 2 failure in execute mode"

    print(f"✅ PASSED: Gate 2 (Structural Stability - Execute Mode) working")
    print(f"   Agents called: {agents_called}")
    print(f"   Tier 3 agents correctly skipped after Tier 2 failure in execute mode")
    return True


def test_3_gate_2_dry_run_continuation():
    """
    Test Case 3: Gate 2 - Dry-Run Continuation

    Run orchestrate(dry_run=True, execute=False) with Tier 2 failing.
    Expect: Tier 3 DOES run because dry-runs are non-destructive.
    """
    print("\n" + "="*60)
    print("TEST 3: Gate 2 - Dry-Run Continuation")
    print("="*60)

    orchestrator = SSOTOrchestratorAgent(PROJECT_ROOT)

    # Track which agents were called
    agents_called = []

    def mock_run_agent(agent_name, dry_run=True, execute=False):
        agents_called.append(agent_name)
        # Tier 1 passes
        if agent_name == 'SyntaxValidatorAgent':
            return MockAgentResult.passing(agent_name)
        # Tier 2: NamingAgent fails
        if agent_name == 'NamingAgent':
            return MockAgentResult.failing(agent_name, violations=2, fixed=0)
        # All other agents pass
        return MockAgentResult.passing(agent_name)

    # Patch run_agent to use our mock
    with patch.object(orchestrator, 'run_agent', side_effect=mock_run_agent):
        report = orchestrator.orchestrate(dry_run=True, execute=False)

    # Verify Tier 1 completed
    assert 'SyntaxValidatorAgent' in agents_called, \
        "SyntaxValidatorAgent should have been called"

    # Verify Tier 2 ran
    assert 'NamingAgent' in agents_called, \
        "NamingAgent should have been called"

    # Verify Tier 3 agents WERE called (dry-run continues despite Tier 2 failure)
    tier3_agents = ['GravityEnforcerAgent', 'TwoPhaseDeduplicationAgent_PhaseB', 'CodeSSOTEnforcerAgent']
    for agent in tier3_agents:
        assert agent in agents_called, \
            f"{agent} SHOULD have been called in dry-run mode despite Tier 2 failure"

    print(f"✅ PASSED: Gate 2 (Dry-Run Continuation) working")
    print(f"   Agents called: {agents_called}")
    print(f"   Tier 3 agents correctly ran in dry-run mode despite Tier 2 failure")
    return True


def test_4_two_phase_deduplication_ordering():
    """
    Test Case 4: Two-Phase Deduplication Ordering

    Verify that PhaseA runs in Tier 2 (before NamingAgent moves files)
    and PhaseB runs in Tier 3 (after LocationAgent has settled file paths).
    """
    print("\n" + "="*60)
    print("TEST 4: Two-Phase Deduplication Ordering")
    print("="*60)

    orchestrator = SSOTOrchestratorAgent(PROJECT_ROOT)

    # Check the tiers structure directly
    tiers = orchestrator.tiers

    # Verify tier structure exists
    assert "Tier 1: Parseability Gate" in tiers, "Tier 1 should exist"
    assert "Tier 2: Identity & Structure" in tiers, "Tier 2 should exist"
    assert "Tier 3: Deep Compliance" in tiers, "Tier 3 should exist"

    # Verify PhaseA is in Tier 2
    tier2_agents = tiers["Tier 2: Identity & Structure"]
    assert "TwoPhaseDeduplicationAgent_PhaseA" in tier2_agents, \
        "PhaseA should be in Tier 2"

    # Verify PhaseB is in Tier 3
    tier3_agents = tiers["Tier 3: Deep Compliance"]
    assert "TwoPhaseDeduplicationAgent_PhaseB" in tier3_agents, \
        "PhaseB should be in Tier 3"

    # Verify PhaseA comes before NamingAgent in Tier 2
    phase_a_idx = tier2_agents.index("TwoPhaseDeduplicationAgent_PhaseA")
    naming_idx = tier2_agents.index("NamingAgent")
    assert phase_a_idx < naming_idx, \
        f"PhaseA (idx={phase_a_idx}) should come before NamingAgent (idx={naming_idx})"

    # Verify PhaseB comes after GravityEnforcerAgent in Tier 3
    gravity_idx = tier3_agents.index("GravityEnforcerAgent")
    phase_b_idx = tier3_agents.index("TwoPhaseDeduplicationAgent_PhaseB")
    assert gravity_idx < phase_b_idx, \
        f"GravityEnforcerAgent (idx={gravity_idx}) should come before PhaseB (idx={phase_b_idx})"

    print(f"✅ PASSED: Two-Phase Deduplication Ordering correct")
    print(f"   Tier 2: {tier2_agents}")
    print(f"   Tier 3: {tier3_agents}")
    print(f"   PhaseA in Tier 2 before NamingAgent: ✓")
    print(f"   PhaseB in Tier 3 after GravityEnforcerAgent: ✓")
    return True


def test_5_full_green_path():
    """
    Test Case 5: Full Green Path

    Run on a "clean" repository (all agents pass).
    Expect: All 3 Tiers execute sequentially with 100% success rate.
    """
    print("\n" + "="*60)
    print("TEST 5: Full Green Path")
    print("="*60)

    orchestrator = SSOTOrchestratorAgent(PROJECT_ROOT)

    # Track which agents were called and in what order
    agents_called = []

    def mock_run_agent(agent_name, dry_run=True, execute=False):
        agents_called.append(agent_name)
        return MockAgentResult.passing(agent_name)

    # Patch run_agent to use our mock
    with patch.object(orchestrator, 'run_agent', side_effect=mock_run_agent):
        report = orchestrator.orchestrate(dry_run=True)

    # Verify all agents were called
    expected_agents = [
        'SyntaxValidatorAgent',  # Tier 1
        'TwoPhaseDeduplicationAgent_PhaseA', 'HygieneGuardianAgent', 'NamingAgent', 'LocationAgent',  # Tier 2
        'GravityEnforcerAgent', 'TwoPhaseDeduplicationAgent_PhaseB', 'CodeSSOTEnforcerAgent'  # Tier 3
    ]

    for agent in expected_agents:
        assert agent in agents_called, \
            f"{agent} should have been called in full green path"

    # Verify order: Tier 1 before Tier 2 before Tier 3
    syntax_idx = agents_called.index('SyntaxValidatorAgent')
    naming_idx = agents_called.index('NamingAgent')
    gravity_idx = agents_called.index('GravityEnforcerAgent')

    assert syntax_idx < naming_idx < gravity_idx, \
        f"Tier order incorrect: Syntax({syntax_idx}) < Naming({naming_idx}) < Gravity({gravity_idx})"

    # Verify report shows 100% success
    assert report.success_rate == 100.0, \
        f"Expected 100% success rate, got {report.success_rate}%"
    assert report.overall_status == 'PASS', \
        f"Expected PASS status, got {report.overall_status}"
    assert report.total_violations == 0, \
        f"Expected 0 violations, got {report.total_violations}"

    print(f"✅ PASSED: Full Green Path working")
    print(f"   Agents called (in order): {agents_called}")
    print(f"   Success rate: {report.success_rate}%")
    print(f"   Overall status: {report.overall_status}")
    print(f"   Total violations: {report.total_violations}")
    return True


def run_all_tests():
    """Run all test cases."""
    print("\n" + "#"*60)
    print("# SSOTOrchestratorAgent Stability Gates Test Suite")
    print("#"*60)

    tests = [
        ("Test 1: Gate 1 - Syntax Critical Failure", test_1_gate_1_syntax_critical_failure),
        ("Test 2: Gate 2 - Structural Stability (Execute Mode)", test_2_gate_2_structural_stability_execute_mode),
        ("Test 3: Gate 2 - Dry-Run Continuation", test_3_gate_2_dry_run_continuation),
        ("Test 4: Two-Phase Deduplication Ordering", test_4_two_phase_deduplication_ordering),
        ("Test 5: Full Green Path", test_5_full_green_path),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("="*60)

    if failed > 0:
        print(f"❌ {failed} test(s) FAILED")
        return 1
    else:
        print("✅ ALL TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
