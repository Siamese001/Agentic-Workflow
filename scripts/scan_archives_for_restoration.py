#!/usr/bin/env python3
"""
scan_archives_for_restoration.py - Comprehensive archive scan for agent restoration

Scans entire archives/ folder to find agents that were incorrectly archived
and should be restored to the codebase.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVES = PROJECT_ROOT / "archives"
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"
APPS_DIRS = [PROJECT_ROOT / "apps_lic", PROJECT_ROOT / "apps_rg"]

# Folders that are legitimately archived (don't restore from these)
SKIP_FOLDERS = {
    "identity_duplicates",  # True duplicates - don't restore
    "consolidated_agents",  # Intentionally consolidated
    "deprecated_agents",    # Intentionally deprecated
    "tests",                # Test files
    "duplicate_tests_20260110_090742",
    "stubs",
    "examples_deprecated",
    "legacy_code",
    "deprecated_code",
    "logs",
    "resume_gen_json",
    "monolithic_configs_20260101",
    "core_contracts_monolithic_20260101",
    "canon_validator_deprecated_2025_12",
    "scripts_healing_20260110",
    "dedup_archived",
}


def get_current_agents() -> Set[str]:
    """Get all agent names currently in the codebase."""
    agents = set()
    
    for f in AGENTIC_CORE.rglob("*Agent.py"):
        agents.add(f.stem)
    
    for d in APPS_DIRS:
        if d.exists():
            for f in d.rglob("*Agent.py"):
                agents.add(f.stem)
    
    return agents


def scan_archives() -> Dict[str, Dict]:
    """Scan all archive folders for agent files."""
    current = get_current_agents()
    results = {}
    
    for subdir in ARCHIVES.iterdir():
        if not subdir.is_dir():
            continue
        
        folder_name = subdir.name
        agents = []
        
        for f in subdir.rglob("*Agent.py"):
            name = f.stem
            # Skip test files
            if name.startswith("Test") or name.startswith("test_"):
                continue
            
            is_unique = name not in current
            agents.append({
                "name": name,
                "path": str(f.relative_to(ARCHIVES)),
                "unique": is_unique,
            })
        
        if agents:
            unique_count = sum(1 for a in agents if a["unique"])
            results[folder_name] = {
                "total": len(agents),
                "unique": unique_count,
                "skip": folder_name in SKIP_FOLDERS,
                "agents": agents,
            }
    
    return results


def main():
    print("=" * 80)
    print("COMPREHENSIVE ARCHIVE SCAN FOR AGENT RESTORATION")
    print("=" * 80)
    
    current = get_current_agents()
    print(f"\nCurrent agents in codebase: {len(current)}")
    
    results = scan_archives()
    
    # Summary table
    print("\n" + "=" * 80)
    print("ARCHIVE SUMMARY")
    print("=" * 80)
    print(f"{'Folder':<40} {'Total':>6} {'Unique':>6} {'Action':<15}")
    print("-" * 80)
    
    total_unique = 0
    restore_candidates = []
    
    for folder in sorted(results.keys()):
        data = results[folder]
        if data["skip"]:
            action = "SKIP"
        elif data["unique"] > 0:
            action = "REVIEW"
            total_unique += data["unique"]
            restore_candidates.append(folder)
        else:
            action = "skip (dups)"
        
        print(f"{folder:<40} {data['total']:>6} {data['unique']:>6} {action:<15}")
    
    # Detailed unique agents
    print("\n" + "=" * 80)
    print(f"UNIQUE AGENTS TO RESTORE ({total_unique} total)")
    print("=" * 80)
    
    all_unique = []
    
    for folder in restore_candidates:
        data = results[folder]
        unique_agents = [a for a in data["agents"] if a["unique"]]
        
        if unique_agents:
            print(f"\n## {folder}/ ({len(unique_agents)} unique)")
            for agent in sorted(unique_agents, key=lambda x: x["name"])[:15]:
                print(f"   - {agent['name']}")
                all_unique.append({
                    "name": agent["name"],
                    "source": agent["path"],
                    "folder": folder,
                })
            if len(unique_agents) > 15:
                print(f"   ... and {len(unique_agents) - 15} more")
    
    # Save restoration manifest
    manifest = {
        "current_count": len(current),
        "unique_to_restore": total_unique,
        "by_folder": {
            folder: {
                "count": results[folder]["unique"],
                "agents": [a for a in results[folder]["agents"] if a["unique"]]
            }
            for folder in restore_candidates
        }
    }
    
    manifest_path = PROJECT_ROOT / "archives_restoration_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n\nSaved manifest to: {manifest_path}")
    print(f"\nTotal unique agents to review: {total_unique}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
