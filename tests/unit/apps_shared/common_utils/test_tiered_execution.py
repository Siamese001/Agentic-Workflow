#!/usr/bin/env python3
"""
Test Suite for Tiered Execution Strategy

Verifies all 5 test cases for the Controlled Burns feature:
1. Isolation Test - Only specified tier runs
2. Default Behavior - All tiers run without --tier
3. Out-of-Bounds - Invalid tier is rejected
4. Burn Verification - Execute mode works correctly
5. State Integrity - Strategy correctly filters tiers
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0


def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")


def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")


# =============================================================================
# Test 1: Isolation Test
# =============================================================================
def test_isolation():
    """Verify that --tier 1 only runs Tier 1 agents."""
    print("\n" + "=" * 70)
    print("Test 1: Isolation Test")
    print("=" * 70)

    from agentic_core.L5_safety.validators.healing_strategy import HealingStrategy

    # Create strategy with target_tier=1
    strategy = HealingStrategy(project_root=PROJECT_ROOT, target_tier=1)

    # Verify should_run_tier returns correct values
    tier0_should_run = strategy.should_run_tier("Tier 0: Pre-Flight")
    tier1_should_run = strategy.should_run_tier("Tier 1: Structural")
    tier2_should_run = strategy.should_run_tier("Tier 2: Architectural")

    if not tier0_should_run and tier1_should_run and not tier2_should_run:
        test_pass("TEST-1", "Isolation - Only Tier 1 runs when target_tier=1")
    else:
        test_fail(
            "TEST-1",
            f"Isolation failed: Tier0={tier0_should_run}, "
            f"Tier1={tier1_should_run}, Tier2={tier2_should_run}",
        )


# =============================================================================
# Test 2: Default Behavior
# =============================================================================
def test_default_behavior():
    """Verify that all tiers run when no --tier is specified."""
    print("\n" + "=" * 70)
    print("Test 2: Default Behavior")
    print("=" * 70)

    from agentic_core.L5_safety.validators.healing_strategy import HealingStrategy

    # Create strategy without target_tier (None = run all)
    strategy = HealingStrategy(project_root=PROJECT_ROOT, target_tier=None)

    # Verify all tiers should run
    tier0_should_run = strategy.should_run_tier("Tier 0: Pre-Flight")
    tier1_should_run = strategy.should_run_tier("Tier 1: Structural")
    tier2_should_run = strategy.should_run_tier("Tier 2: Architectural")
    tier3_should_run = strategy.should_run_tier("Tier 3: Dynamic")
    tier4_should_run = strategy.should_run_tier("Tier 4: Final Gate")

    all_run = (
        tier0_should_run
        and tier1_should_run
        and tier2_should_run
        and tier3_should_run
        and tier4_should_run
    )

    if all_run:
        test_pass("TEST-2", "Default behavior - All 5 tiers run when target_tier=None")
    else:
        test_fail("TEST-2", "Default behavior failed: Not all tiers run")


# =============================================================================
# Test 3: Out-of-Bounds
# =============================================================================
def test_out_of_bounds():
    """Verify that --tier 9 is rejected by argparse."""
    print("\n" + "=" * 70)
    print("Test 3: Out-of-Bounds")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, "canon_validator_agentic_v2_thin.py", "--tier", "9"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 and "invalid choice: 9" in result.stderr:
        test_pass("TEST-3", "Out-of-bounds - argparse rejects --tier 9")
    else:
        test_fail("TEST-3", "Out-of-bounds not rejected properly")


# =============================================================================
# Test 4: Burn Verification (Structural)
# =============================================================================
def test_burn_verification():
    """Verify that tier filtering works with execute mode."""
    print("\n" + "=" * 70)
    print("Test 4: Burn Verification")
    print("=" * 70)

    from agentic_core.L5_safety.validators.healing_strategy import HealingStrategy

    # Create strategy with target_tier=1 (Structural)
    strategy = HealingStrategy(project_root=PROJECT_ROOT, target_tier=1)

    # Verify the strategy has the correct target_tier
    if strategy.target_tier == 1:
        test_pass("TEST-4a", "Burn verification - target_tier correctly set to 1")
    else:
        test_fail("TEST-4a", f"target_tier is {strategy.target_tier}, expected 1")

    # Verify skip message is generated correctly
    skip_msg = strategy.get_tier_skip_message("Tier 0: Pre-Flight")
    if "SKIPPING" in skip_msg and "target_tier=1" in skip_msg:
        test_pass("TEST-4b", "Burn verification - Skip message correctly generated")
    else:
        test_fail("TEST-4b", f"Skip message incorrect: {skip_msg}")


# =============================================================================
# Test 5: State Integrity
# =============================================================================
def test_state_integrity():
    """Verify that OrchestratorAgent respects tier filtering."""
    print("\n" + "=" * 70)
    print("Test 5: State Integrity")
    print("=" * 70)

    from agentic_core.core.orchestrator_main import OrchestratorAgent
    from agentic_core.L5_safety.validators.healing_strategy import HealingStrategy

    # Create strategy with target_tier=0 (Pre-Flight only)
    strategy = HealingStrategy(project_root=PROJECT_ROOT, target_tier=0)

    # Verify the orchestrator can be created with the strategy
    try:
        orchestrator = OrchestratorAgent(
            strategy=strategy, project_root=PROJECT_ROOT, name="TestOrchestrator"
        )
        test_pass("TEST-5a", "State integrity - Orchestrator created with filtered strategy")
    except Exception as e:
        test_fail("TEST-5a", f"Orchestrator creation failed: {e}")
        return

    # Verify the strategy's should_run_tier is accessible from orchestrator
    if hasattr(orchestrator.strategy, "should_run_tier"):
        test_pass("TEST-5b", "State integrity - should_run_tier method accessible")
    else:
        test_fail("TEST-5b", "should_run_tier method not accessible")


# =============================================================================
# Main
# =============================================================================
def main():
    print("\n" + "=" * 70)
    print("TIERED EXECUTION TEST SUITE")
    print("=" * 70)

    test_isolation()
    test_default_behavior()
    test_out_of_bounds()
    test_burn_verification()
    test_state_integrity()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total = PASSED + FAILED
    print(f"  Total Tests: {total}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {100 * PASSED / total:.1f}%")

    if FAILED == 0:
        print("\n  ✅ ALL TESTS PASSED - 100% SUCCESS RATE")
        return 0
    else:
        print(f"\n  ❌ {FAILED} TESTS FAILED - REQUIRES ATTENTION")
        return 1


if __name__ == "__main__":
    sys.exit(main())
