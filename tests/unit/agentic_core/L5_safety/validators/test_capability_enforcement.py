#!/usr/bin/env python3
"""
Test script for sub-atomic capability enforcement.
Validates that HierarchyAgent correctly detects capability violations.
"""

from pathlib import Path

from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent


def main():
    project_root = Path(__file__).parent.parent
    hierarchy_agent = HierarchyAgent(project_root)

    print("\n" + "=" * 80)
    print("SUB-ATOMIC CAPABILITY ENFORCEMENT TEST")
    print("=" * 80)

    # Run capability enforcement scan
    print("\n[*] Running capability isolation enforcement...")
    violations = hierarchy_agent.enforce_subatomic_capability_isolation()

    print(f"\n[RESULTS] Found {len(violations)} capability violations:\n")

    if violations:
        for file_path, violation_msg in violations:
            rel_path = file_path.relative_to(project_root)
            print(f"  ❌ {rel_path}")
            print(f"     {violation_msg}\n")
    else:
        print("  ✅ No capability violations detected — all agents are sub-atomically pure!\n")

    # Run full scan with both hierarchy and capability checks
    print("\n" + "=" * 80)
    print("FULL COMPLIANCE SCAN (Hierarchy + Capability)")
    print("=" * 80 + "\n")

    results = hierarchy_agent.run_with_capability_enforcement()

    print("[SUMMARY]")
    print(f"  Hierarchy violations: {len(results['hierarchy_violations'])}")
    print(f"  Capability violations: {len(results['capability_violations'])}")
    print(f"  Total violations: {results['total_violations']}")

    if results["total_violations"] == 0:
        print("\n✅ ETERNAL PURITY ACHIEVED — All agents compliant!\n")
    else:
        print("\n⚠️  Violations detected — healing recommended\n")


if __name__ == "__main__":
    main()
