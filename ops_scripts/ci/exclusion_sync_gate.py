#!/usr/bin/env python3
"""CI Gate: Verify exclusion synchronization.

Ensures config/excluded_paths.yaml, SOVEREIGN_EXCLUDED_FOLDERS, and .gitignore
are all in sync. Fails the build if drift is detected.

Usage:
    python ops_scripts/ci/exclusion_sync_gate.py

Exit codes:
    0 - All exclusions in sync
    1 - Drift detected (CI failure)
    2 - Configuration error
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Set


def load_yaml_exclusions() -> Set[str]:
    """Load exclusions from YAML config."""
    config_path = Path(__file__).parent.parent.parent / "config" / "excluded_paths.yaml"
    
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required")
        sys.exit(2)
    
    if not config_path.exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(2)
    
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    all_dirs: Set[str] = set()
    categories = [
        "build_cache_dirs",
        "version_control_dirs",
        "virtual_env_dirs",
        "coverage_dirs",
        "archive_dirs",
        "ide_dirs",
        "vendor_dirs",
        "data_dirs",
        "special_dirs",
    ]
    
    for category in categories:
        dirs = data.get(category, [])
        if isinstance(dirs, list):
            all_dirs.update(dirs)
    
    return all_dirs


def load_ssot_exclusions() -> Set[str]:
    """Load SOVEREIGN_EXCLUDED_FOLDERS from ssot.py."""
    # Import the actual constant to ensure we're checking what's really used
    try:
        from agentic_core.L5_safety.config.structure_blueprint.ssot import (
            SOVEREIGN_EXCLUDED_FOLDERS,
        )
        return set(SOVEREIGN_EXCLUDED_FOLDERS)
    except ImportError as e:
        print(f"ERROR: Cannot import SOVEREIGN_EXCLUDED_FOLDERS: {e}")
        sys.exit(2)


def load_gitignore_entries() -> Set[str]:
    """Load directory entries from .gitignore."""
    gitignore_path = Path(__file__).parent.parent.parent / ".gitignore"
    
    if not gitignore_path.exists():
        print(f"ERROR: .gitignore not found: {gitignore_path}")
        sys.exit(2)
    
    entries: Set[str] = set()
    with open(gitignore_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Skip file patterns (contain * or don't look like directories)
            if "*" in line or "." in line and not line.startswith("."):
                continue
            # Extract directory name (remove leading / and trailing /)
            clean = line.strip("/")
            if clean and "/" not in clean:
                entries.add(clean)
    
    return entries


def main() -> int:
    print("=" * 60)
    print("Exclusion Synchronization Gate")
    print("=" * 60)
    
    # Load all three sources
    yaml_dirs = load_yaml_exclusions()
    ssot_dirs = load_ssot_exclusions()
    gitignore_dirs = load_gitignore_entries()
    
    print(f"\nLoaded:")
    print(f"  - YAML config: {len(yaml_dirs)} directories")
    print(f"  - ssot.py: {len(ssot_dirs)} directories")
    print(f"  - .gitignore: {len(gitignore_dirs)} directories")
    
    # Check YAML vs ssot
    yaml_not_ssot = yaml_dirs - ssot_dirs
    ssot_not_yaml = ssot_dirs - yaml_dirs
    
    # Check YAML vs gitignore (with tolerance for gitignore extras)
    yaml_not_gitignore = yaml_dirs - gitignore_dirs
    
    issues = []
    
    if yaml_not_ssot:
        issues.append(f"YAML entries missing from ssot.py ({len(yaml_not_ssot)}):")
        for d in sorted(yaml_not_ssot)[:10]:
            issues.append(f"    - {d}")
        if len(yaml_not_ssot) > 10:
            issues.append(f"    ... and {len(yaml_not_ssot) - 10} more")
    
    if ssot_not_yaml:
        issues.append(f"ssot.py entries not in YAML ({len(ssot_not_yaml)}) - legacy/intentional:")
        for d in sorted(ssot_not_yaml)[:5]:
            issues.append(f"    - {d}")
        if len(ssot_not_yaml) > 5:
            issues.append(f"    ... and {len(ssot_not_yaml) - 5} more")
    
    if yaml_not_gitignore:
        issues.append(f"YAML entries missing from .gitignore ({len(yaml_not_gitignore)}):")
        for d in sorted(yaml_not_gitignore)[:10]:
            issues.append(f"    - {d}")
        if len(yaml_not_gitignore) > 10:
            issues.append(f"    ... and {len(yaml_not_gitignore) - 10} more")
    
    print("\n" + "-" * 60)
    if issues:
        print("❌ SYNC ISSUES DETECTED")
        print("-" * 60)
        for issue in issues:
            print(issue)
        print("-" * 60)
        print("\nREMEDIATION:")
        if yaml_not_ssot:
            print("  1. Add missing entries to ssot.py SOVEREIGN_EXCLUDED_FOLDERS")
        if yaml_not_gitignore:
            print("  2. Run: python tools/generate_gitignore.py --write")
        print("=" * 60)
        return 1
    else:
        print("✅ ALL SOURCES IN SYNC")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
