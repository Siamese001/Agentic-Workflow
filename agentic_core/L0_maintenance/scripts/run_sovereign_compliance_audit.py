#!/usr/bin/env python3
"""
Phase 7: Sovereign Compliance Audit

Runs CodeValidatorAgent and StructureEnforcerAgent across the policy_engine
directory to verify sovereign namespace compliance.
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.policy_engine.CodeValidatorAgent import CodeValidatorAgent
from agentic_core.L5_safety.policy_engine.StructureEnforcerAgent import StructureEnforcerAgent


def run_code_validator():
    """Run CodeValidatorAgent on policy_engine directory."""
    print("=" * 80)
    print("SOVEREIGN COMPLIANCE AUDIT: CodeValidatorAgent")
    print("=" * 80)

    validator = CodeValidatorAgent()
    policy_engine_dir = project_root / "agentic_core" / "L5_safety" / "policy_engine"

    result = validator.heal_repository(policy_engine_dir)

    print("\nResults:")
    print(f"  Violations Found: {result.get('violations_found', 0)}")
    print(f"  Violations Fixed: {result.get('violations_fixed', 0)}")
    print(f"  Status: {result.get('status', 'UNKNOWN')}")
    print(f"  Execution Time: {result.get('execution_time_ms', 0):.2f}ms")

    if result.get("error_message"):
        print(f"  Error: {result['error_message']}")

    return result


def run_structure_enforcer():
    """Run StructureEnforcerAgent on policy_engine directory."""
    print("\n" + "=" * 80)
    print("SOVEREIGN COMPLIANCE AUDIT: StructureEnforcerAgent")
    print("=" * 80)

    enforcer = StructureEnforcerAgent()
    policy_engine_dir = project_root / "agentic_core" / "L5_safety" / "policy_engine"

    result = enforcer.heal_repository(policy_engine_dir)

    print("\nResults:")
    print(f"  Violations Found: {result.get('violations_found', 0)}")
    print(f"  Violations Fixed: {result.get('violations_fixed', 0)}")
    print(f"  Status: {result.get('status', 'UNKNOWN')}")
    print(f"  Execution Time: {result.get('execution_time_ms', 0):.2f}ms")

    if result.get("error_message"):
        print(f"  Error: {result['error_message']}")

    return result


def main():
    """Run sovereign compliance audit."""
    print("\n" + "=" * 80)
    print("PHASE 7: SOVEREIGN COMPLIANCE AUDIT")
    print("=" * 80)
    print(f"Target: {project_root / 'agentic_core' / 'L5_safety' / 'policy_engine'}")
    print()

    # Run validators
    code_result = run_code_validator()
    structure_result = run_structure_enforcer()

    # Summary
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)

    total_violations = code_result.get("violations_found", 0) + structure_result.get(
        "violations_found", 0
    )
    total_fixed = code_result.get("violations_fixed", 0) + structure_result.get(
        "violations_fixed", 0
    )

    print(f"Total Violations Found: {total_violations}")
    print(f"Total Violations Fixed: {total_fixed}")

    code_status = code_result.get("status", "UNKNOWN")
    structure_status = structure_result.get("status", "UNKNOWN")

    if code_status == "PASS" and structure_status == "PASS":
        print("\n✅ SOVEREIGN COMPLIANCE: VERIFIED")
        return 0
    else:
        print("\n⚠️  COMPLIANCE STATUS:")
        print(f"   CodeValidator: {code_status}")
        print(f"   StructureEnforcer: {structure_status}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
