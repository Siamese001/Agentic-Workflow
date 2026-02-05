#!/usr/bin/env python3
"""
Phase 1: LOW Risk Migration - 1 file
Migrates ops_scripts/maintenance/test_manifest_completion.py to tests/e2e/ops_scripts/maintenance/
"""

import pathlib
import shutil
import sys


def main():
    """Execute Phase 1 migration."""
    BASE_DIR = pathlib.Path(__file__).parent.parent.parent

    migrations = [
        (
            "ops_scripts/maintenance/test_manifest_completion.py",
            "tests/e2e/ops_scripts/maintenance/test_manifest_completion.py",
        ),
    ]

    print("🚀 Starting Phase 1: LOW Risk Migration")
    print("=" * 50)

    # Pre-migration checks
    print("📋 Pre-migration checks...")

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        if not src.exists():
            print(f"❌ Source file not found: {src}")
            return False

        print(f"✅ Source exists: {src_rel}")

    # Create backup
    print("\n💾 Creating backup...")
    backup_dir = BASE_DIR / ".backup" / "phase1"
    backup_dir.mkdir(parents=True, exist_ok=True)

    for src_rel, _ in migrations:
        src = BASE_DIR / src_rel
        backup_file = backup_dir / src.name
        shutil.copy2(src, backup_file)
        print(f"✅ Backed up: {src.name}")

    print("\n📝 Note: Rollback script available at ops_scripts/maintenance/rollback_phase1.py")

    # Execute migration
    print("\n🔄 Executing migration...")

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        # Create destination directory
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        shutil.move(str(src), str(dest))
        print(f"✅ Moved: {src_rel} → {dest_rel}")

    # Post-migration verification
    print("\n🔍 Post-migration verification...")

    for src_rel, dest_rel in migrations:
        src = BASE_DIR / src_rel
        dest = BASE_DIR / dest_rel

        if src.exists():
            print(f"❌ Source still exists: {src_rel}")
            return False

        if not dest.exists():
            print(f"❌ Destination not found: {dest_rel}")
            return False

        print(f"✅ Migration verified: {dest_rel}")

    print("\n🎉 Phase 1 migration completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
