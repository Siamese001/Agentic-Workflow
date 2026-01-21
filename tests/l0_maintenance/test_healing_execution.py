#!/usr/bin/env python3
"""Test healing execution and get full summary."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L5_safety.validators.AutonomyGuardianAgent import get_autonomy_guardian

def main():
    project_root = Path(__file__).parent.parent
    guardian = get_autonomy_guardian(project_root)

    print("\n" + "=" * 80)
    print("EXECUTING AUTONOMOUS HEALING")
    print("=" * 80)

    result = guardian.heal_repository(dry_run=False, execute=True)

    print("\n" + "=" * 80)
    print("HEALING SUMMARY")
    print("=" * 80)
    print(f"Violations Found: {result.get('violations', 0)}")
    print(f"Agents Fixed: {result.get('fixed', 0)}")
    print(f"Errors: {result.get('errors', 0)}")
    print("=" * 80)

    return 0 if result.get('errors', 0) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
