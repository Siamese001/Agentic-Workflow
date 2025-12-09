#!/usr/bin/env python3
"""
TEST STRUCTURE AUDIT — YAML COMPLIANCE CHECK
=============================================
Audits tests/ folder against unified_structure_subatomic_meta.yaml taxonomy.
Identifies violations and generates compliance report.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent.resolve()
TESTS_ROOT = REPO_ROOT / "tests"

# YAML-defined test taxonomy (from unified_structure_subatomic_meta.yaml)
YAML_TAXONOMY = {
    "unit": [
        "agentic_core",
        "apps_lic",
        "apps_rg",
        "runtime",
        "data",
        "schemas",
        "prompt_governance",
        "config",
        "observability",
        "scripts",
        # Additional allowed (not in YAML but valid)
        "shared",
        "shared_engine_ops",
    ],
    "integration": [
        "core_plus_runtime",
        "lic_plus_data",
        "rg_plus_data",
        "full_pipeline",
        # Additional found
        "api",
        "cross_domain",
        "workflow",
    ],
    "e2e": [
        "outreach_flows",
        "resume_flows",
        "admin_flows",
    ],
    "golden": [
        "prompts",
        "semantics",
        "safety",
    ],
    "perf": [
        "latency",
        "throughput",
        "cost",
    ],
    "load": [
        "spike",
        "soak",
    ],
}

# Forbidden patterns in test paths (L1-L5, P1-P4 mirroring)
FORBIDDEN_PATTERNS = [
    "L1_cognition",
    "L2_execution",
    "L3_orchestration",
    "L4_memory",
    "L5_safety",
    "P1_retrieve",
    "P2_inspect",
    "P3_aggregate",
    "P4_safety",
]

# Banned folder names
BANNED_FOLDERS = ["logic"]  # Not in YAML taxonomy


def collect_test_files() -> List[Path]:
    """Collect all test files."""
    return [f for f in TESTS_ROOT.rglob("test_*.py")]


def collect_test_dirs() -> List[Path]:
    """Collect all test directories."""
    return [d for d in TESTS_ROOT.rglob("*") if d.is_dir()]


def check_forbidden_patterns(path: Path) -> List[str]:
    """Check if path contains forbidden L/P patterns."""
    violations = []
    path_str = str(path.relative_to(TESTS_ROOT))

    for pattern in FORBIDDEN_PATTERNS:
        if pattern in path_str:
            violations.append(pattern)

    return violations


def check_banned_folders(path: Path) -> List[str]:
    """Check if path is in a banned folder."""
    violations = []
    parts = path.relative_to(TESTS_ROOT).parts

    for part in parts:
        if part in BANNED_FOLDERS:
            violations.append(part)

    return violations


def get_test_category(path: Path) -> Tuple[str, str]:
    """Get the test category (unit/integration/e2e/etc) and subcategory."""
    rel_path = path.relative_to(TESTS_ROOT)
    parts = rel_path.parts

    if len(parts) >= 1:
        category = parts[0]
        subcategory = parts[1] if len(parts) >= 2 else None
        return category, subcategory

    return None, None


def audit_tests() -> Dict:
    """Run full audit of test structure."""
    report = {
        "summary": {
            "total_test_files": 0,
            "total_test_dirs": 0,
            "yaml_compliant": 0,
            "violations": 0,
        },
        "violations": {
            "forbidden_lp_patterns": [],
            "banned_folders": [],
            "unknown_categories": [],
        },
        "coverage": {
            "unit": defaultdict(list),
            "integration": defaultdict(list),
            "e2e": defaultdict(list),
            "golden": defaultdict(list),
            "perf": defaultdict(list),
            "load": defaultdict(list),
        },
        "recommendations": [],
    }

    test_files = collect_test_files()
    test_dirs = collect_test_dirs()

    report["summary"]["total_test_files"] = len(test_files)
    report["summary"]["total_test_dirs"] = len(test_dirs)

    # Check each test file
    for test_file in test_files:
        rel_path = str(test_file.relative_to(TESTS_ROOT))
        category, subcategory = get_test_category(test_file)

        # Check for forbidden L/P patterns
        lp_violations = check_forbidden_patterns(test_file)
        if lp_violations:
            report["violations"]["forbidden_lp_patterns"].append({
                "file": rel_path,
                "patterns": lp_violations,
            })
            report["summary"]["violations"] += 1

        # Check for banned folders
        banned = check_banned_folders(test_file)
        if banned:
            report["violations"]["banned_folders"].append({
                "file": rel_path,
                "folders": banned,
            })
            report["summary"]["violations"] += 1

        # Check category validity
        if category and category in YAML_TAXONOMY:
            if subcategory:
                report["coverage"][category][subcategory].append(test_file.name)
            report["summary"]["yaml_compliant"] += 1
        elif category and category not in ["__pycache__"]:
            if category not in [v["category"] for v in report["violations"]["unknown_categories"]]:
                report["violations"]["unknown_categories"].append({
                    "category": category,
                    "file": rel_path,
                })

    # Generate recommendations
    if report["violations"]["forbidden_lp_patterns"]:
        report["recommendations"].append(
            "CRITICAL: Remove L1-L5/P1-P4 folder mirroring in unit tests. "
            "Tests should be organized by domain (agentic_core, apps_lic, etc.) not by cognitive layer."
        )

    if report["violations"]["banned_folders"]:
        report["recommendations"].append(
            f"Remove banned folders: {BANNED_FOLDERS}. Move tests to appropriate YAML-defined categories."
        )

    # Check for missing coverage
    for category, expected_subs in YAML_TAXONOMY.items():
        actual_subs = set(report["coverage"].get(category, {}).keys())
        missing = set(expected_subs) - actual_subs
        if missing:
            report["recommendations"].append(
                f"Missing test coverage in {category}/: {', '.join(missing)}"
            )

    return report


def print_report(report: Dict) -> None:
    """Print formatted audit report."""
    print("=" * 70)
    print("TEST STRUCTURE AUDIT REPORT")
    print("=" * 70)

    print("\n## SUMMARY")
    print(f"  Total test files: {report['summary']['total_test_files']}")
    print(f"  Total test dirs:  {report['summary']['total_test_dirs']}")
    print(f"  YAML compliant:   {report['summary']['yaml_compliant']}")
    print(f"  Violations:       {report['summary']['violations']}")

    if report["violations"]["forbidden_lp_patterns"]:
        print("\n## VIOLATIONS: L/P Pattern Mirroring (CRITICAL)")
        for v in report["violations"]["forbidden_lp_patterns"][:10]:
            print(f"  ✗ {v['file']}")
            print(f"    Patterns: {', '.join(v['patterns'])}")
        if len(report["violations"]["forbidden_lp_patterns"]) > 10:
            print(f"  ... and {len(report['violations']['forbidden_lp_patterns']) - 10} more")

    if report["violations"]["banned_folders"]:
        print("\n## VIOLATIONS: Banned Folders")
        for v in report["violations"]["banned_folders"]:
            print(f"  ✗ {v['file']}")

    if report["violations"]["unknown_categories"]:
        print("\n## VIOLATIONS: Unknown Categories")
        for v in report["violations"]["unknown_categories"]:
            print(f"  ✗ {v['category']}/")

    print("\n## COVERAGE BY CATEGORY")
    for category in ["unit", "integration", "e2e", "golden", "perf", "load"]:
        subs = report["coverage"].get(category, {})
        total = sum(len(files) for files in subs.values())
        print(f"\n  {category}/ ({total} tests)")
        for sub, files in sorted(subs.items()):
            print(f"    {sub}/: {len(files)} tests")

    if report["recommendations"]:
        print("\n## RECOMMENDATIONS")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")

    print("\n" + "=" * 70)


def main():
    report = audit_tests()
    print_report(report)

    # Save report
    report_path = REPO_ROOT / "test_structure_audit_report.json"

    # Convert defaultdicts to regular dicts for JSON serialization
    report["coverage"] = {k: dict(v) for k, v in report["coverage"].items()}

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nReport saved to: {report_path}")

    return report


if __name__ == "__main__":
    main()
