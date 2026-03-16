#!/usr/bin/env python3
"""
Utility Silent Swallower CI Guardrail

Enforces zero tolerance for silent failures in governance-critical utility scripts.
Implements Windsurf Hardening Response requirements for control-plane integrity.

Usage:
    python ops_scripts/ci/check_utility_silent_swallowers.py [file1.py file2.py ...]

Exit codes:
    0 - No violations
    1 - Violations found (build fails)
"""

import argparse

# Force UTF-8 encoding for Windows compatibility
import io
import json
import sys
from pathlib import Path
from typing import List

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "check_utility_silent_swallowers")
_emit_applies_guardrail("p0", "check_utility_silent_swallowers", "p0_governance")
_emit_reads_policy_state("p0", "check_utility_silent_swallowers", "policy_binding")
_emit_snapshots_state("p0", "check_utility_silent_swallowers", "state_snapshot")
emit_replay_key("p0", "check_utility_silent_swallowers")
emit_determinism_digest("p0", "check_utility_silent_swallowers")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.L5_safety.validators.utility_silent_swallower_validator import (
    UtilitySilentSwallowerDetector,
)

PROJECT_ROOT = get_validated_project_root()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check utility scripts for silent swallowers")
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (default: all Python files in governance paths)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Determine files to scan
    if args.files:
        files_to_scan = [Path(f) for f in args.files if f.endswith('.py')]
    else:
        files_to_scan = get_governance_files()

    if not files_to_scan:
        print("✅ No governance files to scan")
        return 0

    # Scan for violations
    detector = UtilitySilentSwallowerDetector(PROJECT_ROOT)
    all_violations = []

    for file_path in files_to_scan:
        if file_path.exists():
            detection_result = detector.scan_file(file_path)
            all_violations.extend(detection_result.violations)

    # Report results
    if args.json:
        report_json(all_violations, args.verbose)
    else:
        report_text(all_violations, args.verbose)

    # Fail build if any violations found
    if all_violations:
        print(f"\n❌ CI GUARDRAIL: {len(all_violations)} utility silent swallower violations found")
        print("Build FAILED - governance scripts must fail loudly")
        return 1
    else:
        print(f"\n✅ CI GUARDRAIL: No utility silent swallower violations in {len(files_to_scan)} governance files")
        return 0


def get_governance_files() -> list[Path]:
    """Get all Python files in governance-critical paths."""
    governance_paths = [
        "ops_scripts/ci",
        "ops_scripts/maintenance",
        "ops_scripts/root_scripts",
        "tests/guardian",
        "tests/governance",
        "tests/integration",
        "tests/performance",
        "agentic_core/L5_safety/validators",
        "agentic_core/L5_safety/static_checks",
    ]

    files = []
    for path in governance_paths:
        full_path = PROJECT_ROOT / path
        if full_path.exists():
            files.extend(full_path.rglob("*.py"))

    return sorted(files)


def report_text(violations: list, verbose: bool = False) -> None:
    """Report violations in text format."""
    if not violations:
        print("✅ No utility silent swallower violations found")
        return

    print(f"❌ Found {len(violations)} utility silent swallower violations:")
    print()

    # Group violations by file
    by_file = {}
    for v in violations:
        file_key = str(v.file_path)
        if file_key not in by_file:
            by_file[file_key] = []
        by_file[file_key].append(v)

    for file_path, file_violations in sorted(by_file.items()):
        rel_path = Path(file_path).relative_to(PROJECT_ROOT)
        print(f"📁 {rel_path}")

        for v in sorted(file_violations, key=lambda x: x.line_number):
            print(f"   Line {v.line_number}: {v.message}")
            if verbose:
                print(f"   Suggestion: {v.suggestion}")
        print()


def report_json(violations: list, verbose: bool = False) -> None:
    """Report violations in JSON format."""
    report_data = {
        "status": "failed" if violations else "passed",
        "total_violations": len(violations),
        "violations": []
    }

    for v in violations:
        violation_data = {
            "file": str(v.file_path.relative_to(PROJECT_ROOT)),
            "line": v.line_number,
            "column": v.column_number,
            "message": v.message,
            "category": v.category.value,
            "enforcement_level": v.enforcement_level.value,
            "suggestion": v.suggestion
        }
        if verbose:
            violation_data["details"] = v.details
        report_data["violations"].append(violation_data)

    print(json.dumps(report_data, indent=2))


if __name__ == "__main__":
    sys.exit(main())
