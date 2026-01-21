#!/usr/bin/env python3
"""
DASHBOARD SSOT VALIDATOR
Enforces that all files use DASHBOARD_DIR from structure_blueprint.py
Detects hardcoded dashboard paths and reports violations.
"""
import re
from pathlib import Path

# Import SSOT
from agentic_core.L5_safety.validators.structure_blueprint import (
    DASHBOARD_DIR,
    get_validated_project_root,
)

# Patterns that indicate hardcoded dashboard paths
HARDCODED_PATTERNS = [
    r'["\']agentic_core/L6_observability/dashboards["\']',
    r'Path\(["\'].*L6_observability/dashboards.*["\']\)',
    r'["\']C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards["\']',
    r'os\.path\.join\(.*["\']L6_observability["\'].*["\']dashboards["\']\)',
]

# Files/directories to exclude from validation
EXCLUDE_PATTERNS = [
    '.git',
    '__pycache__',
    '.venv',
    'venv',
    'node_modules',
    'archives',
    'legacy_',
    '.pytest_cache',
    'structure_blueprint.py',  # SSOT definition file itself
    'validate_dashboard_ssot.py',  # This file
]

def should_exclude(file_path: Path) -> bool:
    """Check if file should be excluded from validation."""
    path_str = str(file_path)
    return any(pattern in path_str for pattern in EXCLUDE_PATTERNS)

def check_file_for_hardcoded_paths(file_path: Path) -> list[tuple[int, str]]:
    """
    Check a single file for hardcoded dashboard paths.
    Returns list of (line_number, matched_pattern) tuples.
    """
    violations = []

    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip lines that import DASHBOARD_DIR (legitimate usage)
            if 'from agentic_core.L5_safety.validators.structure_blueprint import' in line:
                continue
            if 'DASHBOARD_DIR' in line and 'import' in line:
                continue

            # Check for hardcoded patterns
            for pattern in HARDCODED_PATTERNS:
                if re.search(pattern, line):
                    violations.append((line_num, line.strip()))
                    break

    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")

    return violations

def validate_dashboard_ssot() -> tuple[bool, list[str]]:
    """
    Validate that all files use DASHBOARD_DIR SSOT.
    Returns (is_valid, list_of_violations).
    """
    project_root = get_validated_project_root()
    violations_report = []
    total_violations = 0

    print("=" * 80)
    print("DASHBOARD SSOT VALIDATION")
    print("=" * 80)
    print("\n📍 SSOT Location: structure_blueprint.py")
    print(f"📂 SSOT Value: {DASHBOARD_DIR}")
    print(f"🔍 Scanning project: {project_root}\n")

    # Scan all Python files
    # Final True 20: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(project_root):
        if should_exclude(py_file):
            continue

        violations = check_file_for_hardcoded_paths(py_file)
        if violations:
            total_violations += len(violations)
            rel_path = py_file.relative_to(project_root)
            violations_report.append(f"\n❌ {rel_path}")
            for line_num, line in violations:
                violations_report.append(f"   Line {line_num}: {line}")

    # Print results
    if total_violations == 0:
        print("✅ ALL FILES COMPLIANT - No hardcoded dashboard paths found!")
        print("✅ All files correctly use DASHBOARD_DIR from structure_blueprint.py")
        return True, []
    else:
        print(f"❌ FOUND {total_violations} VIOLATIONS\n")
        print("Files with hardcoded dashboard paths:")
        for line in violations_report:
            print(line)
        print("\n" + "=" * 80)
        print("REMEDIATION REQUIRED:")
        print("=" * 80)
        print("Replace hardcoded paths with:")
        print("  from agentic_core.L5_safety.validators.structure_blueprint import DASHBOARD_DIR")
        print("  dashboard_path = project_root / DASHBOARD_DIR")
        print("=" * 80)
        return False, violations_report

if __name__ == "__main__":
    is_valid, violations = validate_dashboard_ssot()
    exit(0 if is_valid else 1)
