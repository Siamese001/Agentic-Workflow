#!/usr/bin/env python3
"""
Phase 5: HIGH Risk Migration Batch 3 - 8 files
Migrate remaining ops_scripts test files and agentic_core L0_maintenance test files
"""

import pathlib
import shutil
import sys


def execute_phase5():
    """Phase 5: HIGH Risk Migration Batch 3 - 8 files"""

    BASE_DIR = pathlib.Path.cwd()

    migrations = [
        # ops_scripts files (6 files)
        ("ops_scripts/test_mission_dry_run.py", "tests/e2e/ops_scripts/test_mission_dry_run.py"),
        (
            "ops_scripts/test_mission_telemetry_dashboard.py",
            "tests/e2e/ops_scripts/test_mission_telemetry_dashboard.py",
        ),
        ("ops_scripts/test_phase1_config.py", "tests/e2e/ops_scripts/test_phase1_config.py"),
        ("ops_scripts/test_phase2_core.py", "tests/e2e/ops_scripts/test_phase2_core.py"),
        ("ops_scripts/test_phase3_base.py", "tests/e2e/ops_scripts/test_phase3_base.py"),
        (
            "ops_scripts/test_phase4_orchestrator.py",
            "tests/e2e/ops_scripts/test_phase4_orchestrator.py",
        ),
        # agentic_core files (2 files - with filename standardization)
        (
            "agentic_core/L0_maintenance/scripts/direct_hierarchy_boundary_test.py",
            "tests/e2e/agentic_core/L0_maintenance/scripts/test_direct_hierarchy_boundary.py",
        ),
        (
            "agentic_core/L0_maintenance/scripts/run_code_dedup_full_test.py",
            "tests/e2e/agentic_core/L0_maintenance/scripts/test_run_code_dedup_full.py",
        ),
    ]

    print("🚀 Starting Phase 5 Migration...")
    print(f"Base directory: {BASE_DIR}")

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        print(f"\n📁 Processing: {src_rel}")

        # Check if source exists
        if not src.exists():
            print(f"⚠️  Source not found: {src}")
            continue

        # Create destination directory
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        try:
            shutil.move(str(src), str(dest))
            print(f"✅ Moved: {src_rel} → {dest_rel}")
        except Exception as e:
            print(f"❌ Failed to move {src_rel}: {e}")
            return False

    print("\n🎉 Phase 5 Migration Complete!")
    print(f"📊 Moved {len(migrations)} files")

    return True


if __name__ == "__main__":
    success = execute_phase5()
    sys.exit(0 if success else 1)
