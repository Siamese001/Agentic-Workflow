#!/usr/bin/env python3
"""
archive_phase3_legacy_agents.py - Phase 3 Manager & Enforcer Hard Migration

Archives 23 legacy Manager and Enforcer agents that have been consolidated into:
- UnifiedResourceManagerAgent
- UnifiedSecurityManagerAgent
- UnifiedCodeEnforcerAgent
- UnifiedStructureEnforcerAgent

Usage:
    python scripts/archive_phase3_legacy_agents.py --dry-run
    python scripts/archive_phase3_legacy_agents.py
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
ARCHIVE_DIR = PROJECT_ROOT / "archives" / "legacy_agents"

# Phase 3 legacy agents to archive
LEGACY_MANAGERS: List[str] = [
    # Resource Managers -> UnifiedResourceManagerAgent
    "BudgetManagerAgent.py",
    "ProactiveResourceManagerAgent.py",
    "FallbackManagerAgent.py",
    
    # Security Managers -> UnifiedSecurityManagerAgent
    "AgentPermissionManagerAgent.py",
    "SecureCheckpointManagerAgent.py",
    "SecureConfigManagerAgent.py",
    
    # Other Managers
    "McpConnectionManagerAgent.py",
    "FileManagerAgent.py",
    "FissionManagerAgent.py",
    "ValidationContextManagerAgent.py",
]

LEGACY_ENFORCERS: List[str] = [
    # Code Enforcers -> UnifiedCodeEnforcerAgent
    "CodeSSOTEnforcerAgent.py",
    "CodeStandardsEnforcerAgent.py",
    "PatternEnforcerAgent.py",
    "TypeEnforcerAgent.py",
    "PythonFileSovereigntyEnforcerAgent.py",
    
    # Structure Enforcers -> UnifiedStructureEnforcerAgent
    "GravityEnforcerAgent.py",
    "HierarchyEnforcerAgent.py",
    "NamingEnforcerAgent.py",
    "DocEnforcerAgent.py",
    "ASCIIEnforcerAgent.py",
    "StrictDocEnforcerAgent.py",
    
    # Additional enforcers
    "PascalSovereigntyEnforcerAgent.py",
]


def find_agent(filename: str) -> Path | None:
    """Find an agent file in the codebase."""
    # Search in agentic_core
    for path in (PROJECT_ROOT / "agentic_core").rglob(filename):
        path_str = str(path).lower()
        if "__pycache__" not in path_str and "archive" not in path_str and "unified" not in path_str:
            return path
    
    # Search in apps_lic
    for path in (PROJECT_ROOT / "apps_lic").rglob(filename):
        path_str = str(path).lower()
        if "__pycache__" not in path_str and "archive" not in path_str:
            return path
    
    return None


def archive_file(source: Path, category: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Archive a single file to category subfolder."""
    target_dir = ARCHIVE_DIR / category
    target = target_dir / source.name
    
    if target.exists():
        return False, "Already archived"
    
    if dry_run:
        return True, f"Would archive to {target.relative_to(PROJECT_ROOT)}"
    
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        return True, f"Archived to {target.relative_to(PROJECT_ROOT)}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description='Archive Phase 3 legacy agents')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()
    
    print("=" * 70)
    print("Phase 3 Hard Migration - Manager & Enforcer Archive")
    print("=" * 70)
    
    if args.dry_run:
        print("\n[DRY RUN MODE]\n")
    
    total_archived = 0
    total_skipped = 0
    total_not_found = 0
    
    print("\n--- Legacy Managers ---")
    for filename in LEGACY_MANAGERS:
        source = find_agent(filename)
        
        if source is None:
            print(f"  ⊘ NOT FOUND: {filename}")
            total_not_found += 1
            continue
        
        success, message = archive_file(source, "legacy_managers", args.dry_run)
        
        if success:
            icon = "○" if args.dry_run else "✓"
            print(f"  {icon} {filename}")
            total_archived += 1
        else:
            if "Already archived" in message:
                print(f"  ⊘ SKIP: {filename} ({message})")
                total_skipped += 1
            else:
                print(f"  ✗ ERROR: {filename} - {message}")
    
    print("\n--- Legacy Enforcers ---")
    for filename in LEGACY_ENFORCERS:
        source = find_agent(filename)
        
        if source is None:
            print(f"  ⊘ NOT FOUND: {filename}")
            total_not_found += 1
            continue
        
        success, message = archive_file(source, "legacy_enforcers", args.dry_run)
        
        if success:
            icon = "○" if args.dry_run else "✓"
            print(f"  {icon} {filename}")
            total_archived += 1
        else:
            if "Already archived" in message:
                print(f"  ⊘ SKIP: {filename} ({message})")
                total_skipped += 1
            else:
                print(f"  ✗ ERROR: {filename} - {message}")
    
    print(f"\n{'=' * 70}")
    print("Summary:")
    print(f"  Archived:  {total_archived}")
    print(f"  Skipped:   {total_skipped}")
    print(f"  Not Found: {total_not_found}")
    
    if args.dry_run:
        print("\n[DRY RUN COMPLETE]")
    else:
        print("\n✓ PHASE 3 LEGACY ARCHIVE COMPLETE")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
