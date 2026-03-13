"""
Hygiene Guardian Naming Audit Runner
-------------------------------------
Scans the codebase for filename length violations (>5 words).
"""

import sys
from pathlib import Path

root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(root))
from agentic_core.L0_routing.seams.safety_validators_seam import load_hygiene_guardian


def main():
    root = Path(__file__).parent.parent
    HygieneGuardianAgent = load_hygiene_guardian()
    guardian = HygieneGuardianAgent(project_root=root)
    print("=" * 80)
    print("HYGIENE GUARDIAN: FILENAME LENGTH AUDIT")
    print("=" * 80)
    print(f"Scanning: {root}")
    print("Max words allowed: 5")
    print()
    violations = guardian.audit_naming_conventions()
    if violations:
        print(f"\n{'=' * 80}")
        print(f"SUMMARY: Found {len(violations)} files exceeding word limit")
        print(f"{'=' * 80}\n")
        by_count = {}
        for v in violations:
            count = v["current_count"]
            by_count.setdefault(count, []).append(v)
        for count in sorted(by_count.keys(), reverse=True):
            viols = by_count[count]
            print(f"\n{count} WORDS ({len(viols)} files):")
            for v in viols[:10]:
                print(f"  - {v['file']}")
                print(f"    Suggested: {v['suggestion']}")
            if len(viols) > 10:
                print(f"  ... and {len(viols) - 10} more")
    else:
        print("\n✅ All filenames comply with word limit!")


if __name__ == "__main__":
    main()
