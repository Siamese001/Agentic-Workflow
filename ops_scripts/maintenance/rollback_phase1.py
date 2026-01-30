#!/usr/bin/env python3
"""
Phase 1 Rollback Script
Rolls back Phase 1 migration if needed.
"""

import pathlib
import shutil
import sys


def rollback_phase1():
    """Rollback Phase 1 migration."""
    BASE_DIR = pathlib.Path(__file__).parent.parent.parent

    rollbacks = [
        (
            "tests/e2e/ops_scripts/maintenance/test_manifest_completion.py",
            "ops_scripts/maintenance/test_manifest_completion.py",
        ),
    ]

    print("🔄 Rolling back Phase 1 migration...")
    print("=" * 50)

    for src_rel, dest_rel in rollbacks:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        if src.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            print(f"✅ Rolled back: {src_rel} → {dest_rel}")
        else:
            print(f"⚠️ Source not found: {src_rel}")

    print("\n🎉 Phase 1 rollback completed!")
    return True


if __name__ == "__main__":
    success = rollback_phase1()
    sys.exit(0 if success else 1)
