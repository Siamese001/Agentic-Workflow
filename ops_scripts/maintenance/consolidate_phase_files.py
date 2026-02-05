#!/usr/bin/env python3
"""
Consolidate phase test files into single comprehensive test files.

Following the principle: If tests have value, they should be consolidated,
not kept as separate phase1, phase2, phase3 files.
"""

import re
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def find_phase_files() -> dict:
    """Find all phase files and group them by base name."""
    tests_dir = PROJECT_ROOT / "tests" / "unit"

    phase_groups = defaultdict(list)

    for py_file in tests_dir.rglob("*phase*.py"):
        if py_file.name == "__init__.py":
            continue

        # Extract base name (remove phase number)
        base_name = re.sub(r"_phase\d+[a-z]?(_[a-z_]+)?\.py$", "", py_file.name)
        base_name = re.sub(r"_phase\d+[a-z]?\.py$", "", base_name)

        # Group by directory + base name
        rel_dir = py_file.parent.relative_to(tests_dir)
        key = (str(rel_dir), base_name)

        phase_groups[key].append(py_file)

    return phase_groups


def analyze_phase_groups(phase_groups: dict) -> dict:
    """Analyze phase groups to determine consolidation strategy."""
    analysis = {}

    for (rel_dir, base_name), files in phase_groups.items():
        if len(files) <= 1:
            continue

        # Sort files by phase number
        def get_phase_num(f):
            match = re.search(r"phase(\d+)", f.name)
            return int(match.group(1)) if match else 0

        files.sort(key=get_phase_num)

        analysis[(rel_dir, base_name)] = {
            "files": files,
            "count": len(files),
            "phases": [get_phase_num(f) for f in files],
            "total_lines": sum(f.stat().st_size for f in files),
        }

    return analysis


def main():
    """Main analysis function."""
    print("=" * 80)
    print("PHASE FILE CONSOLIDATION ANALYSIS")
    print("=" * 80)

    phase_groups = find_phase_files()
    analysis = analyze_phase_groups(phase_groups)

    # Sort by count (most files first)
    sorted_groups = sorted(analysis.items(), key=lambda x: -x[1]["count"])

    total_phase_files = sum(a["count"] for a in analysis.values())

    print(f"\nTotal phase file groups: {len(analysis)}")
    print(f"Total phase files: {total_phase_files}")

    print("\n" + "=" * 80)
    print("GROUPS TO CONSOLIDATE")
    print("=" * 80)

    files_to_delete = []

    for (rel_dir, base_name), info in sorted_groups:
        print(f"\n### {rel_dir}/{base_name} ({info['count']} files)")
        print(f"    Phases: {info['phases']}")
        for f in info["files"]:
            print(f"    - {f.name}")
            files_to_delete.append(f)

    print("\n" + "=" * 80)
    print("DELETION COMMANDS")
    print("=" * 80)

    print("\n# Run these commands to delete phase files after consolidation:")
    for f in files_to_delete:
        rel_path = f.relative_to(PROJECT_ROOT)
        print(f'Remove-Item -Path "{rel_path}" -Force')

    print(f"\n# Total files to delete: {len(files_to_delete)}")

    return files_to_delete


if __name__ == "__main__":
    files_to_delete = main()
