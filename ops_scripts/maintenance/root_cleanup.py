#!/usr/bin/env python3
"""Clean up root files and move them to appropriate locations."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    REPORTS_DIR,
    TESTS_DIR,
    get_validated_project_root,
)


PROJECT_ROOT = get_validated_project_root()
AUDIT_FILES = [
    "audit_gap_analysis.json",
    "consolidation_candidates.json",
    "DELETION_AUDIT_REPORT.md",
    "depth_violations.txt",
    "gravity_violations.json",
    "guardian_report.txt",
    "HANG_DEBUG_REPORT.md",
    "import_crawl_error.txt",
    "import_errors.txt",
    "init_missing.txt",
    "naming_violations.txt",
    "Phase2_Discovery_Report.md",
    "ssot_recommendations_report.md",
    "TARGET_STATE_GAP_ASSESSMENT_REPORT.md",
]
ASSESSMENT_FILES = [
    "COMPREHENSIVE_TEST_CASES.md",
    "Design Principles.md",
    "Prompt v4.7 Gap Analysis.md",
    "pre_commit_scope_analysis.md",
]
SCRIPT_FILES = [
    "agent_technical_status.py",
    "analyze_deleted_tests.py",
    "batch_restore_tests.py",
    "consolidate_phase_files.py",
    "implement_phase1_renames.py",
    "phase1_1_rename_validators.py",
    "restore_valid_tests.py",
    "root_drift_remediation.py",
    "run_classification.py",
]
TEST_FILES = [
    "test_always_heal_llm.py",
    "test_execute_ssot_e2e.py",
    "test_healing_confidence.py",
    "test_heal_implementations.py",
    "test_location_agent_heal.py",
    "test_location_agent_integration.py",
    "test_location_semantic_lock.py",
    "test_phase1_renames.py",
    "test_phase2_renames.py",
    "test_phase3_renames.py",
    "test_schema_validator.py",
    "test_sovereign_index_e2e.py",
]


def move_file(source: Path, destination: Path, execute: bool) -> bool:
    if not source.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    if execute:
        shutil.move(str(source), str(destination))
        print(f"  ✓ moved {source.relative_to(PROJECT_ROOT)} -> {destination.relative_to(PROJECT_ROOT)}")
    else:
        print(
            f"  [DRY-RUN] Would move {source.relative_to(PROJECT_ROOT)} -> {destination.relative_to(PROJECT_ROOT)}"
        )
    return True


def main(execute: bool = False) -> int:
    audit_dir = PROJECT_ROOT / "docs" / REPORTS_DIR / "audit"
    assessments_dir = PROJECT_ROOT / "docs" / REPORTS_DIR / "assessments"
    scripts_dir = PROJECT_ROOT / OPS_SCRIPTS_DIR
    tests_dir = PROJECT_ROOT / TESTS_DIR

    print("=" * 70)
    print("ROOT CLEANUP: MOVING FILES TO APPROPRIATE TERRITORIES")
    print("=" * 70)
    print(f"Mode: {'EXECUTE' if execute else 'DRY-RUN'}")

    moved = 0

    print("\n[1/4] Moving audit files to docs/reports/audit...")
    for filename in AUDIT_FILES:
        moved += int(move_file(PROJECT_ROOT / filename, audit_dir / filename, execute=execute))

    print("\n[2/4] Moving assessment files to docs/reports/assessments...")
    for filename in ASSESSMENT_FILES:
        moved += int(move_file(PROJECT_ROOT / filename, assessments_dir / filename, execute=execute))

    print(f"\n[3/4] Moving scripts to {OPS_SCRIPTS_DIR}...")
    for filename in SCRIPT_FILES:
        moved += int(move_file(PROJECT_ROOT / filename, scripts_dir / filename, execute=execute))

    print(f"\n[4/4] Moving tests to {TESTS_DIR}...")
    for filename in TEST_FILES:
        moved += int(move_file(PROJECT_ROOT / filename, tests_dir / filename, execute=execute))

    print(f"\nCleanup complete. Total files moved: {moved}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move stray root files into their appropriate territories.")
    parser.add_argument("--execute", action="store_true", help="Perform moves. Default is dry-run.")
    raise SystemExit(main(execute=parser.parse_args().execute))
