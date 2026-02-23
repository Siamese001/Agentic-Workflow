#!/usr/bin/env python3
"""Seed Direct Writes violations into baseline."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L5_safety.static_checks.write_gateway_enforcer import (
    scan_repository_for_writes,
)


def main():
    repo_root = Path.cwd()
    baseline_file = repo_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    # Scan for direct writes
    violations = scan_repository_for_writes(repo_root)

    # Read existing baseline
    existing = set()
    if baseline_file.exists():
        with open(baseline_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    existing.add(line)

    # Add direct write violations
    new_count = 0
    for file_path, lineno, rule_id, snippet in violations:
        violation_key = f"{file_path}:{lineno}:{rule_id}:{snippet}"
        if violation_key not in existing:
            existing.add(violation_key)
            new_count += 1

    # Write back sorted
    with open(baseline_file, 'w', encoding='utf-8') as f:
        f.write("# Static invariant baseline violations\n")
        f.write("# Format: path:lineno:rule_id:excerpt\n")
        f.write("#\n")
        for violation in sorted(existing):
            f.write(f"{violation}\n")

    print(f"Added {new_count} Direct Writes violations to baseline")
    print(f"Total baseline violations: {len(existing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
