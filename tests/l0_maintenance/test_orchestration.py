#!/usr/bin/env python3
"""
Test script to run SSOT Orchestration after syntax remediation.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L3_orchestration.workflow_engines.SSOTOrchestratorAgent import (
    SSOTOrchestratorAgent,
)


def main():
    project_root = Path(__file__).parent.parent

    print("=" * 60)
    print("SSOT ORCHESTRATION - Post-Syntax Remediation Test")
    print("=" * 60)
    print()

    # Initialize orchestrator
    orchestrator = SSOTOrchestratorAgent(project_root=project_root)

    # Run orchestration with full healing enabled
    # Triggering full healing and Meta-Learning write-loop
    result = orchestrator.heal_repository(dry_run=False, execute=True)

    # Print results
    print()
    print("=" * 60)
    print("ORCHESTRATION RESULTS")
    print("=" * 60)
    print(f"Status: {result.get('status')}")
    print(f"Agents Run: {result.get('agents_run')}")
    print(f"Agents Passed: {result.get('agents_passed')}")
    print(f"Agents Failed: {result.get('agents_failed')}")
    print(f"Total Violations: {result.get('violations_found')}")
    print(f"Total Fixes: {result.get('violations_fixed')}")
    print(f"Success Rate: {result.get('success_rate', 0):.1f}%")
    print(f"Execution Time: {result.get('execution_time_ms', 0):.0f}ms")
    print("=" * 60)

    # Meta-Learning status
    if result.get('status') == 'PASS' and result.get('violations_fixed', 0) > 0:
        print(f"\n✅ Meta-Learning Enabled: {result.get('violations_fixed')} fixes recorded to L4 State.")

    return 0 if result.get('status') == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
