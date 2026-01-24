#!/usr/bin/env python3
"""Quick test for CognitiveRecoveryMixin integration."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.base_agents.CognitiveRecoveryMixin import CognitiveRecoveryMixin


class TestAgent(CognitiveRecoveryMixin):
    pass


def main():
    print("Testing CognitiveRecoveryMixin...")

    agent = TestAgent()

    # Test 1: consult_knowledge_base
    print("\n[TEST 1] consult_knowledge_base('dashboard testing')")
    results = agent.consult_knowledge_base("dashboard testing")
    print(f"  Returned {len(results)} results")
    if results:
        top = results[0]
        print(f"  Top result: {top['id']} (score: {top['score']:.3f})")

    # Test 2: perform_cognitive_rca
    print("\n[TEST 2] perform_cognitive_rca(ValueError('base class missing'))")
    try:
        raise ValueError("base class inheritance missing")
    except Exception as e:
        advice = agent.perform_cognitive_rca(e)
        if advice:
            print("  ✅ RCA returned advice")
        else:
            print("  ⚠️  No high-confidence pattern found (expected for novel errors)")

    print("\n✅ CognitiveRecoveryMixin integration test complete")


if __name__ == "__main__":
    main()
