#!/usr/bin/env python3
"""Clean up root files and move them to appropriate locations."""

import shutil
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
    get_validated_project_root,
)


def main():
    """Clean up root files."""
    root = get_validated_project_root()

    # Files to move to docs/reports/audit
    audit_files = [
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

    # Files to move to docs/reports/assessments
    assessment_files = [
        "COMPREHENSIVE_TEST_CASES.md",
        "Design Principles.md",
        "Prompt v4.7 Gap Analysis.md",
        "pre_commit_scope_analysis.md",
    ]

    # Scripts to move to ops_scripts/maintenance
    script_files = [
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

    # Test files to move to tests/
    test_files = [
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

    # Config files to keep in root (whitelist)

    print("=" * 70)
    print("ROOT CLEANUP: MOVING FILES TO APPROPRIATE TERRITORIES")
    print("=" * 70)
    print()

    # Move audit files
    print("[1/4] Moving audit files to docs/reports/audit...")
    audit_dir = root / "docs" / "reports" / "audit"
    for filename in audit_files:
        source = root / filename
        if source.exists():
            target = audit_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ {filename}")

    # Move assessment files
    print()
    print("[2/4] Moving assessment files to docs/reports/assessments...")
    assessment_dir = root / "docs" / "reports" / "assessments"
    for filename in assessment_files:
        source = root / filename
        if source.exists():
            target = assessment_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ {filename}")

    # Move script files
    print()
    print("[3/4] Moving scripts to ops_scripts/maintenance...")
    scripts_dir = root / OPS_SCRIPTS_DIR / "maintenance"
    for filename in script_files:
        source = root / filename
        if source.exists():
            target = scripts_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ {filename}")

    # Move test files
    print()
    print("[4/4] Moving test files to tests/...")
    tests_dir = root / TESTS_DIR
    for filename in test_files:
        source = root / filename
        if source.exists():
            target = tests_dir / filename
            shutil.move(str(source), str(target))
            print(f"  ✓ {filename}")

    print()
    print("=" * 70)
    print("ROOT CLEANUP COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
