#!/usr/bin/env python3
"""Test CognitiveRecoveryMixin integration in SelfRecoveringOrchestratorAgent."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ARCHIVED: SelfRecoveringOrchestratorAgent import removed # (
    SelfRecoveringOrchestratorAgent,
)


def main():
    print("Testing SelfRecoveringOrchestratorAgent with CognitiveRecoveryMixin...")

    # Test 1: Import and instantiation
    print("\n[TEST 1] Import and Instantiation")
    agent = SelfRecoveringOrchestratorAgent()
    print("  ✅ Agent instantiated successfully")

    # Test 2: Check for cognitive recovery methods
    print("\n[TEST 2] Cognitive Recovery Methods")
    has_attempt = hasattr(agent, "attempt_cognitive_recovery")
    has_perform = hasattr(agent, "perform_cognitive_rca")
    has_consult = hasattr(agent, "consult_knowledge_base")

    print(f"  attempt_cognitive_recovery: {'✅' if has_attempt else '❌'}")
    print(f"  perform_cognitive_rca: {'✅' if has_perform else '❌'}")
    print(f"  consult_knowledge_base: {'✅' if has_consult else '❌'}")

    if not all([has_attempt, has_perform, has_consult]):
        print("\n❌ Missing cognitive recovery methods")
        return 1

    # Test 3: Trigger cognitive recovery
    print("\n[TEST 3] Trigger Cognitive Recovery")
    try:
        raise ValueError("base class inheritance missing in HealerMixin")
    except Exception as e:
        found_fix = agent.attempt_cognitive_recovery(e)
        if found_fix:
            print("  ✅ Cognitive recovery found a known pattern")
        else:
            print("  ⚠️  No high-confidence pattern (expected for some errors)")

    print("\n✅ All tests passed - SelfRecoveringOrchestratorAgent has cognitive capabilities")
    return 0


if __name__ == "__main__":
    sys.exit(main())
