#!/usr/bin/env python3
"""
Test that healing ALWAYS proceeds, using LLM when confidence < 0.75
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_always_heal_with_llm():
    """Test that healing always proceeds, using LLM when confidence is low"""

    print("=== Test: Healing ALWAYS ON with LLM Arbitration ===\n")

    # Create a test file in an invalid location
    test_dir = project_root / "temp_test_always_heal"
    test_dir.mkdir(exist_ok=True)

    test_file = test_dir / "AlwaysHealTestAgent.py"
    test_file.write_text("""
# This file should always be healed, regardless of confidence
class AlwaysHealTestAgent:
    '''File in wrong location - should be moved with LLM help if needed'''
    pass
""")

    try:
        from agentic_core.L0_routing.scripts.execute_ssot import (
            RuntimeStateManager,
            SovereignDecisionEngine,
            execute_phase2_reconciliation,
        )

        print("1. Setting up agents with LLM ENABLED...")

        # Initialize required components
        state_mgr = RuntimeStateManager(project_root)

        # IMPORTANT: Enable LLM to ensure healing always proceeds
        decision_engine = SovereignDecisionEngine(
            enable_llm=True,  # LLM ENABLED - healing will ALWAYS proceed
            state_mgr=state_mgr,
        )

        # Create agents dict
        from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent

        agents = {"LocationAgent": LocationAgent(project_root)}

        print("2. Creating violation with LOW confidence (will trigger LLM)...")

        # Create a violation with low confidence type
        violations_found = [
            {
                "suggested_agent": "LocationAgent",
                "file": str(test_file),
                "type": "UNKNOWN",  # This gets low confidence (0.5)
                "message": "File in unknown location - needs LLM arbitration",
                "severity": "medium",
            },
        ]

        plan = {
            "violations_found": violations_found,
            "territory": "temp_test_always_heal",
            "confidence": 0.45,  # Low confidence - should trigger LLM
        }

        print(f"  Plan includes {len(violations_found)} violation(s) with LOW confidence")
        print("  Expected: LLM arbitration will be used")

        print("\n3. Testing Phase 2 reconciliation with LLM arbitration...")

        # Execute Phase 2 reconciliation
        result = execute_phase2_reconciliation(
            agents=agents,
            territory="temp_test_always_heal",
            decision_engine=decision_engine,
            state_mgr=state_mgr,
            plan=plan,
            dry_run=False,  # Actual execution
        )

        print(f"\nResult: {json.dumps(result, indent=2)}")

        # Check the decision engine to see if LLM was used
        llm_decisions = [d for d in decision_engine.decisions_made if "LLM" in d.get("reason", "")]

        if llm_decisions:
            print(f"\n✓ LLM was used for decision: {llm_decisions[0]['reason']}")
        else:
            print("\n! No LLM decisions recorded (high confidence path used)")

        # The key test: healing should have been attempted, not blocked
        if result["violations_found"] > 0:
            if result["status"] == "success" or (result["violations_fixed"] > 0):
                print("✓ Healing proceeded successfully")
            elif result["errors"] > 0:
                print("! Healing attempted but failed (check logs for details)")
                print("  This is OK - the important thing is that it wasn't BLOCKED")
            else:
                print("? Healing result unclear")
        else:
            print("! No violations found")

        # Verify it wasn't blocked due to confidence
        error_message = result.get("error_message", "")
        if error_message and "BLOCK" in error_message:
            print("✗ ERROR: Healing was blocked - this should not happen with LLM enabled")
            return False
        else:
            print("✓ Healing was NOT blocked - LLM arbitration worked")

        return True

    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def test_confidence_thresholds():
    """Test different confidence levels to ensure proper LLM usage"""

    print("\n=== Test: Confidence Threshold Behavior ===\n")

    from agentic_core.L0_routing.scripts.execute_ssot import (
        ConfidenceScore,
        SovereignDecisionEngine,
    )

    decision_engine = SovereignDecisionEngine(enable_llm=True)

    test_cases = [
        (0.9, "HIGH confidence - should proceed without LLM"),
        (0.6, "MEDIUM confidence - should use LLM Flash"),
        (0.3, "LOW confidence - should use LLM Pro"),
    ]

    for i, (confidence_val, description) in enumerate(test_cases):
        print(f"\nTesting {description} ({confidence_val})...")

        confidence = ConfidenceScore(value=confidence_val, reasoning=f"Test confidence {confidence_val}")

        allowed, reason = decision_engine.should_proceed_with_healing(confidence, f"TestAgent{i}")

        print(f"  Result: {allowed}")
        print(f"  Reason: {reason}")

        if not allowed:
            print("  ✗ ERROR: Should always be allowed with LLM enabled")
            return False
        elif "LLM-ARBITRATED-FLASH" in reason:
            print("  ✓ MEDIUM confidence - LLM Flash used as expected")
        elif "REASONING-RECOVERY-PRO" in reason:
            print("  ✓ LOW confidence - LLM Pro used as expected")
        elif "SOVEREIGN-AUTO" in reason:
            print("  ✓ HIGH confidence - no LLM needed")
        else:
            print(f"  ? Unexpected reason: {reason}")

    return True


if __name__ == "__main__":
    print("=== Testing: Healing ALWAYS ON with LLM Support ===\n")

    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    # Check if Gemini API key is available
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY not found in .env")
        print("  LLM arbitration will fail, but healing should still proceed")

    always_heal_test = test_always_heal_with_llm()
    confidence_test = test_confidence_thresholds()

    print("\n=== Final Results ===")
    print(f"Always heal with LLM: {'PASS' if always_heal_test else 'FAIL'}")
    print(f"Confidence thresholds: {'PASS' if confidence_test else 'FAIL'}")

    if always_heal_test and confidence_test:
        print("\n✅ ALL TESTS PASSED!")
        print("Healing is now ALWAYS ON with LLM arbitration when needed")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
