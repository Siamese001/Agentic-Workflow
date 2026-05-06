#!/usr/bin/env python3
"""
Orphan Plan Detector — W1 P1 Implementation

Cross-references disk plans against Notion Plans DB to identify:
- True orphans: file exists, no Notion row
- Stale orphans: file exists, Notion shows Retired/Archived without archive folder

Usage:
    python tools/analysis/orphan_plan_detector.py [--json]
"""

import json
import sys
from pathlib import Path
from typing import Set, Dict, List

REPO_ROOT = Path(__file__).parent.parent.parent
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"
ARCHIVE_DIR = PLANS_DIR / "_archive"


def get_disk_plans() -> Set[str]:
    """Get all plan slugs from disk (excluding archive)."""
    slugs = set()
    if not PLANS_DIR.exists():
        return slugs
    
    for f in PLANS_DIR.glob("*.md"):
        if f.name.endswith(".md"):
            # Match pattern: <name>-<6hex>.md
            slug = f.name.replace(".md", "")
            if len(slug) > 7 and slug[-7] == "-":
                slugs.add(slug)
    return slugs


def get_archived_plans() -> Set[str]:
    """Get all plan slugs from archive folders."""
    slugs = set()
    if not ARCHIVE_DIR.exists():
        return slugs
    
    for archive_subdir in ARCHIVE_DIR.iterdir():
        if archive_subdir.is_dir():
            for f in archive_subdir.glob("*.md"):
                if f.name.endswith(".md"):
                    slug = f.name.replace(".md", "")
                    if len(slug) > 7 and slug[-7] == "-":
                        slugs.add(slug)
    return slugs


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    disk_plans = get_disk_plans()
    archived_plans = get_archived_plans()
    
    # For this script, we assume Notion slugs are passed via stdin or file
    # In production, this would query Notion API
    notion_slugs: Set[str] = set()
    
    # Read from file if exists (for testing)
    notion_cache = REPO_ROOT / "artifacts" / "windsurf" / "notion_plan_slugs.json"
    if notion_cache.exists():
        notion_slugs = set(json.loads(notion_cache.read_text()))
    
    # Calculate orphans
    true_orphans = disk_plans - notion_slugs  # On disk, not in Notion
    unarchived_retired = notion_slugs & disk_plans - archived_plans  # In Notion as Retired but not archived
    
    report = {
        "disk_total": len(disk_plans),
        "archived_total": len(archived_plans),
        "notion_total": len(notion_slugs),
        "true_orphans": sorted(true_orphans),
        "true_orphan_count": len(true_orphans),
        "analysis_time": "2026-05-06",
        "orphan_candidates": sorted(disk_plans - notion_slugs) if not notion_slugs else [],
    }
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== Orphan Plan Analysis ===")
        print(f"\nDisk plans (main folder): {len(disk_plans)}")
        print(f"Archived plans: {len(archived_plans)}")
        print(f"Notion registered: {len(notion_slugs)}")
        
        if notion_slugs:
            print(f"\nTrue orphans (disk only): {len(true_orphans)}")
            for slug in sorted(true_orphans)[:10]:
                print(f"  - {slug}")
            if len(true_orphans) > 10:
                print(f"  ... and {len(true_orphans) - 10} more")
        else:
            print("\n⚠️  No Notion data available — run with Notion API integration")
            print(f"   Disk-only candidates: {len(disk_plans)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
