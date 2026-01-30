#!/usr/bin/env python3
"""
MRO Verification Script

Verifies the Method Resolution Order (MRO) for complex agents after
the infrastructure_mixin consolidation.

Opportunity #4: Mixin Inheritance Complexity - Phase 4 Verification
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_mro(agent_class, agent_name: str):
    """Print the MRO for an agent class."""
    print(f"\n{'=' * 80}")
    print(f"MRO for {agent_name}")
    print(f"{'=' * 80}")

    mro = agent_class.__mro__
    for i, cls in enumerate(mro):
        indent = "  " * i
        print(f"{indent}{i}. {cls.__module__}.{cls.__name__}")

    print(f"\nTotal classes in MRO: {len(mro)}")

    # Check for infrastructure_mixin
    has_infra = any("infrastructure_mixin" in cls.__name__ for cls in mro)
    has_healer = any("HealerMixin" in cls.__name__ for cls in mro)
    has_mcp = any("MCPHardened" in cls.__name__ for cls in mro)
    has_testing = any("SubatomicTesting" in cls.__name__ for cls in mro)

    print("\nInfrastructure Components:")
    print(f"  infrastructure_mixin: {'✅' if has_infra else '❌'}")
    print(f"  HealerMixin: {'✅' if has_healer else '❌'}")
    print(f"  MCPHardenedMixin: {'✅' if has_mcp else '❌'}")
    print(f"  SubatomicTestingMixin: {'✅' if has_testing else '❌'}")

    return {
        "has_infra": has_infra,
        "has_healer": has_healer,
        "has_mcp": has_mcp,
        "has_testing": has_testing,
        "mro_length": len(mro),
    }


def verify_sovereign_base_agent():
    """Verify SovereignBaseAgent MRO."""
    try:
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        return print_mro(SovereignBaseAgent, "SovereignBaseAgent")
    except ImportError as e:
        print(f"❌ Failed to import SovereignBaseAgent: {e}")
        return None


def verify_meta_learning_agent():
    """Verify MetaLearningAgent MRO (complex case)."""
    try:
        from agentic_core.L6_observability.meta_learning.MetaLearningAgent import MetaLearningAgent

        return print_mro(MetaLearningAgent, "MetaLearningAgent")
    except ImportError as e:
        print(f"❌ Failed to import MetaLearningAgent: {e}")
        return None


def verify_location_validator_agent():
    """Verify LocationValidatorAgent MRO."""
    try:
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent

        return print_mro(LocationValidatorAgent, "LocationValidatorAgent")
    except ImportError as e:
        print(f"❌ Failed to import LocationValidatorAgent: {e}")
        return None


def verify_hierarchy_agent():
    """Verify HierarchyAgent MRO."""
    try:
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        return print_mro(HierarchyAgent, "HierarchyAgent")
    except ImportError as e:
        print(f"❌ Failed to import HierarchyAgent: {e}")
        return None


def main():
    """Run MRO verification for multiple agents."""
    print("=" * 80)
    print("MRO VERIFICATION - Opportunity #4: Mixin Inheritance Complexity")
    print("=" * 80)

    results = {}

    # Test 1: SovereignBaseAgent (root)
    print("\n[Test 1] SovereignBaseAgent (Root)")
    results["sovereign"] = verify_sovereign_base_agent()

    # Test 2: MetaLearningAgent (complex case)
    print("\n[Test 2] MetaLearningAgent (Complex Case)")
    results["meta_learning"] = verify_meta_learning_agent()

    # Test 3: LocationValidatorAgent (L5 agent)
    print("\n[Test 3] LocationValidatorAgent (L5 Agent)")
    results["location_validator"] = verify_location_validator_agent()

    # Test 4: HierarchyAgent (L5 agent)
    print("\n[Test 4] HierarchyAgent (L5 Agent)")
    results["hierarchy"] = verify_hierarchy_agent()

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    success_count = sum(1 for r in results.values() if r is not None and r.get("has_infra"))
    total_count = len(results)

    print(f"\nAgents with infrastructure_mixin: {success_count}/{total_count}")

    for agent_name, result in results.items():
        if result is None:
            print(f"  ❌ {agent_name}: Failed to import")
        elif result.get("has_infra"):
            print(
                f"  ✅ {agent_name}: infrastructure_mixin present (MRO length: {result['mro_length']})"
            )
        else:
            print(
                f"  ⚠️  {agent_name}: infrastructure_mixin missing (MRO length: {result['mro_length']})"
            )

    # Validation
    if success_count == total_count:
        print("\n✅ ALL AGENTS VERIFIED: infrastructure_mixin consolidation successful")
        return 0
    else:
        print(
            f"\n❌ VERIFICATION FAILED: {total_count - success_count} agents missing infrastructure_mixin"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
