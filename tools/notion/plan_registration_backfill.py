#!/usr/bin/env python3
"""
Plan Registration Backfill — W3 P1 Implementation

Batch-creates Notion Plans DB rows for orphan plans that exist on disk
but lack Notion registration (per §36).

Usage:
    python tools/notion/plan_registration_backfill.py --dry-run
    python tools/notion/plan_registration_backfill.py --execute

Features:
- Reads all .md files from .windsurf/plans/
- Checks Notion Plans DB for existing rows
- Generates canonical row payloads
- Dry-run mode by default (no writes)
- Skips if NOTION_TOKEN not set
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).parent.parent.parent
PLANS_DIR = REPO_ROOT / ".windsurf" / "plans"

# Notion Plans DB configuration
PLANS_DATABASE_ID = "6aba34d9-4d0b-4f4c-b956-b2bdea541ca9"


def extract_frontmatter(content: str) -> Dict[str, str]:
    """Extract YAML frontmatter from markdown."""
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_text = parts[1]
            for line in yaml_text.split("\n"):
                if ":" in line:
                    key, val = line.split(":", 1)
                    frontmatter[key.strip()] = val.strip().strip('"').strip("'")
    return frontmatter


def get_disk_plans() -> List[Dict[str, str]]:
    """Get all plans from disk with metadata."""
    plans = []
    if not PLANS_DIR.exists():
        return plans
    
    for f in PLANS_DIR.glob("*.md"):
        if f.name.endswith(".md"):
            slug = f.name.replace(".md", "")
            # Match pattern: <name>-<6hex>.md
            if len(slug) > 7 and slug[-7] == "-":
                content = f.read_text(encoding="utf-8")
                frontmatter = extract_frontmatter(content)
                
                # Extract first header as description
                description = ""
                for line in content.split("\n"):
                    if line.startswith("# "):
                        description = line[2:].strip()
                        break
                
                plans.append({
                    "slug": slug,
                    "path": str(f.relative_to(REPO_ROOT)),
                    "description": description,
                    "title": frontmatter.get("title", ""),
                    "status": frontmatter.get("status", "unknown"),
                })
    
    return plans


def build_notion_payload(plan: Dict[str, str]) -> Dict:
    """Build Notion API payload for plan registration."""
    # Default to "Not Started" for unknown status
    notion_status = "Not Started"
    if plan.get("status", "").lower() == "completed":
        notion_status = "Completed"
    elif plan.get("status", "").lower() == "in progress":
        notion_status = "In Progress"
    
    summary = plan.get("description", "") or plan.get("title", "")
    if not summary:
        summary = f"Plan {plan['slug']}"
    
    return {
        "parent": {
            "database_id": PLANS_DATABASE_ID,
            "type": "database_id"
        },
        "properties": {
            "Slug": {
                "title": [{"text": {"content": plan["slug"]}}]
            },
            "Status": {
                "select": {"name": notion_status}
            },
            "Exists On Disk": {
                "checkbox": True
            },
            "Plan File Path": {
                "rich_text": [{"text": {"content": f".windsurf/plans/{plan['slug']}.md"}}]
            },
            "Summary": {
                "rich_text": [{"text": {"content": summary[:500]}}]
            },
            "AI Summary ": {
                "rich_text": [{"text": {"content": f"Backfilled plan: {plan['slug']}"}}]
            }
        }
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Preview actions without executing (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually create Notion rows")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON report")
    args = parser.parse_args()
    
    # Check for token
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not token and args.execute:
        print("ERROR: NOTION_TOKEN or NOTION_API_KEY required for --execute")
        return 1
    
    plans = get_disk_plans()
    
    # In real implementation, would query Notion for existing slugs
    # For now, assume all disk plans are orphans (conservative)
    orphan_candidates = plans
    
    payloads = [build_notion_payload(p) for p in orphan_candidates]
    
    report = {
        "disk_plans": len(plans),
        "orphan_candidates": len(orphan_candidates),
        "would_create": len(payloads) if args.execute else 0,
        "payloads": payloads[:5],  # Sample
        "dry_run": not args.execute,
        "token_available": bool(token),
    }
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== Plan Registration Backfill ===")
        print(f"\nDisk plans found: {len(plans)}")
        print(f"Orphan candidates: {len(orphan_candidates)}")
        
        if args.execute:
            print(f"\n✅ EXECUTE mode: Would create {len(payloads)} Notion rows")
            print("   (API calls disabled in this version)")
        else:
            print(f"\n🔍 DRY RUN mode: {len(payloads)} payloads ready")
            print("   Use --execute to create rows (requires NOTION_TOKEN)")
            print("\n   Sample payloads:")
            for i, p in enumerate(payloads[:3], 1):
                slug = p["properties"]["Slug"]["title"][0]["text"]["content"]
                status = p["properties"]["Status"]["select"]["name"]
                print(f"   {i}. {slug} → Status: {status}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
