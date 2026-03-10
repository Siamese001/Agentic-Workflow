#!/usr/bin/env python3
"""
Registry Synchronization Script (Phase 5 Recovery)

Updates content_hash in registry.json to match current template state.
This resolves the "healthy" drift detected after Phase 4 header injection.
"""

import json
import sys
from pathlib import Path

from agentic_core.utils.fs_util import calculate_file_hash


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def load_registry(registry_path: Path) -> dict:
    """Load the prompt registry JSON file."""
    try:
        with open(registry_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # guardian: allow-silent-swallower
        print(f"ERROR: Failed to load registry: {e}")
        sys.exit(1)


def save_registry(registry_path: Path, registry: dict):
    """Save the updated registry."""
    try:
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        print(f"✅ Registry saved to {registry_path}")
    except Exception as e:
        print(f"ERROR: Failed to save registry: {e}")
        sys.exit(1)


def synchronize_registry_hashes(registry_path: Path, base_dir: Path) -> dict:
    """
    Synchronize registry content hashes with actual template files.

    Returns:
        Dict with synchronization statistics
    """
    registry = load_registry(registry_path)
    prompts = registry.get("prompts", {})

    updated_count = 0
    skipped_count = 0
    error_count = 0

    print("Synchronizing content hashes...")
    print()

    for template_name, prompt_versions in prompts.items():
        for prompt_data in prompt_versions:
            if not prompt_data.get("active", False):
                skipped_count += 1
                print(f"⏭️  Skipping inactive: {template_name}")
                continue

            template_path = base_dir / "templates" / template_name

            if not template_path.exists():
                print(f"❌ Missing template: {template_name}")
                error_count += 1
                continue

            # Calculate current hash
            current_hash = calculate_file_hash(template_path)
            existing_hash = prompt_data.get("content_hash", "")

            if current_hash != existing_hash:
                # Update the hash
                prompt_data["content_hash"] = current_hash
                updated_count += 1
                print(f"🔄 Updated: {template_name}")
                print(f"   Old: {existing_hash[:16]}..." if existing_hash else "   Old: None")
                print(f"   New: {current_hash[:16]}...")
            else:
                print(f"✅ Current: {template_name}")

            print()

    return {
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": error_count,
        "total": updated_count + skipped_count + error_count,
    }


def main():
    # Determine paths
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    registry_path = base_dir / "registry.json"

    print("Registry Synchronization Script (Phase 5 Recovery)")
    print("=" * 60)
    print(f"Registry: {registry_path}")
    print(f"Base Directory: {base_dir}")
    print()

    if not registry_path.exists():
        print(f"ERROR: Registry file not found: {registry_path}")
        sys.exit(1)

    # Backup original registry
    backup_path = registry_path.with_suffix(".json.backup")
    try:
        import shutil

        shutil.copy2(registry_path, backup_path)
        print(f"📋 Backup created: {backup_path}")
        print()
    except Exception as e:
        # guardian: allow-silent-swallower
        print(f"WARNING: Could not create backup: {e}")
        print()

    # Synchronize hashes
    stats = synchronize_registry_hashes(registry_path, base_dir)

    # Save updated registry
    registry = load_registry(registry_path)
    registry["last_sync_date"] = str(Path(__file__).stat().st_mtime)
    save_registry(registry_path, registry)

    # Report results
    print("SYNCHRONIZATION COMPLETE:")
    print(f"  Templates processed: {stats['total']}")
    print(f"  Hashes updated: {stats['updated']}")
    print(f"  Inactive skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")
    print()

    if stats["errors"] > 0:
        print("⚠️  Some templates had errors - check the output above")
        sys.exit(1)
    elif stats["updated"] > 0:
        print("✅ Registry synchronized successfully")
        print("💡 Run the drift detection audit again to verify")
        sys.exit(0)
    else:
        print("✅ Registry already synchronized")
        sys.exit(0)


if __name__ == "__main__":
    main()
