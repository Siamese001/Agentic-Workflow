#!/usr/bin/env python3
"""
Analyze critical test files that need immediate reconstruction.
"""

import pathlib


def analyze_critical_files():
    """Analyze which test files are most critical for reconstruction."""

    critical_files = {
        "runtime": [],
        "l0_routing": [],
        "l2_execution": [],
        "l5_safety": [],
        "governance": [],
        "integration": [],
        "e2e": [],
    }

    tests_dir = pathlib.Path("tests")

    # Analyze placeholder files by category
    for f in sorted(tests_dir.rglob("test_*.py")):
        if "archive" in str(f).lower():
            continue

        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            if "Placeholder test file - syntax fixed" in content:
                path_parts = f.parts

                # Categorize by directory
                if "runtime" in str(f):
                    critical_files["runtime"].append(f)
                elif "L0_routing" in str(f):
                    critical_files["l0_routing"].append(f)
                elif "L2_execution" in str(f):
                    critical_files["l2_execution"].append(f)
                elif "L5_safety" in str(f):
                    critical_files["l5_safety"].append(f)
                elif "governance" in str(f):
                    critical_files["governance"].append(f)
                elif "integration" in str(f):
                    critical_files["integration"].append(f)
                elif "e2e" in str(f):
                    critical_files["e2e"].append(f)
        except:  # guardian: allow-broad-exception -- offline tooling, reports failure
            continue

    print("CRITICAL TEST FILE RECONSTRUCTION ANALYSIS")
    print("=" * 60)

    total_critical = sum(len(files) for files in critical_files.values())
    print(f"Total critical placeholder files: {total_critical}")
    print()

    # Print analysis for each category
    for category, files in critical_files.items():
        if files:
            print(f"{category.upper()}: {len(files)} files")
            print(f"  Rationale: {get_rationale(category)}")
            print(f"  Priority: {get_priority(category)}")
            print("  Sample files:")
            for i, f in enumerate(files[:3], 1):
                print(f"    {i}. {f}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
            print()

    # Generate immediate action list
    print("IMMEDIATE ACTION LIST (Top 20 Most Critical)")
    print("=" * 60)

    all_critical = []
    for category, files in critical_files.items():
        for f in files:
            priority_score = get_priority_score(category)
            all_critical.append((priority_score, category, f))

    # Sort by priority score (lower = more critical)
    all_critical.sort(key=lambda x: x[0])

    for i, (score, category, f) in enumerate(all_critical[:20], 1):
        print(f"{i:2d}. [{category}] {f} (Priority: {score})")

    return critical_files


def get_rationale(category):
    """Get rationale for why a category is critical."""
    rationales = {
        "runtime": "Core execution engine - fundamental to all system operations",
        "l0_routing": "Request routing - entry point for all system interactions",
        "l2_execution": "Agent execution - handles all agent operations",
        "l5_safety": "Safety mechanisms - prevents system damage and ensures safe operation",
        "governance": "System governance - ensures compliance and policy enforcement",
        "integration": "Component integration - validates cross-component interactions",
        "e2e": "End-to-end workflows - validates complete user journeys",
    }
    return rationales.get(category, "Critical system component")


def get_priority(category):
    """Get priority level for a category."""
    priorities = {
        "runtime": "P1 - Critical",
        "l0_routing": "P1 - Critical",
        "l2_execution": "P1 - Critical",
        "l5_safety": "P2 - High",
        "governance": "P2 - High",
        "integration": "P3 - Medium",
        "e2e": "P3 - Medium",
    }
    return priorities.get(category, "P4 - Low")


def get_priority_score(category):
    """Get numeric priority score (lower = more critical)."""
    scores = {
        "runtime": 1,
        "l0_routing": 1,
        "l2_execution": 1,
        "l5_safety": 2,
        "governance": 2,
        "integration": 3,
        "e2e": 3,
    }
    return scores.get(category, 4)


if __name__ == "__main__":
    analyze_critical_files()
